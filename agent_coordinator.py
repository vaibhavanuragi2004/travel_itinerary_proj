import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import asyncio
from dataclasses import dataclass

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.tools import Tool
from langchain_core.messages import HumanMessage, SystemMessage

from weather_service import WeatherService
from budget_optimizer import BudgetOptimizer

@dataclass
class AgentContext:
    """Shared context between agents"""
    user_id: Optional[int] = None
    itinerary_id: Optional[int] = None
    current_location: Optional[str] = None
    travel_date: Optional[datetime] = None
    budget_remaining: Optional[float] = None
    user_preferences: Dict[str, Any] = None
    
class TravelAgentCoordinator:
    """
    Multi-agent coordinator for proactive travel assistance
    Orchestrates specialized agents for different travel domains
    """
    
    def __init__(self):
        self.weather_service = WeatherService()
        self.budget_optimizer = BudgetOptimizer()
        
        # Initialize base LLM
        try:
            self.llm = ChatGroq(
                groq_api_key=os.environ.get("GROQ_API_KEY"),
                model_name="llama-3.1-8b-instant",
                temperature=0.3,  # Lower temperature for more consistent decisions
                max_tokens=1000
            )
        except Exception as e:
            logging.error(f"Failed to initialize LLM: {e}")
            self.llm = None
        
        # Agent memory for learning patterns
        self.agent_memory = {
            'successful_recommendations': [],
            'user_feedback_patterns': {},
            'weather_adaptations': [],
            'budget_optimizations': []
        }
    
    def create_weather_agent(self) -> Tool:
        """Weather monitoring and advisory agent"""
        def weather_analysis(query: str) -> str:
            try:
                # Parse location from query
                location = self._extract_location(query)
                if not location:
                    return "Location not specified for weather analysis"
                
                # Get current weather and forecast
                current = self.weather_service.get_current_weather(location)
                forecast = self.weather_service.get_forecast(location, days=3)
                
                if not current:
                    return f"Weather data unavailable for {location}"
                
                # Analyze conditions and generate proactive advice
                analysis = self._analyze_weather_conditions(current, forecast)
                
                return json.dumps({
                    'current_conditions': current,
                    'forecast_summary': forecast[:3] if forecast else [],
                    'travel_recommendations': analysis['recommendations'],
                    'alerts': analysis['alerts'],
                    'suggested_changes': analysis['changes']
                })
                
            except Exception as e:
                return f"Weather analysis failed: {str(e)}"
        
        return Tool(
            name="weather_agent",
            description="Monitors weather conditions and provides proactive travel advice",
            func=weather_analysis
        )
    
    def create_budget_agent(self) -> Tool:
        """Budget monitoring and optimization agent"""
        def budget_analysis(query: str) -> str:
            try:
                # Extract budget context from query
                context = self._extract_budget_context(query)
                
                # Analyze spending patterns and suggest optimizations
                recommendations = self.budget_optimizer.get_budget_recommendations(
                    context.get('destination', ''),
                    context.get('duration', 3),
                    context.get('budget', 25000),
                    context.get('interests', [])
                )
                
                # Add proactive cost-saving suggestions
                cost_saving_tips = self._generate_cost_saving_tips(context)
                
                return json.dumps({
                    'budget_analysis': recommendations,
                    'cost_saving_opportunities': cost_saving_tips,
                    'spending_alerts': self._check_budget_alerts(context),
                    'optimization_suggestions': self._suggest_budget_optimizations(context)
                })
                
            except Exception as e:
                return f"Budget analysis failed: {str(e)}"
        
        return Tool(
            name="budget_agent",
            description="Monitors budget and suggests cost optimizations",
            func=budget_analysis
        )
    
    def create_activity_agent(self) -> Tool:
        """Activity discovery and management agent"""
        def activity_recommendations(query: str) -> str:
            try:
                context = self._extract_activity_context(query)
                
                # Generate personalized activity suggestions
                activities = self._discover_activities(context)
                
                # Check for better alternatives or new experiences
                alternatives = self._find_activity_alternatives(context)
                
                return json.dumps({
                    'new_activities': activities,
                    'alternative_suggestions': alternatives,
                    'timing_optimizations': self._optimize_activity_timing(context),
                    'booking_opportunities': self._find_booking_deals(context)
                })
                
            except Exception as e:
                return f"Activity recommendations failed: {str(e)}"
        
        return Tool(
            name="activity_agent", 
            description="Discovers activities and optimizes travel experiences",
            func=activity_recommendations
        )
    
    async def proactive_monitoring(self, context: AgentContext) -> Dict[str, Any]:
        """
        Proactive monitoring that runs autonomously to detect:
        - Weather changes requiring itinerary adjustments
        - Budget optimization opportunities
        - New activity suggestions
        - Travel disruptions or improvements
        """
        monitoring_results = {
            'weather_alerts': [],
            'budget_insights': [],
            'activity_suggestions': [],
            'urgent_notifications': []
        }
        
        try:
            # Weather monitoring
            if context.current_location:
                weather_check = await self._check_weather_proactively(context)
                monitoring_results['weather_alerts'] = weather_check
            
            # Budget monitoring  
            if context.budget_remaining is not None:
                budget_check = await self._monitor_budget_proactively(context)
                monitoring_results['budget_insights'] = budget_check
            
            # Activity discovery
            activity_check = await self._discover_activities_proactively(context)
            monitoring_results['activity_suggestions'] = activity_check
            
            # Generate coordinated recommendations
            coordinated_advice = await self._coordinate_agent_recommendations(monitoring_results)
            monitoring_results['coordinated_recommendations'] = coordinated_advice
            
        except Exception as e:
            logging.error(f"Proactive monitoring failed: {e}")
            monitoring_results['errors'] = [str(e)]
        
        return monitoring_results
    
    def learn_from_interaction(self, interaction_data: Dict[str, Any]):
        """
        Learn from user interactions to improve future recommendations
        """
        try:
            # Store successful recommendations
            if interaction_data.get('feedback') == 'positive':
                self.agent_memory['successful_recommendations'].append({
                    'timestamp': datetime.now().isoformat(),
                    'recommendation_type': interaction_data.get('type'),
                    'context': interaction_data.get('context'),
                    'success_factors': interaction_data.get('success_factors', [])
                })
            
            # Update user preference patterns
            user_id = interaction_data.get('user_id')
            if user_id:
                if user_id not in self.agent_memory['user_feedback_patterns']:
                    self.agent_memory['user_feedback_patterns'][user_id] = []
                
                self.agent_memory['user_feedback_patterns'][user_id].append({
                    'timestamp': datetime.now().isoformat(),
                    'interaction': interaction_data
                })
            
            # Adapt agent behavior based on patterns
            self._adapt_agent_strategies()
            
        except Exception as e:
            logging.error(f"Learning from interaction failed: {e}")
    
    def _analyze_weather_conditions(self, current: Dict, forecast: List) -> Dict:
        """Analyze weather and generate proactive recommendations"""
        recommendations = []
        alerts = []
        changes = []
        
        # Check current conditions
        if current.get('main', {}).get('temp', 0) > 35:
            recommendations.append("High temperature detected. Consider indoor activities during midday.")
            changes.append("Suggest morning/evening outdoor activities")
        
        if current.get('weather', [{}])[0].get('main') == 'Rain':
            alerts.append("Rain detected. Indoor backup plans recommended.")
            changes.append("Move outdoor activities to covered venues")
        
        # Check forecast for planning
        if forecast:
            for day_forecast in forecast[:2]:
                if day_forecast.get('weather', [{}])[0].get('main') == 'Rain':
                    alerts.append(f"Rain expected. Plan indoor alternatives.")
        
        return {
            'recommendations': recommendations,
            'alerts': alerts,
            'changes': changes
        }
    
    def _extract_location(self, query: str) -> Optional[str]:
        """Extract location from query string"""
        # Simple extraction - could be enhanced with NLP
        words = query.lower().split()
        locations = ['mumbai', 'delhi', 'bangalore', 'goa', 'kerala', 'rajasthan']
        for word in words:
            if word in locations:
                return word.title()
        return None
    
    def _extract_budget_context(self, query: str) -> Dict:
        """Extract budget context from query"""
        return {
            'destination': self._extract_location(query) or '',
            'duration': 3,  # Default
            'budget': 25000,  # Default
            'interests': []
        }
    
    def _extract_activity_context(self, query: str) -> Dict:
        """Extract activity context from query"""
        return {
            'location': self._extract_location(query),
            'interests': [],
            'budget_range': 'medium',
            'time_of_day': 'any'
        }
    
    async def _check_weather_proactively(self, context: AgentContext) -> List[Dict]:
        """Proactive weather monitoring"""
        alerts = []
        if context.current_location:
            try:
                current = self.weather_service.get_current_weather(context.current_location)
                if current and current.get('main', {}).get('temp', 0) > 40:
                    alerts.append({
                        'type': 'extreme_heat',
                        'message': 'Extreme heat detected. Recommend indoor activities.',
                        'suggested_action': 'Reschedule outdoor activities to evening'
                    })
            except Exception as e:
                logging.error(f"Weather proactive check failed: {e}")
        return alerts
    
    async def _monitor_budget_proactively(self, context: AgentContext) -> List[Dict]:
        """Proactive budget monitoring"""
        insights = []
        if context.budget_remaining is not None and context.budget_remaining < 1000:
            insights.append({
                'type': 'low_budget',
                'message': 'Budget running low. Suggesting cost-effective alternatives.',
                'recommendations': ['Use public transport', 'Try local street food', 'Visit free attractions']
            })
        return insights
    
    async def _discover_activities_proactively(self, context: AgentContext) -> List[Dict]:
        """Proactive activity discovery"""
        suggestions = []
        if context.current_location:
            suggestions.append({
                'type': 'local_experience',
                'activity': f'Explore local markets in {context.current_location}',
                'estimated_cost': 500,
                'duration': '2 hours'
            })
        return suggestions
    
    async def _coordinate_agent_recommendations(self, monitoring_results: Dict) -> List[str]:
        """Coordinate recommendations from multiple agents"""
        coordinated = []
        
        # Combine weather and activity recommendations
        if monitoring_results.get('weather_alerts') and monitoring_results.get('activity_suggestions'):
            coordinated.append("Weather conditions suggest indoor activities. Here are some recommendations...")
        
        # Combine budget and activity recommendations  
        if monitoring_results.get('budget_insights'):
            coordinated.append("Budget optimization: Consider these cost-effective activities...")
        
        return coordinated
    
    def _generate_cost_saving_tips(self, context: Dict) -> List[str]:
        """Generate personalized cost-saving tips"""
        return [
            "Book accommodations in advance for better rates",
            "Use public transportation instead of private cabs",
            "Try local restaurants instead of hotel dining"
        ]
    
    def _check_budget_alerts(self, context: Dict) -> List[str]:
        """Check for budget-related alerts"""
        alerts = []
        budget = context.get('budget', 0)
        if budget < 15000:
            alerts.append("Budget is below recommended amount for destination")
        return alerts
    
    def _suggest_budget_optimizations(self, context: Dict) -> List[str]:
        """Suggest budget optimizations"""
        return [
            "Allocate more budget to experiences, less to accommodation",
            "Consider traveling in off-peak season for savings"
        ]
    
    def _discover_activities(self, context: Dict) -> List[Dict]:
        """Discover new activities based on context"""
        location = context.get('location', '')
        activities = []
        
        if 'mumbai' in location.lower():
            activities.append({
                'name': 'Marine Drive sunset walk',
                'cost': 0,
                'duration': '1 hour',
                'type': 'sightseeing'
            })
        
        return activities
    
    def _find_activity_alternatives(self, context: Dict) -> List[Dict]:
        """Find alternative activities"""
        return [
            {
                'original': 'Expensive restaurant',
                'alternative': 'Local food market',
                'cost_saving': 800
            }
        ]
    
    def _optimize_activity_timing(self, context: Dict) -> List[str]:
        """Optimize activity timing"""
        return [
            "Visit attractions early morning to avoid crowds",
            "Plan outdoor activities during cooler evening hours"
        ]
    
    def _find_booking_deals(self, context: Dict) -> List[Dict]:
        """Find booking deals and opportunities"""
        return [
            {
                'type': 'early_bird_discount',
                'description': 'Book museum tickets online for 20% discount',
                'savings': 200
            }
        ]
    
    def _adapt_agent_strategies(self):
        """Adapt agent strategies based on learned patterns"""
        # Analyze successful recommendation patterns
        successful = self.agent_memory['successful_recommendations']
        
        # Extract common success factors
        success_factors = {}
        for rec in successful[-10:]:  # Last 10 successful recommendations
            for factor in rec.get('success_factors', []):
                success_factors[factor] = success_factors.get(factor, 0) + 1
        
        # Adapt strategies based on patterns
        logging.info(f"Adapting strategies based on success factors: {success_factors}")