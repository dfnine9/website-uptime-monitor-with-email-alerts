```python
"""
Weather-Based Clothing Recommendation Engine

This module provides a rule-based clothing recommendation system that suggests
appropriate outfits based on weather conditions including temperature, precipitation,
wind speed, and seasonal considerations. The engine uses predefined rules and logic
to map weather data to specific clothing recommendations.

Features:
- Temperature-based clothing suggestions with seasonal adjustments
- Precipitation-aware recommendations (rain, snow, etc.)
- Wind condition considerations for layering
- Seasonal outfit modifications (spring, summer, fall, winter)
- Rule-based logic engine for consistent recommendations
- Error handling for invalid inputs and edge cases

Usage:
    python script.py

The script will demonstrate the recommendation engine with various weather scenarios
and print the suggested outfits to stdout.
"""

import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from enum import Enum


class Season(Enum):
    SPRING = "spring"
    SUMMER = "summer"
    FALL = "fall"
    WINTER = "winter"


class PrecipitationType(Enum):
    NONE = "none"
    LIGHT_RAIN = "light_rain"
    HEAVY_RAIN = "heavy_rain"
    SNOW = "snow"
    SLEET = "sleet"


class ClothingItem:
    def __init__(self, name: str, category: str, warmth_level: int, 
                 water_resistant: bool = False, wind_resistant: bool = False):
        self.name = name
        self.category = category
        self.warmth_level = warmth_level  # 1-5 scale
        self.water_resistant = water_resistant
        self.wind_resistant = wind_resistant


class WeatherCondition:
    def __init__(self, temperature: float, precipitation_type: PrecipitationType,
                 precipitation_intensity: float, wind_speed: float, 
                 humidity: float, season: Season):
        self.temperature = temperature  # Fahrenheit
        self.precipitation_type = precipitation_type
        self.precipitation_intensity = precipitation_intensity  # 0-1 scale
        self.wind_speed = wind_speed  # mph
        self.humidity = humidity  # 0-100 percentage
        self.season = season


class ClothingRecommendationEngine:
    def __init__(self):
        self.clothing_database = self._initialize_clothing_database()
        self.temperature_rules = self._initialize_temperature_rules()
        self.seasonal_adjustments = self._initialize_seasonal_adjustments()
    
    def _initialize_clothing_database(self) -> Dict[str, List[ClothingItem]]:
        """Initialize the clothing item database organized by category"""
        try:
            return {
                "tops": [
                    ClothingItem("Tank top", "tops", 1),
                    ClothingItem("T-shirt", "tops", 2),
                    ClothingItem("Long sleeve shirt", "tops", 3),
                    ClothingItem("Light sweater", "tops", 4),
                    ClothingItem("Heavy sweater", "tops", 5),
                    ClothingItem("Hoodie", "tops", 4, wind_resistant=True),
                ],
                "outerwear": [
                    ClothingItem("Light cardigan", "outerwear", 2),
                    ClothingItem("Denim jacket", "outerwear", 3, wind_resistant=True),
                    ClothingItem("Light jacket", "outerwear", 3, water_resistant=True),
                    ClothingItem("Rain jacket", "outerwear", 2, water_resistant=True, wind_resistant=True),
                    ClothingItem("Windbreaker", "outerwear", 2, wind_resistant=True),
                    ClothingItem("Wool coat", "outerwear", 5),
                    ClothingItem("Winter parka", "outerwear", 5, water_resistant=True, wind_resistant=True),
                    ClothingItem("Heavy winter coat", "outerwear", 5, water_resistant=True, wind_resistant=True),
                ],
                "bottoms": [
                    ClothingItem("Shorts", "bottoms", 1),
                    ClothingItem("Lightweight pants", "bottoms", 2),
                    ClothingItem("Jeans", "bottoms", 3),
                    ClothingItem("Dress pants", "bottoms", 3),
                    ClothingItem("Thermal leggings", "bottoms", 4),
                    ClothingItem("Wool pants", "bottoms", 4),
                    ClothingItem("Waterproof pants", "bottoms", 3, water_resistant=True),
                ],
                "footwear": [
                    ClothingItem("Sandals", "footwear", 1),
                    ClothingItem("Sneakers", "footwear", 2),
                    ClothingItem("Canvas shoes", "footwear", 2),
                    ClothingItem("Leather shoes", "footwear", 3),
                    ClothingItem("Waterproof boots", "footwear", 4, water_resistant=True),
                    ClothingItem("Winter boots", "footwear", 5, water_resistant=True),
                ],
                "accessories": [
                    ClothingItem("Sunglasses", "accessories", 0),
                    ClothingItem("Light scarf", "accessories", 2),
                    ClothingItem("Warm scarf", "accessories", 3),
                    ClothingItem("Beanie", "accessories", 3),
                    ClothingItem("Winter hat", "accessories", 4),
                    ClothingItem("Gloves", "accessories", 3),
                    ClothingItem("Umbrella", "accessories", 0, water_resistant=True),
                    ClothingItem("Rain hat", "accessories", 2, water_resistant=True),
                ]
            }
        except Exception as e:
            print(f"Error initializing clothing database: {e}")
            return {}
    
    def _initialize_temperature_rules(self) -> List[Tuple[Tuple[float, float], int]]:
        """Initialize temperature-based warmth level rules"""
        return [
            ((-float('inf'), 20), 5),  # Below 20°F - Maximum warmth
            ((20, 32), 5),             # 20-32°F - Heavy winter clothing
            ((32, 50), 4),             # 32-50°F - Moderate winter clothing
            ((50, 65), 3),             # 50-65°F - Light layers
            ((65, 75), 2),             # 65-75°F - Comfortable clothing
            ((75, 85), 1),             # 75-85°F - Light clothing
            ((85, float('inf')), 1),   # Above 85°F - Minimal clothing
        ]
    
    def _initialize_seasonal_adjustments(self) -> Dict[Season, Dict[str, int]]:
        """Initialize seasonal warmth adjustments"""
        return {
            Season.SPRING: {"warmth_adjustment": -1, "rain_likelihood": 0.3},
            Season.SUMMER: {"warmth_adjustment": -2, "rain_likelihood": 0.2},
            Season.FALL: {"warmth_adjustment": 0, "rain_likelihood": 0.4},
            Season.WINTER: {"warmth_adjustment": 1, "rain_likelihood": 0.2},
        }
    
    def _get_required_warmth_level(self, weather: WeatherCondition) -> int:
        """Determine required warmth level based on temperature and season"""
        try:
            base_warmth = 3  # Default moderate warmth
            
            # Apply temperature rules
            for (temp_min, temp_max), warmth in self.temperature_rules:
                if temp_min < weather.temperature <= temp_max:
                    base_warmth = warmth
                    break
            
            # Apply seasonal adjustment
            seasonal_adj = self.seasonal_adjustments[weather.season]["warmth_adjustment"]
            adjusted_warmth = base_warmth + seasonal_adj
            
            # Apply wind chill adjustment
            if weather.wind_speed > 15:  # High wind
                adjusted_warmth