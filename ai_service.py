import json
import os
from openai import OpenAI

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai = OpenAI(api_key=OPENAI_API_KEY)

def generate_travel_itinerary(destination, duration, budget, interests):
    """
    Generate a detailed travel itinerary using AI for Indian tourists
    """
    try:
        interests_str = ", ".join(interests) if interests else "general sightseeing"
        
        prompt = f"""
        Create a detailed {duration}-day travel itinerary for Indian tourists visiting {destination} 
        with a budget of ₹{budget}. The traveler is interested in: {interests_str}.

        Please provide a comprehensive itinerary with the following structure:
        - Daily breakdown with specific activities
        - Recommended timings for each activity
        - Estimated costs in Indian Rupees
        - Popular landmarks and attractions suitable for Indian tourists
        - Local transportation suggestions
        - Food recommendations (vegetarian options when possible)
        - Cultural considerations and tips

        Format the response as JSON with this exact structure:
        {{
            "destination": "{destination}",
            "duration": {duration},
            "total_estimated_cost": <number>,
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
                            "cost": <estimated cost in rupees>,
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
                "accommodation": <amount>,
                "food": <amount>,
                "transportation": <amount>,
                "activities": <amount>,
                "shopping": <amount>
            }}
        }}

        Ensure all costs are realistic and within the specified budget. Include specific landmark names, 
        addresses where relevant, and practical advice for Indian travelers.
        """

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert travel planner specializing in creating detailed, "
                    + "culturally-aware itineraries for Indian tourists. Provide practical, "
                    + "budget-conscious recommendations with specific details."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=4000
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Validate the response structure
        if not all(key in result for key in ['destination', 'duration', 'days']):
            raise ValueError("Invalid response structure from AI service")
        
        return result
        
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return None
    except Exception as e:
        print(f"Error generating itinerary: {e}")
        return None

def get_location_suggestions(query):
    """
    Get location suggestions based on user input
    """
    try:
        prompt = f"""
        Suggest 5 popular travel destinations in India that match the query: "{query}"
        
        Respond with JSON in this format:
        {{
            "suggestions": [
                {{
                    "name": "Destination name",
                    "state": "State name", 
                    "description": "Brief description",
                    "best_time": "Best time to visit"
                }}
            ]
        }}
        """
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            max_tokens=1000
        )
        
        return json.loads(response.choices[0].message.content)
        
    except Exception as e:
        print(f"Error getting location suggestions: {e}")
        return {"suggestions": []}
