```python
"""
Automated Daily Weather & Outfit Recommendation System

This module provides an automated scheduling system that fetches weather data
and generates outfit recommendations at a specified daily time. It runs
continuously and executes the weather/outfit check at the configured schedule.

Features:
- Daily automated scheduling using threading
- Weather data retrieval from OpenWeatherMap API
- AI-powered outfit recommendations based on weather conditions
- Formatted output for display/notifications
- Comprehensive error handling and logging
- Self-contained with minimal dependencies

Dependencies: httpx, anthropic (beyond standard library)
Usage: python script.py
"""

import json
import threading
import time
import datetime
import logging
from typing import Dict, Any, Optional
import httpx
import anthropic

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WeatherOutfitScheduler:
    """Automated weather fetch and outfit recommendation scheduler."""
    
    def __init__(self, 
                 openweather_api_key: str = "your_openweather_api_key",
                 anthropic_api_key: str = "your_anthropic_api_key",
                 city: str = "San Francisco",
                 schedule_time: str = "08:00"):
        """
        Initialize the scheduler.
        
        Args:
            openweather_api_key: OpenWeatherMap API key
            anthropic_api_key: Anthropic API key for outfit recommendations
            city: City name for weather data
            schedule_time: Daily execution time in HH:MM format
        """
        self.openweather_api_key = openweather_api_key
        self.anthropic_api_key = anthropic_api_key
        self.city = city
        self.schedule_time = schedule_time
        self.running = False
        
        # Initialize Anthropic client if API key provided
        self.anthropic_client = None
        if anthropic_api_key and anthropic_api_key != "your_anthropic_api_key":
            try:
                self.anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize Anthropic client: {e}")
    
    def fetch_weather(self) -> Optional[Dict[str, Any]]:
        """
        Fetch current weather data from OpenWeatherMap API.
        
        Returns:
            Weather data dictionary or None if failed
        """
        try:
            if self.openweather_api_key == "your_openweather_api_key":
                # Return mock data for demo purposes
                return {
                    "main": {
                        "temp": 72,
                        "feels_like": 74,
                        "humidity": 65
                    },
                    "weather": [{
                        "main": "Clear",
                        "description": "clear sky"
                    }],
                    "wind": {"speed": 5.2},
                    "name": self.city
                }
            
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": self.city,
                "appid": self.openweather_api_key,
                "units": "imperial"
            }
            
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                return response.json()
                
        except httpx.RequestError as e:
            logger.error(f"Network error fetching weather: {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching weather: {e.response.status_code}")
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing weather response: {e}")
        except Exception as e:
            logger.error(f"Unexpected error fetching weather: {e}")
        
        return None
    
    def generate_outfit_recommendation(self, weather_data: Dict[str, Any]) -> str:
        """
        Generate outfit recommendation based on weather data.
        
        Args:
            weather_data: Weather information dictionary
            
        Returns:
            Outfit recommendation string
        """
        try:
            if not self.anthropic_client:
                return self._generate_basic_outfit_recommendation(weather_data)
            
            # Extract weather details
            temp = weather_data["main"]["temp"]
            condition = weather_data["weather"][0]["description"]
            humidity = weather_data["main"]["humidity"]
            wind_speed = weather_data.get("wind", {}).get("speed", 0)
            
            prompt = f"""Based on the current weather conditions, provide a concise outfit recommendation:

Temperature: {temp}°F
Condition: {condition}
Humidity: {humidity}%
Wind Speed: {wind_speed} mph

Please provide a practical outfit suggestion in 2-3 sentences, considering comfort and weather appropriateness."""

            message = self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=200,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            return message.content[0].text.strip()
            
        except Exception as e:
            logger.error(f"Error generating AI outfit recommendation: {e}")
            return self._generate_basic_outfit_recommendation(weather_data)
    
    def _generate_basic_outfit_recommendation(self, weather_data: Dict[str, Any]) -> str:
        """Generate basic outfit recommendation using rules."""
        temp = weather_data["main"]["temp"]
        condition = weather_data["weather"][0]["main"].lower()
        
        outfit = []
        
        # Temperature-based recommendations
        if temp < 32:
            outfit.append("heavy coat, warm layers, gloves, and hat")
        elif temp < 50:
            outfit.append("jacket or sweater, long pants")
        elif temp < 70:
            outfit.append("light sweater or long sleeves")
        elif temp < 85:
            outfit.append("t-shirt and comfortable pants or shorts")
        else:
            outfit.append("light, breathable clothing")
        
        # Weather condition adjustments
        if "rain" in condition or "drizzle" in condition:
            outfit.append("waterproof jacket and umbrella")
        elif "snow" in condition:
            outfit.append("waterproof boots and warm accessories")
        elif "wind" in condition:
            outfit.append("windbreaker")
        
        recommendation = f"Recommended outfit: {', '.join(outfit)}."
        
        if temp > 80:
            recommendation += " Stay hydrated and seek shade when possible."
        elif temp < 40:
            recommendation += " Layer up and protect exposed skin."
            
        return recommendation
    
    def format_weather_report(self, weather_data: Dict[str, Any], outfit_rec: str) -> str:
        """
        Format weather and outfit data for display.
        
        Args:
            weather_data: Weather information
            outfit_rec: Outfit recommendation
            
        Returns:
            Formatted report string
        """
        try:
            temp = weather_data["main"]["temp"]
            feels_like = weather_data["main"]["feels_like"]
            condition = weather_data["weather"][0]["description"].title()
            humidity = weather_data["main"]["humidity"]
            wind_speed = weather_data.get("wind", {}).get("speed", 0)
            city = weather_data.get("name", self.city)
            
            report = f"""
╔══════════════════════════════════════════════════════════════════════
║ DAILY WEATHER & OUTFIT REPORT
║ {datetime.datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}
╠══════════════════════════════════════════════════════════════════════
║ 📍 Location: {city}
║ 🌡️  Temperature: {temp}°F (feels like {feels_like}°F)
║ ☁️  Condition: {condition}
║