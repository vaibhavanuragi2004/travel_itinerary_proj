import json
import os
from groq import Groq

# Using Groq for open source LLM models
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
groq_client = None

if GROQ_API_KEY:
    groq_client = Groq(api_key=GROQ_API_KEY)
else:
    print("Warning: GROQ_API_KEY not found. AI features will be disabled.")

def generate_travel_itinerary(destination, duration, budget, interests):
    """
    Generate a detailed travel itinerary using AI for Indian tourists
    """
    if not groq_client:
        print("Groq API key not configured. Cannot generate AI itinerary.")
        return None
        
    try:
        interests_str = ", ".join(interests) if interests else "general sightseeing"
        
        prompt = f"""Create a detailed {duration}-day travel itinerary for Indian tourists visiting {destination} with a budget of ₹{budget}. The traveler is interested in: {interests_str}.

Please provide a comprehensive itinerary with the following structure:
- Daily breakdown with specific activities
- Recommended timings for each activity
- Estimated costs in Indian Rupees
- Popular landmarks and attractions suitable for Indian tourists
- Local transportation suggestions
- Food recommendations (vegetarian options when possible)
- Cultural considerations and tips

You must respond with valid JSON in this exact structure:
{{
  "destination": "{destination}",
  "duration": {duration},
  "total_estimated_cost": 25000,
  "overview": "Brief description of the trip",
  "days": [
    {{
      "day": 1,
      "theme": "Day theme/focus",
      "activities": [
        {{
          "time": "09:00",
          "location": "Specific location name",
          "description": "Detailed activity description",
          "cost": 500,
          "duration": "2 hours",
          "tips": "Helpful tips for Indian tourists"
        }}
      ]
    }}
  ],
  "travel_tips": [
    "Important travel tips for Indian tourists"
  ],
  "budget_breakdown": {{
    "accommodation": 10000,
    "food": 5000,
    "transportation": 3000,
    "activities": 5000,
    "shopping": 2000
  }}
}}

Ensure all costs are realistic and within the specified budget. Include specific landmark names and practical advice for Indian travelers."""

        response = groq_client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert travel planner specializing in creating detailed, culturally-aware itineraries for Indian tourists. Provide practical, budget-conscious recommendations with specific details. Always respond with valid JSON only."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000,
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        if not content:
            print("Empty response from Groq API")
            return None
            
        result = json.loads(content)
        
        # Validate the response structure
        if not all(key in result for key in ['destination', 'duration', 'days']):
            raise ValueError("Invalid response structure from AI service")
        
        return result
        
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        print(f"Response content: {content if 'content' in locals() else 'No content'}")
        return None
    except Exception as e:
        print(f"Error generating itinerary: {e}")
        return None

def get_location_suggestions(query):
    """
    Get location suggestions based on user input
    """
    if not groq_client:
        print("Groq API key not configured. Cannot get location suggestions.")
        return {"suggestions": []}
        
    try:
        prompt = f"""Suggest 5 popular travel destinations in India that match the query: "{query}"

Respond with valid JSON in this exact format:
{{
  "suggestions": [
    {{
      "name": "Destination name",
      "state": "State name", 
      "description": "Brief description",
      "best_time": "Best time to visit"
    }}
  ]
}}"""
        
        response = groq_client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a travel expert for Indian destinations. Always respond with valid JSON only."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        if not content:
            return {"suggestions": []}
            
        return json.loads(content)
        
    except Exception as e:
        print(f"Error getting location suggestions: {e}")
        return {"suggestions": []}
