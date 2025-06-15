import json
import os
from groq import Groq

# Using Groq for open source LLM models
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
groq_client = None

if GROQ_API_KEY:
    try:
        groq_client = Groq(api_key=GROQ_API_KEY)
        print(f"GROQ client initialized successfully with key length: {len(GROQ_API_KEY)}")
    except Exception as e:
        print(f"Failed to initialize GROQ client: {e}")
        groq_client = None
else:
    print("Warning: GROQ_API_KEY not found. AI features will be disabled.")

def generate_basic_itinerary(destination, duration, budget, interests):
    """
    Generate a basic itinerary template when AI is not available
    """
    interests_str = ", ".join(interests) if interests else "sightseeing"
    daily_budget = budget / duration if duration > 0 else 0
    
    activities_template = [
        {"time": "09:00", "location": f"{destination} - Morning Attraction", "description": f"Visit popular morning attractions in {destination}", "cost": daily_budget * 0.3},
        {"time": "12:00", "location": f"{destination} - Local Restaurant", "description": "Lunch at local restaurant", "cost": daily_budget * 0.2},
        {"time": "14:00", "location": f"{destination} - Main Attraction", "description": f"Explore main attractions related to {interests_str}", "cost": daily_budget * 0.3},
        {"time": "17:00", "location": f"{destination} - Evening Spot", "description": "Evening leisure activities", "cost": daily_budget * 0.2}
    ]
    
    days = []
    for day in range(1, duration + 1):
        day_activities = [
            {
                "time": activity["time"],
                "location": activity["location"].replace("Morning", f"Day {day} Morning").replace("Main", f"Day {day} Main"),
                "description": activity["description"],
                "cost": activity["cost"]
            }
            for activity in activities_template
        ]
        
        days.append({
            "day": day,
            "theme": f"Day {day} - Exploring {destination}",
            "activities": day_activities
        })
    
    return {
        "destination": destination,
        "duration": duration,
        "total_estimated_cost": budget,
        "overview": f"A {duration}-day basic itinerary for {destination} focusing on {interests_str}. Add your API key for personalized AI-generated itineraries.",
        "days": days
    }

def generate_travel_itinerary(destination, duration, budget, interests):
    """
    Generate a detailed travel itinerary using AI for Indian tourists
    """
    if not groq_client:
        print("Groq API key not configured. Using basic itinerary template.")
        return generate_basic_itinerary(destination, duration, budget, interests)
        
    try:
        interests_str = ", ".join(interests) if interests else "general sightseeing"
        
        prompt = f"""Create a detailed {duration}-day travel itinerary for Indian tourists visiting {destination} with a budget of ₹{budget}. The traveler is interested in: {interests_str}.

CRITICAL PLANNING RULES:
1. Plan activities in GEOGRAPHICAL SEQUENCE - group nearby attractions together on the same day
2. Minimize travel time between locations - visit places in logical proximity order
3. Consider traffic patterns and peak hours for major cities
4. Start each day from accommodation and plan a circular/efficient route
5. Include specific landmark names, addresses, opening/closing hours, and realistic travel times between locations
6. Factor in meal breaks at restaurants near the current location cluster
7. End each day at a location convenient for returning to accommodation

IMPORTANT: Respond ONLY with valid JSON. No additional text before or after the JSON.

Required JSON structure:
{{
  "destination": "{destination}",
  "duration": {duration},
  "total_estimated_cost": 25000,
  "overview": "Brief description of the trip focusing on geographical efficiency",
  "days": [
    {{
      "day": 1,
      "theme": "Day theme/focus area",
      "geographical_zone": "Specific area/district being explored",
      "activities": [
        {{
          "time": "09:00",
          "location": "Specific landmark/attraction name with area",
          "description": "Detailed activity description with duration",
          "cost": 500,
          "opening_hours": "9:00 AM - 6:00 PM",
          "travel_time_to_next": "15 minutes",
          "transportation_mode": "walking/taxi/metro",
          "tips": "Practical tips for Indian tourists"
        }}
      ]
    }}
  ],
  "travel_tips": [
    "Location-specific tips including best travel routes and timing advice"
  ],
  "budget_breakdown": {{
    "accommodation": 10000,
    "food": 5000,
    "local_transportation": 3000,
    "activities": 5000,
    "shopping": 2000
  }}
}}

Plan each day to cover one geographical area/zone efficiently. Ensure realistic travel times and costs within the specified budget."""

        print(f"Making GROQ API call for {destination}, {duration} days, budget ₹{budget}")
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert travel planner specializing in geographically efficient itineraries for Indian tourists. Your priority is creating routes that minimize travel time by grouping nearby attractions together. Plan each day around a specific geographical zone or district. Consider local transportation, traffic patterns, and walking distances. Include specific landmark names, realistic travel times, and practical routing advice. Always respond with valid JSON only."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000,
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        if not content:
            print("Empty response from Groq API")
            return generate_basic_itinerary(destination, duration, budget, interests)
        
        # Clean the content to extract valid JSON
        try:
            # Find JSON block within the response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_content = content[start_idx:end_idx]
                result = json.loads(json_content)
            else:
                # If no JSON found, parse the entire content
                result = json.loads(content)
            
            # Validate the response structure
            if not all(key in result for key in ['destination', 'duration', 'days']):
                print("Invalid response structure, using fallback")
                return generate_basic_itinerary(destination, duration, budget, interests)
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Response content preview: {content[:500]}...")
            return generate_basic_itinerary(destination, duration, budget, interests)
        
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return generate_basic_itinerary(destination, duration, budget, interests)
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
            model="llama-3.1-8b-instant",
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
