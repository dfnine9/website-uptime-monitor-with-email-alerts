```python
"""
Weather-Based Recommendation Engine

This module analyzes weather patterns and generates actionable suggestions including:
- Clothing recommendations based on temperature and conditions
- Outdoor activity suggestions considering weather factors
- Travel alerts for adverse conditions

The engine processes temperature, precipitation probability, and weather conditions
to provide personalized recommendations for daily planning.

Usage:
    python script.py

Dependencies:
    - httpx (for weather API requests)
    - anthropic (for enhanced recommendation generation)
    - Standard library modules
"""

import json
import sys
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import httpx
import asyncio
from datetime import datetime, timedelta

class WeatherCondition(Enum):
    CLEAR = "clear"
    PARTLY_CLOUDY = "partly_cloudy"
    CLOUDY = "cloudy"
    RAIN = "rain"
    HEAVY_RAIN = "heavy_rain"
    SNOW = "snow"
    THUNDERSTORM = "thunderstorm"
    FOG = "fog"
    WINDY = "windy"

@dataclass
class WeatherData:
    temperature: float
    feels_like: float
    humidity: int
    precipitation_prob: int
    wind_speed: float
    condition: WeatherCondition
    visibility: float = 10.0
    uv_index: int = 0

@dataclass
class Recommendation:
    category: str
    suggestion: str
    priority: str  # high, medium, low
    reasoning: str

class WeatherRecommendationEngine:
    def __init__(self):
        self.temperature_ranges = {
            "extreme_cold": (-float('inf'), -10),
            "very_cold": (-10, 0),
            "cold": (0, 10),
            "cool": (10, 18),
            "mild": (18, 25),
            "warm": (25, 30),
            "hot": (30, 35),
            "extreme_hot": (35, float('inf'))
        }
    
    def classify_temperature(self, temp: float) -> str:
        """Classify temperature into predefined ranges."""
        for range_name, (min_temp, max_temp) in self.temperature_ranges.items():
            if min_temp <= temp < max_temp:
                return range_name
        return "mild"
    
    def generate_clothing_recommendations(self, weather: WeatherData) -> List[Recommendation]:
        """Generate clothing recommendations based on weather conditions."""
        recommendations = []
        temp_class = self.classify_temperature(weather.temperature)
        
        # Base clothing recommendations by temperature
        clothing_map = {
            "extreme_cold": {
                "base": "Heavy winter coat, thermal underwear, wool sweater",
                "accessories": "Insulated boots, thick gloves, warm hat, scarf",
                "priority": "high"
            },
            "very_cold": {
                "base": "Winter jacket, warm layers, long pants",
                "accessories": "Warm boots, gloves, hat",
                "priority": "high"
            },
            "cold": {
                "base": "Jacket or coat, long sleeves, long pants",
                "accessories": "Closed shoes, light gloves",
                "priority": "medium"
            },
            "cool": {
                "base": "Light jacket or sweater, long pants or jeans",
                "accessories": "Comfortable shoes, optional light scarf",
                "priority": "medium"
            },
            "mild": {
                "base": "Light shirt or blouse, comfortable pants or shorts",
                "accessories": "Comfortable shoes, optional light cardigan",
                "priority": "low"
            },
            "warm": {
                "base": "Light clothing, shorts or light pants, t-shirt",
                "accessories": "Breathable shoes, sun hat",
                "priority": "medium"
            },
            "hot": {
                "base": "Very light, breathable clothing, shorts, tank top",
                "accessories": "Sandals, wide-brim hat, sunglasses",
                "priority": "high"
            },
            "extreme_hot": {
                "base": "Minimal, ultra-light clothing with sun protection",
                "accessories": "Protective footwear, hat, sunglasses, cooling towel",
                "priority": "high"
            }
        }
        
        base_clothing = clothing_map.get(temp_class, clothing_map["mild"])
        
        recommendations.append(Recommendation(
            category="clothing_base",
            suggestion=f"Wear: {base_clothing['base']}",
            priority=base_clothing['priority'],
            reasoning=f"Temperature is {weather.temperature}°C ({temp_class})"
        ))
        
        recommendations.append(Recommendation(
            category="clothing_accessories",
            suggestion=f"Accessories: {base_clothing['accessories']}",
            priority=base_clothing['priority'],
            reasoning=f"Temperature and comfort optimization for {temp_class} weather"
        ))
        
        # Weather-specific modifications
        if weather.precipitation_prob > 60:
            recommendations.append(Recommendation(
                category="clothing_weather",
                suggestion="Bring waterproof jacket or umbrella",
                priority="high",
                reasoning=f"High precipitation probability ({weather.precipitation_prob}%)"
            ))
        
        if weather.wind_speed > 20:
            recommendations.append(Recommendation(
                category="clothing_weather",
                suggestion="Wear wind-resistant outer layer, secure accessories",
                priority="medium",
                reasoning=f"Strong winds expected ({weather.wind_speed} km/h)"
            ))
        
        if weather.uv_index > 6:
            recommendations.append(Recommendation(
                category="clothing_protection",
                suggestion="Apply sunscreen, wear UV-protective clothing and sunglasses",
                priority="high",
                reasoning=f"High UV index ({weather.uv_index})"
            ))
        
        return recommendations
    
    def generate_activity_recommendations(self, weather: WeatherData) -> List[Recommendation]:
        """Generate outdoor activity recommendations."""
        recommendations = []
        temp_class = self.classify_temperature(weather.temperature)
        
        # Temperature-based activities
        if temp_class in ["mild", "warm"]:
            if weather.precipitation_prob < 30:
                recommendations.append(Recommendation(
                    category="outdoor_activity",
                    suggestion="Perfect for hiking, cycling, or outdoor sports",
                    priority="high",
                    reasoning="Ideal temperature and low precipitation risk"
                ))
            
            recommendations.append(Recommendation(
                category="outdoor_activity", 
                suggestion="Great for picnics, outdoor dining, or walking",
                priority="medium",
                reasoning=f"Comfortable temperature ({weather.temperature}°C)"
            ))
        
        elif temp_class in ["hot", "extreme_hot"]:
            recommendations.append(Recommendation(
                category="outdoor_activity",
                suggestion="Early morning or evening activities recommended. Avoid midday sun.",
                priority="high",
                reasoning="High temperatures require timing consideration"
            ))
            
            recommendations.append(Recommendation(
                category="outdoor_activity",
                suggestion="Water activities, swimming, or shaded areas preferred",
                priority="medium",
                reasoning="Hot weather calls for cooling activities"
            ))
        
        elif temp_class in ["cold", "very_cold", "extreme_cold"]:
            recommendations.append(Recommendation(
                category="outdoor_activity",
                suggestion="Winter sports like skiing, ice skating, or snowshoeing",
                priority="medium",
                reasoning="Cold temperatures suitable for winter activities"
            ))
            
            if weather.condition == WeatherCondition.SNOW:
                recommendations.append(Recommendation(
                    category="outdoor_activity",
                    suggestion="Great conditions for snow activities and winter photography",
                    priority="high",
                    reasoning="Fresh snowfall creates ideal winter conditions"
                ))
        
        # Weather condition specific activities
        if weather.precipitation_prob > 70:
            recommendations.append(Recommendation(
                category="indoor_alternative",
                suggestion="Consider indoor activities: museums, shopping, indoor sports",
                priority="medium",
                reasoning=f"High chance of precipitation ({weather.precipitation_prob}%)"
            ))
        
        if weather.condition == WeatherCondition.