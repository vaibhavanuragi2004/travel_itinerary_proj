import json
import os
from datetime import datetime
from groq import Groq
from weather_service import WeatherService
from budget_optimizer import BudgetOptimizer

# Using Groq for chatbot functionality
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
groq_client = None

if GROQ_API_KEY:
    try:
        groq_client = Groq(api_key=GROQ_API_KEY)
        print("Chatbot Groq client initialized successfully")
    except Exception as e:
        print(f"Error initializing Groq client for chatbot: {e}")

class TravelChatbot:
    def __init__(self):
        self.weather_service = WeatherService()
        self.budget_optimizer = BudgetOptimizer()
        self.conversation_history = []
        
    def get_context_from_itinerary(self, itinerary_data):
        """Extract relevant context from user's itinerary"""
        if not itinerary_data:
            return ""
        
        try:
            data = json.loads(itinerary_data) if isinstance(itinerary_data, str) else itinerary_data
            context = f"""
            User's Current Trip Context:
            - Destination: {data.get('destination', 'Unknown')}
            - Duration: {data.get('duration', 'Unknown')} days
            - Total Budget: ₹{data.get('total_estimated_cost', 'Unknown')}
            - Current Activities: {len(data.get('days', []))} days planned
            """
            return context
        except:
            return ""
    
    def generate_response(self, user_message, itinerary_context=None, user_preferences=None):
        """Generate chatbot response using AI"""
        if not groq_client:
            return self.get_fallback_response(user_message)
        
        try:
            # Build context
            context = "You are a helpful Indian travel companion chatbot. You provide practical, culturally-aware travel advice for Indian tourists."
            
            if itinerary_context:
                context += self.get_context_from_itinerary(itinerary_context)
            
            if user_preferences:
                context += f"\nUser Interests: {', '.join(user_preferences)}"
            
            # Add conversation history
            conversation_context = ""
            if self.conversation_history:
                recent_history = self.conversation_history[-4:]  # Last 4 exchanges
                for entry in recent_history:
                    conversation_context += f"User: {entry.get('user', '')}\nBot: {entry.get('bot', '')}\n"
            
            prompt = f"""
{context}

Previous conversation:
{conversation_context}

Current user question: {user_message}

Provide a helpful, practical response. Keep it conversational but informative. If the question is about:
- Weather: Use current conditions and practical advice
- Budget: Give cost-effective suggestions 
- Activities: Suggest culturally relevant experiences
- Food: Recommend authentic local cuisine
- Transport: Provide practical travel tips for India
- Safety: Give responsible travel advice

Respond in a friendly, knowledgeable tone. Keep responses under 200 words unless detailed explanation is needed.
"""

            completion = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a helpful Indian travel companion chatbot."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            response = completion.choices[0].message.content.strip()
            
            # Store in conversation history
            self.conversation_history.append({
                'user': user_message,
                'bot': response,
                'timestamp': datetime.now().isoformat()
            })
            
            # Keep only recent history
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            return response
            
        except Exception as e:
            print(f"Error generating chatbot response: {e}")
            return self.get_fallback_response(user_message)
    
    def get_fallback_response(self, user_message):
        """Provide rule-based responses when AI is unavailable"""
        message_lower = user_message.lower()
        
        # Weather queries
        if any(word in message_lower for word in ['weather', 'rain', 'temperature', 'climate']):
            return "I can help you check current weather conditions for your destination. Please specify which city you'd like weather information for."
        
        # Budget queries
        elif any(word in message_lower for word in ['budget', 'cost', 'expensive', 'cheap', 'money']):
            return "For budget planning, I can help you optimize costs based on your destination and travel style. What specific budget questions do you have?"
        
        # Food queries
        elif any(word in message_lower for word in ['food', 'restaurant', 'eat', 'cuisine', 'local']):
            return "I'd love to help you discover authentic local cuisine! Which destination are you asking about? I can suggest traditional dishes and good restaurants."
        
        # Transport queries
        elif any(word in message_lower for word in ['transport', 'travel', 'bus', 'train', 'flight', 'taxi']):
            return "For transportation advice, I can help you choose the best travel options. Are you asking about getting to your destination or local transport?"
        
        # Activities queries
        elif any(word in message_lower for word in ['activity', 'things to do', 'attractions', 'sightseeing']):
            return "I can suggest activities based on your interests! What type of experiences are you looking for - adventure, cultural, nature, or something else?"
        
        # Greetings
        elif any(word in message_lower for word in ['hello', 'hi', 'help', 'start']):
            return "Hello! I'm your travel companion. I can help you with weather updates, budget tips, local recommendations, and answer any travel questions about your trip. What would you like to know?"
        
        else:
            return "I'm here to help with your travel questions! I can assist with weather, budget planning, local recommendations, activities, food suggestions, and transportation advice. What would you like to know about your trip?"
    
    def get_contextual_suggestions(self, destination, interests=None):
        """Generate proactive travel suggestions"""
        try:
            # Get weather context
            weather_data = self.weather_service.get_current_weather(destination)
            weather_context = ""
            if weather_data:
                temp = weather_data['main']['temp']
                condition = weather_data['weather'][0]['description']
                weather_context = f"Current weather in {destination}: {temp}°C, {condition}. "
            
            suggestions = []
            
            # Weather-based suggestions
            if weather_data:
                if temp > 35:
                    suggestions.append("🌡️ It's quite hot! Consider indoor activities during midday and carry plenty of water.")
                elif temp < 10:
                    suggestions.append("🧥 Pack warm clothes! Perfect weather for hot drinks and cozy indoor experiences.")
                elif 'rain' in condition.lower():
                    suggestions.append("☔ Pack an umbrella and consider indoor attractions today.")
            
            # Interest-based suggestions
            if interests:
                if 'Adventure' in interests:
                    suggestions.append("🏔️ Don't forget to check equipment rentals and book adventure activities in advance!")
                if 'Food' in interests:
                    suggestions.append("🍽️ Try booking food tours early - they fill up quickly in popular destinations!")
                if 'Cultural' in interests:
                    suggestions.append("🏛️ Many historical sites offer early morning visits with fewer crowds.")
            
            # Generic helpful tips
            suggestions.append("💡 Tip: Download offline maps and keep emergency contacts handy.")
            
            return {
                'weather_context': weather_context,
                'suggestions': suggestions[:3]  # Limit to 3 suggestions
            }
            
        except Exception as e:
            print(f"Error generating contextual suggestions: {e}")
            return {
                'weather_context': "",
                'suggestions': ["I'm here to help with any travel questions you have!"]
            }
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []