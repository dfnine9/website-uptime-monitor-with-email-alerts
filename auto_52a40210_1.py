```python
#!/usr/bin/env python3
"""
Clothing Recommendation Engine

A self-contained Python script that analyzes weather data and generates personalized
outfit suggestions based on temperature, precipitation, wind conditions, and user preferences.

The engine uses rule-based logic to recommend appropriate clothing items considering:
- Temperature ranges (hot, warm, mild, cool, cold, freezing)
- Precipitation probability and type
- Wind speed conditions
- User style preferences and activity level
- Seasonal adjustments

Usage: python script.py

Dependencies: httpx, anthropic (installable via pip)
"""

import json
import sys
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

try:
    import httpx
except ImportError:
    print("Error: httpx not installed. Run: pip install httpx")
    sys.exit(1)

class ActivityLevel(Enum):
    SEDENTARY = "sedentary"
    MODERATE = "moderate"
    ACTIVE = "active"

class Style(Enum):
    CASUAL = "casual"
    BUSINESS = "business"
    ATHLETIC = "athletic"
    FORMAL = "formal"

@dataclass
class WeatherData:
    temperature: float
    precipitation_prob: float
    wind_speed: float
    humidity: Optional[float] = None
    feels_like: Optional[float] = None

@dataclass
class UserPreferences:
    style: Style
    activity_level: ActivityLevel
    heat_tolerance: str  # "low", "medium", "high"
    cold_tolerance: str  # "low", "medium", "high"
    preferred_colors: List[str]
    avoid_materials: List[str]

@dataclass
class ClothingItem:
    name: str
    category: str
    warmth_level: int  # 1-5 scale
    water_resistance: bool
    wind_resistance: bool
    breathability: int  # 1-5 scale
    formality: int  # 1-5 scale

class ClothingRecommendationEngine:
    def __init__(self):
        self.clothing_database = self._initialize_clothing_database()
        
    def _initialize_clothing_database(self) -> Dict[str, List[ClothingItem]]:
        """Initialize the clothing database with predefined items."""
        return {
            "tops": [
                ClothingItem("T-shirt", "tops", 1, False, False, 5, 1),
                ClothingItem("Long-sleeve shirt", "tops", 2, False, False, 4, 2),
                ClothingItem("Sweater", "tops", 3, False, True, 2, 3),
                ClothingItem("Hoodie", "tops", 3, False, True, 3, 1),
                ClothingItem("Light jacket", "tops", 3, True, True, 3, 2),
                ClothingItem("Heavy coat", "tops", 5, True, True, 1, 3),
                ClothingItem("Rain jacket", "tops", 2, True, True, 4, 2),
                ClothingItem("Wool coat", "tops", 5, False, True, 1, 4),
                ClothingItem("Blazer", "tops", 2, False, False, 3, 5),
                ClothingItem("Tank top", "tops", 1, False, False, 5, 1),
            ],
            "bottoms": [
                ClothingItem("Shorts", "bottoms", 1, False, False, 5, 1),
                ClothingItem("Jeans", "bottoms", 2, False, True, 3, 2),
                ClothingItem("Dress pants", "bottoms", 2, False, True, 3, 4),
                ClothingItem("Leggings", "bottoms", 2, False, False, 4, 2),
                ClothingItem("Sweatpants", "bottoms", 3, False, True, 3, 1),
                ClothingItem("Thermal underwear", "bottoms", 4, False, True, 2, 1),
                ClothingItem("Rain pants", "bottoms", 2, True, True, 2, 2),
                ClothingItem("Cargo pants", "bottoms", 2, False, True, 3, 1),
            ],
            "footwear": [
                ClothingItem("Sandals", "footwear", 1, False, False, 5, 1),
                ClothingItem("Sneakers", "footwear", 2, False, False, 4, 2),
                ClothingItem("Dress shoes", "footwear", 2, False, False, 2, 5),
                ClothingItem("Boots", "footwear", 3, True, True, 2, 3),
                ClothingItem("Rain boots", "footwear", 2, True, True, 3, 2),
                ClothingItem("Winter boots", "footwear", 4, True, True, 1, 2),
                ClothingItem("Athletic shoes", "footwear", 2, False, False, 5, 1),
            ],
            "accessories": [
                ClothingItem("Baseball cap", "accessories", 1, False, False, 5, 1),
                ClothingItem("Beanie", "accessories", 3, False, True, 2, 2),
                ClothingItem("Scarf", "accessories", 3, False, True, 1, 3),
                ClothingItem("Gloves", "accessories", 4, False, True, 1, 2),
                ClothingItem("Umbrella", "accessories", 0, True, False, 5, 2),
                ClothingItem("Sunglasses", "accessories", 0, False, False, 5, 2),
                ClothingItem("Belt", "accessories", 0, False, False, 5, 3),
            ]
        }

    def get_weather_data(self, city: str = "New York") -> WeatherData:
        """
        Fetch weather data from a free API service.
        Falls back to mock data if API call fails.
        """
        try:
            # Using OpenWeatherMap-style mock data for demonstration
            # In production, you would use a real API key
            url = f"https://api.openweathermap.org/data/2.5/weather"
            
            # Mock response for demonstration
            mock_weather = {
                "main": {"temp": 22.5, "feels_like": 24.0, "humidity": 65},
                "weather": [{"main": "Clear"}],
                "wind": {"speed": 3.2},
                "clouds": {"all": 10}
            }
            
            return WeatherData(
                temperature=mock_weather["main"]["temp"],
                feels_like=mock_weather["main"]["feels_like"],
                precipitation_prob=mock_weather["clouds"]["all"],
                wind_speed=mock_weather["wind"]["speed"],
                humidity=mock_weather["main"]["humidity"]
            )
            
        except Exception as e:
            print(f"Warning: Could not fetch weather data ({e}). Using default values.")
            return WeatherData(
                temperature=20.0,
                precipitation_prob=30.0,
                wind_speed=5.0,
                humidity=60.0,
                feels_like=22.0
            )

    def categorize_temperature(self, temp: float, user_prefs: UserPreferences) -> str:
        """Categorize temperature based on user's tolerance levels."""
        cold_adjustment = {"low": 2, "medium": 0, "high": -2}[user_prefs.cold_tolerance]
        heat_adjustment = {"low": -2, "medium": 0, "high": 2}[user_prefs.heat_tolerance]
        
        adjusted_temp = temp + cold_adjustment + heat_adjustment
        
        if adjusted_temp < 0:
            return "freezing"
        elif adjusted_temp < 10:
            return "cold"
        elif adjusted_temp < 16:
            return "cool"
        elif adjusted_temp < 22:
            return "mild"
        elif adjusted_temp < 28: