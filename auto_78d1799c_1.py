```python
"""
Weather-Based Clothing Recommendation Algorithm

This module provides intelligent clothing recommendations based on current weather conditions.
It analyzes temperature, precipitation, wind speed, and humidity to suggest appropriate outfits
for different scenarios (casual, business, outdoor activities).

The algorithm considers:
- Temperature ranges with seasonal adjustments
- Rain/snow protection requirements
- Wind chill factors
- Humidity comfort levels
- Activity-specific clothing needs

Usage: python script.py
"""

import json
import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class ActivityLevel(Enum):
    CASUAL = "casual"
    BUSINESS = "business"
    OUTDOOR = "outdoor"
    EXERCISE = "exercise"


@dataclass
class WeatherConditions:
    temperature_f: float
    humidity_percent: float
    wind_speed_mph: float
    precipitation_type: Optional[str] = None  # None, "rain", "snow"
    precipitation_intensity: float = 0.0  # 0-1 scale
    uv_index: float = 0.0


@dataclass
class ClothingItem:
    name: str
    category: str
    warmth_rating: float  # 1-10 scale
    water_resistance: bool
    wind_resistance: bool
    breathability: float  # 1-10 scale


class ClothingRecommendationEngine:
    def __init__(self):
        self.clothing_database = self._initialize_clothing_database()
        
    def _initialize_clothing_database(self) -> Dict[str, List[ClothingItem]]:
        """Initialize comprehensive clothing database with ratings"""
        return {
            "tops": [
                ClothingItem("T-shirt", "casual", 1, False, False, 9),
                ClothingItem("Long sleeve shirt", "casual", 3, False, False, 8),
                ClothingItem("Sweater", "casual", 6, False, True, 5),
                ClothingItem("Hoodie", "casual", 5, False, True, 6),
                ClothingItem("Fleece jacket", "casual", 7, False, True, 7),
                ClothingItem("Rain jacket", "outdoor", 3, True, True, 8),
                ClothingItem("Winter coat", "outdoor", 9, True, True, 4),
                ClothingItem("Blazer", "business", 4, False, False, 6),
                ClothingItem("Dress shirt", "business", 2, False, False, 7),
                ClothingItem("Cardigan", "business", 5, False, False, 7),
            ],
            "bottoms": [
                ClothingItem("Shorts", "casual", 1, False, False, 10),
                ClothingItem("Jeans", "casual", 4, False, True, 6),
                ClothingItem("Chinos", "business", 3, False, False, 7),
                ClothingItem("Dress pants", "business", 3, False, False, 6),
                ClothingItem("Thermal leggings", "outdoor", 7, False, True, 5),
                ClothingItem("Rain pants", "outdoor", 2, True, True, 7),
            ],
            "footwear": [
                ClothingItem("Sandals", "casual", 1, False, False, 10),
                ClothingItem("Sneakers", "casual", 2, False, False, 8),
                ClothingItem("Boots", "outdoor", 5, True, True, 6),
                ClothingItem("Dress shoes", "business", 2, False, False, 5),
                ClothingItem("Winter boots", "outdoor", 8, True, True, 4),
            ],
            "accessories": [
                ClothingItem("Baseball cap", "casual", 0, False, False, 10),
                ClothingItem("Beanie", "casual", 4, False, True, 7),
                ClothingItem("Scarf", "casual", 5, False, True, 5),
                ClothingItem("Gloves", "outdoor", 6, False, True, 6),
                ClothingItem("Umbrella", "outdoor", 0, True, False, 10),
                ClothingItem("Sunglasses", "casual", 0, False, False, 10),
            ]
        }
    
    def calculate_wind_chill(self, temp_f: float, wind_mph: float) -> float:
        """Calculate wind chill factor"""
        if temp_f > 50 or wind_mph < 3:
            return temp_f
        
        wind_chill = (35.74 + (0.6215 * temp_f) - 
                     (35.75 * (wind_mph ** 0.16)) + 
                     (0.4275 * temp_f * (wind_mph ** 0.16)))
        return wind_chill
    
    def calculate_heat_index(self, temp_f: float, humidity: float) -> float:
        """Calculate heat index for hot weather"""
        if temp_f < 80:
            return temp_f
            
        hi = (-42.379 + 2.04901523 * temp_f + 10.14333127 * humidity -
              0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2 -
              5.481717e-2 * humidity**2 + 1.22874e-3 * temp_f**2 * humidity +
              8.5282e-4 * temp_f * humidity**2 - 1.99e-6 * temp_f**2 * humidity**2)
        return hi
    
    def determine_warmth_need(self, weather: WeatherConditions) -> float:
        """Calculate required warmth rating based on weather"""
        effective_temp = self.calculate_wind_chill(weather.temperature_f, weather.wind_speed_mph)
        
        if effective_temp >= 80:
            return 1  # Very light clothing
        elif effective_temp >= 70:
            return 2
        elif effective_temp >= 60:
            return 3
        elif effective_temp >= 50:
            return 4
        elif effective_temp >= 40:
            return 5
        elif effective_temp >= 30:
            return 6
        elif effective_temp >= 20:
            return 7
        elif effective_temp >= 10:
            return 8
        else:
            return 9  # Very warm clothing needed
    
    def needs_rain_protection(self, weather: WeatherConditions) -> bool:
        """Determine if rain protection is needed"""
        return (weather.precipitation_type == "rain" and 
                weather.precipitation_intensity > 0.3)
    
    def needs_snow_protection(self, weather: WeatherConditions) -> bool:
        """Determine if snow protection is needed"""
        return (weather.precipitation_type == "snow" and 
                weather.precipitation_intensity > 0.2)
    
    def needs_wind_protection(self, weather: WeatherConditions) -> bool:
        """Determine if wind protection is needed"""
        return weather.wind_speed_mph > 15
    
    def filter_by_activity(self, items: List[ClothingItem], activity: ActivityLevel) -> List[ClothingItem]:
        """Filter clothing items by activity appropriateness"""
        if activity == ActivityLevel.BUSINESS:
            return [item for item in items if item.category in ["business", "casual"]]
        elif activity == ActivityLevel.OUTDOOR:
            return [item for item in items if item.category in ["outdoor", "casual"]]
        else:  # CASUAL or EXERCISE
            return items
    
    def score_clothing_item(self, item: ClothingItem, weather: WeatherConditions, 
                           warmth_needed: float) -> float:
        """Score a clothing item based on weather appropriateness"""
        score = 0.0
        
        # Temperature appropriateness
        temp_diff = abs(item.warmth_rating - warmth_needed)
        if temp_diff == 0:
            score += 10
        elif