```python
#!/usr/bin/env python3
"""
OpenWeatherMap Weather Reporter

This module fetches current weather conditions and 5-day forecast data from the
OpenWeatherMap API, processes the data, and generates structured daily reports
containing temperature, humidity, precipitation, and wind information.

The script outputs formatted weather reports to stdout, including current conditions
and a 5-day forecast with daily summaries.

Requirements:
- OpenWeatherMap API key (set as environment variable OPENWEATHER_API_KEY)
- httpx library for HTTP requests
- Standard library modules for data processing

Usage: python weather_reporter.py
"""

import json
import os
import sys
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

try:
    import httpx
except ImportError:
    print("Error: httpx library is required. Install with: pip install httpx")
    sys.exit(1)


class WeatherReporter:
    """Handles weather data fetching and reporting from OpenWeatherMap API."""
    
    def __init__(self, api_key: str, city: str = "New York", country_code: str = "US"):
        """
        Initialize WeatherReporter with API credentials and location.
        
        Args:
            api_key: OpenWeatherMap API key
            city: City name for weather data
            country_code: ISO country code
        """
        self.api_key = api_key
        self.city = city
        self.country_code = country_code
        self.base_url = "https://api.openweathermap.org/data/2.5"
        
    def fetch_current_weather(self) -> Optional[Dict[str, Any]]:
        """
        Fetch current weather conditions.
        
        Returns:
            Dictionary containing current weather data or None if failed
        """
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(
                    f"{self.base_url}/weather",
                    params={
                        "q": f"{self.city},{self.country_code}",
                        "appid": self.api_key,
                        "units": "metric"
                    }
                )
                response.raise_for_status()
                return response.json()
        except httpx.RequestError as e:
            print(f"Error fetching current weather: {e}")
            return None
        except httpx.HTTPStatusError as e:
            print(f"HTTP error fetching current weather: {e}")
            return None
            
    def fetch_forecast(self) -> Optional[Dict[str, Any]]:
        """
        Fetch 5-day weather forecast.
        
        Returns:
            Dictionary containing forecast data or None if failed
        """
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(
                    f"{self.base_url}/forecast",
                    params={
                        "q": f"{self.city},{self.country_code}",
                        "appid": self.api_key,
                        "units": "metric"
                    }
                )
                response.raise_for_status()
                return response.json()
        except httpx.RequestError as e:
            print(f"Error fetching forecast: {e}")
            return None
        except httpx.HTTPStatusError as e:
            print(f"HTTP error fetching forecast: {e}")
            return None
            
    def process_current_weather(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process current weather data into structured format.
        
        Args:
            data: Raw weather data from API
            
        Returns:
            Processed weather data
        """
        try:
            main = data.get("main", {})
            weather = data.get("weather", [{}])[0]
            wind = data.get("wind", {})
            rain = data.get("rain", {})
            snow = data.get("snow", {})
            
            # Calculate precipitation
            precipitation = 0
            if rain.get("1h"):
                precipitation += rain["1h"]
            if snow.get("1h"):
                precipitation += snow["1h"]
                
            return {
                "location": f"{data.get('name', 'Unknown')}, {data.get('sys', {}).get('country', 'Unknown')}",
                "datetime": datetime.fromtimestamp(data.get("dt", 0), tz=timezone.utc),
                "description": weather.get("description", "").title(),
                "temperature": {
                    "current": main.get("temp", 0),
                    "feels_like": main.get("feels_like", 0),
                    "min": main.get("temp_min", 0),
                    "max": main.get("temp_max", 0)
                },
                "humidity": main.get("humidity", 0),
                "precipitation": precipitation,
                "wind": {
                    "speed": wind.get("speed", 0),
                    "direction": wind.get("deg", 0),
                    "gust": wind.get("gust", 0)
                },
                "pressure": main.get("pressure", 0),
                "visibility": data.get("visibility", 0) / 1000 if data.get("visibility") else 0
            }
        except Exception as e:
            print(f"Error processing current weather data: {e}")
            return {}
            
    def process_forecast(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process forecast data into daily summaries.
        
        Args:
            data: Raw forecast data from API
            
        Returns:
            List of daily weather summaries
        """
        try:
            forecast_list = data.get("list", [])
            daily_data = {}
            
            for item in forecast_list:
                dt = datetime.fromtimestamp(item.get("dt", 0), tz=timezone.utc)
                date_key = dt.date()
                
                if date_key not in daily_data:
                    daily_data[date_key] = {
                        "date": date_key,
                        "temperatures": [],
                        "humidity_values": [],
                        "precipitation": 0,
                        "wind_speeds": [],
                        "wind_directions": [],
                        "descriptions": [],
                        "pressure_values": []
                    }
                
                main = item.get("main", {})
                weather = item.get("weather", [{}])[0]
                wind = item.get("wind", {})
                rain = item.get("rain", {})
                snow = item.get("snow", {})
                
                daily_data[date_key]["temperatures"].append(main.get("temp", 0))
                daily_data[date_key]["humidity_values"].append(main.get("humidity", 0))
                daily_data[date_key]["wind_speeds"].append(wind.get("speed", 0))
                daily_data[date_key]["wind_directions"].append(wind.get("deg", 0))
                daily_data[date_key]["descriptions"].append(weather.get("description", ""))
                daily_data[date_key]["pressure_values"].append(main.get("pressure", 0))
                
                # Add precipitation
                precip = 0
                if rain.get("3h"):
                    precip += rain["3h"]
                if snow.get("3h"):
                    precip += snow["3h"]
                daily_data[date_key]["precipitation"] += precip
            
            # Process daily summaries
            daily_summaries = []
            for date_key in sorted(daily_data.keys()):
                day = daily_data[date_key]
                temps = day["temperatures"]
                
                # Get most common weather description
                descriptions = day["descriptions"]
                most_common_desc = max(set(descriptions), key=descriptions.count) if descriptions else "Unknown"
                
                summary = {
                    "date": date_key,
                    "description": most_common_desc.title(),
                    "temperature": {
                        "min": min(temps) if temps else 0,
                        "max": max(temps) if temps else 0,
                        "avg": sum(temps) / len(