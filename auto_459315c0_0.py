```python
#!/usr/bin/env python3
"""
Weather Data Fetcher

This module fetches weather data from OpenWeatherMap API for multiple cities.
It handles API authentication, error handling, and formats the data into
structured daily summaries including current weather and 5-day forecasts.

Features:
- Fetches current weather and 5-day forecast for multiple cities
- Handles API authentication and rate limiting
- Comprehensive error handling for network and API issues
- Structured output with temperature, conditions, and forecasts
- Self-contained with minimal dependencies

Usage:
    python script.py

Requirements:
    - httpx library for HTTP requests
    - Valid OpenWeatherMap API key (set as environment variable or modify API_KEY)
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any

try:
    import httpx
except ImportError:
    print("Error: httpx library is required. Install with: pip install httpx")
    sys.exit(1)


class WeatherFetcher:
    """Handles weather data fetching from OpenWeatherMap API."""
    
    def __init__(self, api_key: str):
        """
        Initialize WeatherFetcher with API key.
        
        Args:
            api_key: OpenWeatherMap API key
        """
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.client = httpx.Client(timeout=30.0)
    
    def fetch_current_weather(self, city: str) -> Optional[Dict[str, Any]]:
        """
        Fetch current weather data for a city.
        
        Args:
            city: Name of the city
            
        Returns:
            Dictionary containing weather data or None if failed
        """
        try:
            url = f"{self.base_url}/weather"
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric"
            }
            
            response = self.client.get(url, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                print(f"Error: Invalid API key for {city}")
            elif e.response.status_code == 404:
                print(f"Error: City '{city}' not found")
            else:
                print(f"Error: HTTP {e.response.status_code} for {city}")
            return None
            
        except httpx.RequestError as e:
            print(f"Error: Network request failed for {city}: {e}")
            return None
        
        except Exception as e:
            print(f"Error: Unexpected error for {city}: {e}")
            return None
    
    def fetch_forecast(self, city: str) -> Optional[Dict[str, Any]]:
        """
        Fetch 5-day weather forecast for a city.
        
        Args:
            city: Name of the city
            
        Returns:
            Dictionary containing forecast data or None if failed
        """
        try:
            url = f"{self.base_url}/forecast"
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric"
            }
            
            response = self.client.get(url, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                print(f"Error: Invalid API key for forecast {city}")
            elif e.response.status_code == 404:
                print(f"Error: City '{city}' not found for forecast")
            else:
                print(f"Error: HTTP {e.response.status_code} for forecast {city}")
            return None
            
        except httpx.RequestError as e:
            print(f"Error: Network request failed for forecast {city}: {e}")
            return None
        
        except Exception as e:
            print(f"Error: Unexpected error for forecast {city}: {e}")
            return None
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()


class WeatherFormatter:
    """Formats weather data into structured summaries."""
    
    @staticmethod
    def format_current_weather(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format current weather data.
        
        Args:
            data: Raw weather data from API
            
        Returns:
            Formatted weather summary
        """
        try:
            return {
                "city": data["name"],
                "country": data["sys"]["country"],
                "temperature": {
                    "current": round(data["main"]["temp"], 1),
                    "feels_like": round(data["main"]["feels_like"], 1),
                    "min": round(data["main"]["temp_min"], 1),
                    "max": round(data["main"]["temp_max"], 1)
                },
                "conditions": {
                    "main": data["weather"][0]["main"],
                    "description": data["weather"][0]["description"].title(),
                    "humidity": data["main"]["humidity"],
                    "pressure": data["main"]["pressure"]
                },
                "wind": {
                    "speed": data["wind"]["speed"],
                    "direction": data["wind"].get("deg", "N/A")
                },
                "visibility": data.get("visibility", "N/A"),
                "timestamp": datetime.fromtimestamp(data["dt"]).strftime("%Y-%m-%d %H:%M:%S")
            }
        except KeyError as e:
            print(f"Error: Missing field in weather data: {e}")
            return {}
    
    @staticmethod
    def format_forecast(data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Format 5-day forecast data into daily summaries.
        
        Args:
            data: Raw forecast data from API
            
        Returns:
            List of daily forecast summaries
        """
        try:
            daily_forecasts = {}
            
            for item in data["list"]:
                date = datetime.fromtimestamp(item["dt"]).strftime("%Y-%m-%d")
                
                if date not in daily_forecasts:
                    daily_forecasts[date] = {
                        "date": date,
                        "temperatures": [],
                        "conditions": [],
                        "humidity": [],
                        "pressure": []
                    }
                
                daily_forecasts[date]["temperatures"].append(item["main"]["temp"])
                daily_forecasts[date]["conditions"].append(item["weather"][0]["description"])
                daily_forecasts[date]["humidity"].append(item["main"]["humidity"])
                daily_forecasts[date]["pressure"].append(item["main"]["pressure"])
            
            # Summarize daily data
            formatted_forecasts = []
            for date, day_data in daily_forecasts.items():
                temps = day_data["temperatures"]
                formatted_forecasts.append({
                    "date": date,
                    "temperature": {
                        "min": round(min(temps), 1),
                        "max": round(max(temps), 1),
                        "avg": round(sum(temps) / len(temps), 1)
                    },
                    "conditions": {
                        "primary": max(set(day_data["conditions"]), key=day_data["conditions"].count).title(),
                        "avg_humidity": round(sum(day_data["humidity"]) / len(day_data["humidity"]), 1),
                        "avg_pressure": round(sum(day_data["pressure"]) / len(day_data["pressure"]), 1)
                    }
                })
            
            return sorted(formatted_forecasts, key=lambda x: x["date"])
            
        except KeyError as e:
            print(f"Error: Missing field in forecast data: {e}")
            return []


def print_weather_summary(city_data: Dict[str, Any]):
    """
    Print formatted weather summary for a city.
    
    Args:
        city_data: