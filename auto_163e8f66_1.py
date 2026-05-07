```python
"""
Clothing Recommendation Engine

This module provides a clothing recommendation system that analyzes weather conditions
including temperature, precipitation probability, and wind speed to suggest appropriate
outfits. The engine uses conditional logic to match weather patterns with suitable
clothing items and layering strategies.

Features:
- Temperature-based base layer recommendations
- Precipitation-aware outerwear suggestions
- Wind condition considerations for additional layers
- Seasonal outfit coordination
- Activity-based clothing modifications

Usage: python script.py
"""

import json
import random
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import Enum


class WeatherCondition(Enum):
    """Enumeration of weather condition categories"""
    HOT = "hot"
    WARM = "warm"
    MILD = "mild"
    COOL = "cool"
    COLD = "cold"
    FREEZING = "freezing"


class ActivityLevel(Enum):
    """Enumeration of activity levels"""
    SEDENTARY = "sedentary"
    LIGHT = "light"
    MODERATE = "moderate"
    VIGOROUS = "vigorous"


@dataclass
class WeatherData:
    """Weather data structure"""
    temperature_f: float
    precipitation_probability: float  # 0-100
    wind_speed_mph: float
    humidity: float = 50.0
    activity: ActivityLevel = ActivityLevel.MODERATE


@dataclass
class ClothingItem:
    """Individual clothing item with properties"""
    name: str
    category: str
    warmth_rating: int  # 1-10 scale
    water_resistance: bool
    wind_resistance: bool
    breathability: int  # 1-10 scale


@dataclass
class OutfitRecommendation:
    """Complete outfit recommendation"""
    base_layer: List[ClothingItem]
    mid_layer: List[ClothingItem]
    outer_layer: List[ClothingItem]
    accessories: List[ClothingItem]
    footwear: List[ClothingItem]
    total_warmth: int
    weather_protection: str
    notes: List[str]


class ClothingDatabase:
    """Database of available clothing items"""
    
    def __init__(self):
        self.items = self._initialize_clothing_items()
    
    def _initialize_clothing_items(self) -> Dict[str, List[ClothingItem]]:
        """Initialize the clothing database"""
        return {
            "base_layer": [
                ClothingItem("Cotton T-shirt", "base_layer", 2, False, False, 8),
                ClothingItem("Moisture-wicking shirt", "base_layer", 3, False, False, 9),
                ClothingItem("Long-sleeve shirt", "base_layer", 4, False, False, 7),
                ClothingItem("Thermal underwear", "base_layer", 6, False, False, 6),
                ClothingItem("Merino wool base layer", "base_layer", 7, False, False, 8),
                ClothingItem("Tank top", "base_layer", 1, False, False, 10),
                ClothingItem("Polo shirt", "base_layer", 3, False, False, 7),
            ],
            "mid_layer": [
                ClothingItem("Light sweater", "mid_layer", 5, False, False, 6),
                ClothingItem("Fleece jacket", "mid_layer", 6, False, True, 7),
                ClothingItem("Wool cardigan", "mid_layer", 6, False, False, 5),
                ClothingItem("Down vest", "mid_layer", 7, False, True, 4),
                ClothingItem("Hoodie", "mid_layer", 5, False, False, 6),
                ClothingItem("Light jacket", "mid_layer", 4, False, True, 8),
                ClothingItem("Blazer", "mid_layer", 3, False, False, 4),
            ],
            "outer_layer": [
                ClothingItem("Rain jacket", "outer_layer", 2, True, True, 9),
                ClothingItem("Winter coat", "outer_layer", 9, True, True, 3),
                ClothingItem("Light windbreaker", "outer_layer", 1, False, True, 10),
                ClothingItem("Parka", "outer_layer", 10, True, True, 2),
                ClothingItem("Trench coat", "outer_layer", 4, True, False, 5),
                ClothingItem("Denim jacket", "outer_layer", 3, False, False, 6),
                ClothingItem("Bomber jacket", "outer_layer", 4, False, True, 6),
            ],
            "accessories": [
                ClothingItem("Knit hat", "accessories", 3, False, True, 5),
                ClothingItem("Baseball cap", "accessories", 1, False, False, 10),
                ClothingItem("Scarf", "accessories", 4, False, True, 4),
                ClothingItem("Gloves", "accessories", 3, False, True, 5),
                ClothingItem("Sunglasses", "accessories", 0, False, False, 10),
                ClothingItem("Light scarf", "accessories", 2, False, False, 7),
                ClothingItem("Warm gloves", "accessories", 5, False, True, 3),
            ],
            "footwear": [
                ClothingItem("Sneakers", "footwear", 2, False, False, 8),
                ClothingItem("Boots", "footwear", 4, True, True, 5),
                ClothingItem("Sandals", "footwear", 1, False, False, 10),
                ClothingItem("Dress shoes", "footwear", 2, False, False, 4),
                ClothingItem("Winter boots", "footwear", 6, True, True, 3),
                ClothingItem("Running shoes", "footwear", 2, False, False, 9),
                ClothingItem("Waterproof boots", "footwear", 4, True, True, 4),
            ],
            "bottoms": [
                ClothingItem("Shorts", "bottoms", 1, False, False, 10),
                ClothingItem("Light pants", "bottoms", 3, False, False, 8),
                ClothingItem("Jeans", "bottoms", 4, False, False, 6),
                ClothingItem("Thermal pants", "bottoms", 6, False, False, 5),
                ClothingItem("Waterproof pants", "bottoms", 4, True, True, 7),
                ClothingItem("Dress pants", "bottoms", 3, False, False, 5),
                ClothingItem("Leggings", "bottoms", 3, False, False, 8),
            ]
        }


class WeatherAnalyzer:
    """Analyzes weather conditions and categorizes them"""
    
    @staticmethod
    def categorize_temperature(temp_f: float, activity: ActivityLevel) -> WeatherCondition:
        """Categorize temperature based on Fahrenheit and activity level"""
        # Adjust temperature perception based on activity
        activity_adjustment = {
            ActivityLevel.SEDENTARY: 0,
            ActivityLevel.LIGHT: -5,
            ActivityLevel.MODERATE: -10,
            ActivityLevel.VIGOROUS: -15
        }
        
        adjusted_temp = temp_f + activity_adjustment[activity]
        
        if adjusted_temp >= 85:
            return WeatherCondition.HOT
        elif adjusted_temp >= 70:
            return WeatherCondition.WARM
        elif adjusted_temp >= 60:
            return WeatherCondition.MILD
        elif adjusted_temp >= 45:
            return WeatherCondition.COOL
        elif adjusted_temp >= 32:
            return WeatherCondition.COLD
        else:
            return WeatherCondition.FREEZING
    
    @staticmethod
    def assess_precipitation_risk(precipitation_prob: float) -> Tuple[bool, str]: