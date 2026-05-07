```python
#!/usr/bin/env python3
"""
Weather Forecast Script

This module fetches current weather and 7-day forecast data from the OpenWeatherMap API
for a specified location. It retrieves temperature, humidity, precipitation, and wind
conditions and displays them in a formatted output.

Requirements:
- OpenWeatherMap API key (set as environment variable OPENWEATHER_API_KEY)
- httpx library for HTTP requests
- Standard library modules: os, json, datetime

Usage:
    python script.py

The script will prompt for a location and display current weather plus 7-day forecast.
"""

import os
import json
import sys
from datetime import datetime, timezone
try:
    import httpx
except ImportError:
    print("Error: httpx library not found. Install with: pip install httpx")
    sys.exit(1)


class WeatherFetcher:
    """Handles weather data retrieval from OpenWeatherMap API."""
    
    BASE_URL = "https://api.openweathermap.org/data/2.5"
    
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        if not self.api_key:
            raise ValueError("OpenWeatherMap API key not found. Set OPENWEATHER_API_KEY environment variable.")
    
    def get_coordinates(self, location):
        """Get latitude and longitude for a location using geocoding API."""
        try:
            url = f"http://api.openweathermap.org/geo/1.0/direct"
            params = {
                'q': location,
                'limit': 1,
                'appid': self.api_key
            }
            
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                
            data = response.json()
            if not data:
                raise ValueError(f"Location '{location}' not found")
                
            return data[0]['lat'], data[0]['lon'], data[0]['name']
        except httpx.RequestError as e:
            raise ConnectionError(f"Network error while fetching coordinates: {e}")
        except (KeyError, IndexError) as e:
            raise ValueError(f"Invalid response format for location lookup: {e}")
    
    def get_current_weather(self, lat, lon):
        """Fetch current weather data."""
        try:
            url = f"{self.BASE_URL}/weather"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                
            return response.json()
        except httpx.RequestError as e:
            raise ConnectionError(f"Network error while fetching current weather: {e}")
    
    def get_forecast(self, lat, lon):
        """Fetch 7-day weather forecast."""
        try:
            url = f"{self.BASE_URL}/onecall"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric',
                'exclude': 'minutely,alerts'
            }
            
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                
            return response.json()
        except httpx.RequestError as e:
            raise ConnectionError(f"Network error while fetching forecast: {e}")


def format_current_weather(data, location_name):
    """Format current weather data for display."""
    try:
        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        humidity = data['main']['humidity']
        description = data['weather'][0]['description'].title()
        wind_speed = data['wind']['speed']
        wind_direction = data['wind'].get('deg', 'N/A')
        
        # Convert wind direction from degrees to cardinal direction
        if wind_direction != 'N/A':
            directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                         'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
            wind_dir_text = directions[int((wind_direction + 11.25) / 22.5) % 16]
        else:
            wind_dir_text = 'N/A'
        
        print(f"\n{'='*50}")
        print(f"CURRENT WEATHER FOR {location_name.upper()}")
        print(f"{'='*50}")
        print(f"Temperature: {temp:.1f}°C (feels like {feels_like:.1f}°C)")
        print(f"Condition: {description}")
        print(f"Humidity: {humidity}%")
        print(f"Wind: {wind_speed:.1f} m/s {wind_dir_text}")
        
        if 'rain' in data:
            rain_1h = data['rain'].get('1h', 0)
            print(f"Precipitation (1h): {rain_1h:.1f} mm")
        elif 'snow' in data:
            snow_1h = data['snow'].get('1h', 0)
            print(f"Snow (1h): {snow_1h:.1f} mm")
        else:
            print("Precipitation: None")
            
    except KeyError as e:
        print(f"Error formatting current weather data: Missing key {e}")


def format_forecast(data):
    """Format 7-day forecast data for display."""
    try:
        print(f"\n{'='*50}")
        print("7-DAY WEATHER FORECAST")
        print(f"{'='*50}")
        
        for i, day in enumerate(data['daily'][:7]):
            date = datetime.fromtimestamp(day['dt'], tz=timezone.utc)
            day_name = date.strftime('%A, %B %d')
            
            temp_max = day['temp']['max']
            temp_min = day['temp']['min']
            description = day['weather'][0]['description'].title()
            humidity = day['humidity']
            wind_speed = day['wind_speed']
            
            # Precipitation
            rain = day.get('rain', {}).get('1h', 0) if 'rain' in day else 0
            snow = day.get('snow', {}).get('1h', 0) if 'snow' in day else 0
            precipitation = rain + snow
            
            print(f"\n{day_name}")
            print(f"  Temperature: {temp_min:.1f}°C - {temp_max:.1f}°C")
            print(f"  Condition: {description}")
            print(f"  Humidity: {humidity}%")
            print(f"  Wind: {wind_speed:.1f} m/s")
            print(f"  Precipitation: {precipitation:.1f} mm")
            
    except KeyError as e:
        print(f"Error formatting forecast data: Missing key {e}")


def main():
    """Main function to orchestrate weather data fetching and display."""
    try:
        # Initialize weather fetcher
        weather = WeatherFetcher()
        
        # Get location from user input
        location = input("Enter location (city, country): ").strip()
        if not location:
            print("Error: Location cannot be empty")
            return
        
        print(f"Fetching weather data for {location}...")
        
        # Get coordinates
        lat, lon, location_name = weather.get_coordinates(location)
        
        # Get current weather
        current_data = weather.get_current_weather(lat, lon)
        format_current_weather(current_data, location_name)
        
        # Get forecast
        forecast_data = weather.get_forecast(lat, lon)
        format_forecast(forecast_data)