import json
from datetime import datetime
from typing import Dict, List, Tuple

class BudgetOptimizer:
    """
    Dynamic budget allocation based on destination, interests, duration, and season
    """
    
    def __init__(self):
        # Base cost multipliers by destination type
        self.destination_profiles = {
            'metro_cities': {
                'cities': ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Hyderabad', 'Pune'],
                'accommodation_multiplier': 1.5,
                'food_multiplier': 1.3,
                'transport_multiplier': 1.2,
                'activities_multiplier': 1.4
            },
            'hill_stations': {
                'cities': ['Shimla', 'Manali', 'Mussoorie', 'Darjeeling', 'Ooty'],
                'accommodation_multiplier': 1.3,
                'food_multiplier': 1.1,
                'transport_multiplier': 1.5,  # Higher due to terrain
                'activities_multiplier': 1.2
            },
            'coastal': {
                'cities': ['Goa', 'Kerala', 'Pondicherry', 'Andaman'],
                'accommodation_multiplier': 1.4,
                'food_multiplier': 1.0,
                'transport_multiplier': 0.9,
                'activities_multiplier': 1.3
            },
            'heritage': {
                'cities': ['Rajasthan', 'Agra', 'Varanasi', 'Hampi', 'Khajuraho'],
                'accommodation_multiplier': 1.2,
                'food_multiplier': 0.9,
                'transport_multiplier': 1.1,
                'activities_multiplier': 1.1
            },
            'tier2_cities': {
                'cities': ['Jaipur', 'Ahmedabad', 'Kochi', 'Mysore', 'Udaipur'],
                'accommodation_multiplier': 1.0,
                'food_multiplier': 0.8,
                'transport_multiplier': 0.9,
                'activities_multiplier': 0.9
            }
        }
        
        # Interest-based budget allocation preferences
        self.interest_allocations = {
            'Adventure': {
                'accommodation': 0.25,  # Lower - camping/budget stays
                'food': 0.25,
                'transport': 0.20,
                'activities': 0.25,    # Higher - equipment, guides
                'shopping': 0.05
            },
            'Luxury': {
                'accommodation': 0.50,  # Higher - premium hotels
                'food': 0.25,
                'transport': 0.10,     # Lower - included in packages
                'activities': 0.10,
                'shopping': 0.05
            },
            'Cultural': {
                'accommodation': 0.35,
                'food': 0.20,
                'transport': 0.15,
                'activities': 0.20,    # Museums, guides, experiences
                'shopping': 0.10       # Handicrafts, souvenirs
            },
            'Food': {
                'accommodation': 0.30,
                'food': 0.35,          # Higher - food tours, restaurants
                'transport': 0.15,
                'activities': 0.15,
                'shopping': 0.05
            },
            'Nature': {
                'accommodation': 0.30,
                'food': 0.20,
                'transport': 0.20,     # Park entries, safari vehicles
                'activities': 0.25,    # Safari, trekking, guides
                'shopping': 0.05
            },
            'Spiritual': {
                'accommodation': 0.25,  # Ashrams, budget accommodations
                'food': 0.15,          # Simple vegetarian meals
                'transport': 0.20,
                'activities': 0.30,    # Ceremonies, donations, guides
                'shopping': 0.10       # Religious items
            },
            'Beach': {
                'accommodation': 0.40,  # Beach resorts
                'food': 0.25,
                'transport': 0.10,
                'activities': 0.20,    # Water sports, boat rides
                'shopping': 0.05
            }
        }
        
        # Seasonal multipliers (peak season = higher costs)
        self.seasonal_multipliers = {
            'peak': 1.4,     # Dec-Jan, Apr-May for hills
            'high': 1.2,     # Oct-Nov, Feb-Mar
            'medium': 1.0,   # Sep, Jun
            'low': 0.8       # Jul-Aug (monsoon)
        }
        
        # Duration-based efficiency factors
        self.duration_factors = {
            'accommodation': {
                'short': 1.2,    # 1-3 days - less negotiation power
                'medium': 1.0,   # 4-7 days
                'long': 0.9      # 8+ days - bulk discounts
            },
            'transport': {
                'short': 1.3,    # Higher per-day transport costs
                'medium': 1.0,
                'long': 0.8      # Economy of scale
            }
        }

    def get_destination_type(self, destination: str) -> str:
        """Classify destination type based on name"""
        destination_lower = destination.lower()
        
        for dest_type, data in self.destination_profiles.items():
            for city in data['cities']:
                if city.lower() in destination_lower:
                    return dest_type
        
        # Default classification
        return 'tier2_cities'

    def get_season(self, travel_date: datetime = None) -> str:
        """Determine season based on travel date"""
        if not travel_date:
            travel_date = datetime.now()
        
        month = travel_date.month
        
        if month in [12, 1, 4, 5]:  # Winter + Pre-summer
            return 'peak'
        elif month in [10, 11, 2, 3]:  # Post-monsoon + Spring
            return 'high'
        elif month in [9, 6]:  # Post-monsoon start + Summer start
            return 'medium'
        else:  # Monsoon months
            return 'low'

    def get_duration_category(self, duration: int) -> str:
        """Categorize trip duration"""
        if duration <= 3:
            return 'short'
        elif duration <= 7:
            return 'medium'
        else:
            return 'long'

    def calculate_optimized_budget(self, 
                                 destination: str, 
                                 duration: int, 
                                 total_budget: float, 
                                 interests: List[str],
                                 travel_date: datetime = None) -> Dict[str, float]:
        """
        Calculate optimized budget breakdown based on multiple factors
        """
        
        # Get base allocation from primary interest
        primary_interest = interests[0] if interests else 'Cultural'
        base_allocation = self.interest_allocations.get(primary_interest, 
                                                       self.interest_allocations['Cultural'])
        
        # Get destination profile
        dest_type = self.get_destination_type(destination)
        dest_profile = self.destination_profiles[dest_type]
        
        # Get seasonal and duration factors
        season = self.get_season(travel_date)
        seasonal_multiplier = self.seasonal_multipliers[season]
        duration_category = self.get_duration_category(duration)
        
        # Calculate adjusted allocations
        adjusted_budget = {}
        
        for category, base_percent in base_allocation.items():
            # Apply destination-specific multipliers
            if category in dest_profile:
                multiplier = dest_profile[f'{category}_multiplier']
            else:
                multiplier = 1.0
            
            # Apply seasonal adjustments (mainly affects accommodation and activities)
            if category in ['accommodation', 'activities']:
                multiplier *= seasonal_multiplier
            
            # Apply duration factors
            if category in self.duration_factors:
                duration_factor = self.duration_factors[category][duration_category]
                multiplier *= duration_factor
            
            adjusted_percent = base_percent * multiplier
            adjusted_budget[category] = adjusted_percent
        
        # Normalize to ensure total = 100%
        total_percent = sum(adjusted_budget.values())
        normalized_budget = {k: (v / total_percent) for k, v in adjusted_budget.items()}
        
        # Convert to actual amounts
        final_budget = {k: round(v * total_budget) for k, v in normalized_budget.items()}
        
        # Add metadata for transparency
        final_budget['_metadata'] = {
            'destination_type': dest_type,
            'season': season,
            'duration_category': duration_category,
            'seasonal_multiplier': seasonal_multiplier,
            'primary_interest': primary_interest
        }
        
        return final_budget

    def get_budget_recommendations(self, 
                                 destination: str, 
                                 duration: int, 
                                 total_budget: float,
                                 interests: List[str]) -> Dict:
        """
        Get budget breakdown with recommendations and warnings
        """
        
        optimized = self.calculate_optimized_budget(destination, duration, total_budget, interests)
        metadata = optimized.pop('_metadata')
        
        # Calculate per-day costs
        per_day_costs = {k: round(v / duration) for k, v in optimized.items()}
        
        # Generate recommendations
        recommendations = []
        warnings = []
        
        # Budget adequacy checks
        min_daily_budget = {
            'metro_cities': 3000,
            'hill_stations': 2500,
            'coastal': 2800,
            'heritage': 2000,
            'tier2_cities': 1800
        }
        
        daily_budget = total_budget / duration
        min_required = min_daily_budget.get(metadata['destination_type'], 2000)
        
        if daily_budget < min_required:
            warnings.append(f"Budget might be tight for {destination}. Recommended minimum: ₹{min_required * duration:,.0f}")
        
        # Seasonal recommendations
        if metadata['season'] == 'peak':
            recommendations.append("Peak season - book accommodations early for better rates")
        elif metadata['season'] == 'low':
            recommendations.append("Monsoon season - budget extra for indoor activities and transport delays")
        
        # Interest-specific tips
        if 'Adventure' in interests:
            recommendations.append("Consider equipment rental vs purchase for cost efficiency")
        if 'Food' in interests:
            recommendations.append("Allocate extra budget for food tours and fine dining experiences")
        
        return {
            'budget_breakdown': optimized,
            'per_day_costs': per_day_costs,
            'recommendations': recommendations,
            'warnings': warnings,
            'metadata': metadata
        }

# Usage example and testing
if __name__ == "__main__":
    optimizer = BudgetOptimizer()
    
    # Test case: Adventure trip to Manali
    result = optimizer.get_budget_recommendations(
        destination="Manali, Himachal Pradesh",
        duration=5,
        total_budget=50000,
        interests=["Adventure", "Nature"]
    )
    
    print(json.dumps(result, indent=2, default=str))