```python
"""
Automated Daily Weather & Outfit Recommendation Scheduler

This module creates an automated scheduler that fetches daily weather data and
generates clothing recommendations based on temperature, conditions, and season.
Results are saved to a dated text file and displayed to stdout.

The scheduler runs daily weather checks and outfit suggestions, formatting output
into readable reports with weather summaries and contextual clothing advice.

Dependencies: httpx (for HTTP requests)
Usage: python script.py
"""

import json
import datetime
import time
import threading
import os
from typing import Dict, List, Optional

try:
    import httpx
except ImportError:
    print("Error: httpx not installed. Run: pip install httpx")
    exit(1)


class WeatherService:
    """Handles weather data fetching from OpenWeatherMap API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or "demo_key"  # Use demo for testing
        self.base_url = "http://api.openweathermap.org/data/2.5"
    
    def get_weather(self, city: str = "London") -> Dict:
        """Fetch current weather data for specified city"""
        try:
            with httpx.Client(timeout=10.0) as client:
                url = f"{self.base_url}/weather"
                params = {
                    "q": city,
                    "appid": self.api_key,
                    "units": "metric"
                }
                response = client.get(url, params=params)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    # Return mock data for demo purposes
                    return self._get_mock_weather()
                    
        except Exception as e:
            print(f"Weather API error: {e}")
            return self._get_mock_weather()
    
    def _get_mock_weather(self) -> Dict:
        """Return mock weather data when API is unavailable"""
        return {
            "name": "Demo City",
            "main": {
                "temp": 18.5,
                "feels_like": 16.2,
                "humidity": 65
            },
            "weather": [{
                "main": "Clouds",
                "description": "partly cloudy"
            }],
            "wind": {"speed": 3.2}
        }


class OutfitRecommender:
    """Generates clothing recommendations based on weather conditions"""
    
    def __init__(self):
        self.temperature_ranges = {
            "very_cold": (-20, 0),
            "cold": (0, 10),
            "cool": (10, 18),
            "mild": (18, 25),
            "warm": (25, 30),
            "hot": (30, 50)
        }
        
        self.outfits = {
            "very_cold": [
                "Heavy winter coat or parka",
                "Thermal underwear",
                "Wool sweater",
                "Insulated boots",
                "Warm hat and gloves",
                "Scarf"
            ],
            "cold": [
                "Winter jacket",
                "Long-sleeve shirt",
                "Jeans or warm pants",
                "Closed-toe shoes",
                "Light scarf",
                "Beanie (optional)"
            ],
            "cool": [
                "Light jacket or cardigan",
                "Long-sleeve shirt or sweater",
                "Jeans or trousers",
                "Sneakers or boots",
                "Light layers"
            ],
            "mild": [
                "Light sweater or hoodie",
                "T-shirt or blouse",
                "Jeans or casual pants",
                "Sneakers",
                "Optional light jacket"
            ],
            "warm": [
                "T-shirt or tank top",
                "Shorts or light pants",
                "Sandals or sneakers",
                "Sunglasses",
                "Light cotton clothing"
            ],
            "hot": [
                "Lightweight, breathable fabrics",
                "Shorts and tank top",
                "Sandals",
                "Sun hat",
                "Sunglasses",
                "Stay hydrated!"
            ]
        }
        
        self.weather_modifiers = {
            "rain": ["Umbrella", "Waterproof jacket", "Rain boots"],
            "snow": ["Waterproof boots", "Extra warm layers", "Gloves"],
            "wind": ["Windbreaker", "Secure hat", "Avoid loose clothing"]
        }
    
    def get_temperature_category(self, temp: float) -> str:
        """Categorize temperature into clothing-appropriate ranges"""
        for category, (min_temp, max_temp) in self.temperature_ranges.items():
            if min_temp <= temp < max_temp:
                return category
        return "mild"  # Default fallback
    
    def recommend_outfit(self, weather_data: Dict) -> List[str]:
        """Generate outfit recommendations based on weather data"""
        temp = weather_data["main"]["temp"]
        conditions = weather_data["weather"][0]["main"].lower()
        description = weather_data["weather"][0]["description"]
        
        temp_category = self.get_temperature_category(temp)
        recommendations = self.outfits[temp_category].copy()
        
        # Add weather-specific modifiers
        if "rain" in description or conditions == "rain":
            recommendations.extend(self.weather_modifiers["rain"])
        
        if "snow" in description or conditions == "snow":
            recommendations.extend(self.weather_modifiers["snow"])
        
        if weather_data.get("wind", {}).get("speed", 0) > 5:
            recommendations.extend(self.weather_modifiers["wind"])
        
        return recommendations


class DailyScheduler:
    """Automated scheduler for daily weather and outfit recommendations"""
    
    def __init__(self, city: str = "London"):
        self.weather_service = WeatherService()
        self.outfit_recommender = OutfitRecommender()
        self.city = city
        self.running = False
    
    def generate_daily_report(self) -> str:
        """Generate a complete daily weather and outfit report"""
        current_time = datetime.datetime.now()
        date_str = current_time.strftime("%Y-%m-%d")
        
        print(f"Generating daily report for {date_str}...")
        
        try:
            # Fetch weather data
            weather_data = self.weather_service.get_weather(self.city)
            
            # Generate outfit recommendations
            outfit_suggestions = self.outfit_recommender.recommend_outfit(weather_data)
            
            # Format report
            report = self._format_report(weather_data, outfit_suggestions, current_time)
            
            # Save to file
            filename = f"daily_weather_report_{date_str}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(report)
            
            print(f"Report saved to: {filename}")
            return report
            
        except Exception as e:
            error_report = f"Error generating report: {e}\n"
            print(error_report)
            return error_report
    
    def _format_report(self, weather_data: Dict, outfits: List[str], timestamp: datetime.datetime) -> str:
        """Format weather and outfit data into readable report"""
        city_name = weather_data.get("name", "Unknown City")
        temp = weather_data["main"]["temp"]
        feels_like = weather_data["main"]["feels_like"]
        humidity = weather_data["main"]["humidity"]
        description = weather_data["weather"][0]["description"].title()
        
        report = f"""
=== DAILY WEATHER & OUTFIT REPORT ===
Date: {timestamp.strftime("%A, %B %d, %Y")}
Time: {timestamp.strftime("%I:%M %p")}
Location: {city_name}

WEATHER SUMMARY:
• Temperature: {temp}°C (feels like {feels_like}°C)
• Conditions: {description}
• Humidity: {humidity}%

CLOTHING RECOMMENDATIONS:
"""
        for i, item in enumerate(outf