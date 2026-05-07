#!/usr/bin/env python3
"""
Weather Data Fetcher

This module fetches weather data from the OpenWeatherMap API, including current
weather conditions and a 5-day forecast. It parses the temperature, weather
conditions, and forecast data, storing everything in a structured JSON format.

The script requires an OpenWeatherMap API key to be set as an environment variable
'OPENWEATHER_API_KEY' or hardcoded in the script.

Usage:
    python script.py

Dependencies:
    - httpx (for HTTP requests)
    - json (standard library)
    - os (standard library)
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any

try:
    import httpx
except ImportError:
    print("Error: httpx is required. Install with: pip install httpx")
    sys.exit(1)


class WeatherFetcher:
    """Fetches and processes weather data from OpenWeatherMap API."""
    
    def __init__(self, api_key: str = None, city: str = "London"):
        """
        Initialize the weather fetcher.
        
        Args:
            api_key: OpenWeatherMap API key
            city: City name for weather data
        """
        self.api_key = api_key or os.getenv('OPENWEATHER_API_KEY')
        self.city = city
        self.base_url = "https://api.openweathermap.org/data/2.5"
        
        if not self.api_key:
            raise ValueError("API key is required. Set OPENWEATHER_API_KEY environment variable.")
    
    def fetch_current_weather(self) -> Dict[str, Any]:
        """
        Fetch current weather data.
        
        Returns:
            Dictionary containing current weather data
        """
        url = f"{self.base_url}/weather"
        params = {
            'q': self.city,
            'appid': self.api_key,
            'units': 'metric'
        }
        
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                return response.json()
        except httpx.RequestError as e:
            raise Exception(f"Request failed: {e}")
        except httpx.HTTPStatusError as e:
            raise Exception(f"HTTP error {e.response.status_code}: {e.response.text}")
    
    def fetch_forecast(self) -> Dict[str, Any]:
        """
        Fetch 5-day weather forecast.
        
        Returns:
            Dictionary containing forecast data
        """
        url = f"{self.base_url}/forecast"
        params = {
            'q': self.city,
            'appid': self.api_key,
            'units': 'metric'
        }
        
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                return response.json()
        except httpx.RequestError as e:
            raise Exception(f"Request failed: {e}")
        except httpx.HTTPStatusError as e:
            raise Exception(f"HTTP error {e.response.status_code}: {e.response.text}")
    
    def parse_current_weather(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse current weather data into structured format.
        
        Args:
            data: Raw weather data from API
            
        Returns:
            Structured weather data
        """
        return {
            'location': {
                'city': data['name'],
                'country': data['sys']['country'],
                'coordinates': {
                    'lat': data['coord']['lat'],
                    'lon': data['coord']['lon']
                }
            },
            'current': {
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'weather': {
                    'main': data['weather'][0]['main'],
                    'description': data['weather'][0]['description'],
                    'icon': data['weather'][0]['icon']
                },
                'wind': {
                    'speed': data['wind'].get('speed', 0),
                    'direction': data['wind'].get('deg', 0)
                },
                'visibility': data.get('visibility', 0),
                'timestamp': datetime.fromtimestamp(data['dt']).isoformat()
            }
        }
    
    def parse_forecast(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse 5-day forecast data into structured format.
        
        Args:
            data: Raw forecast data from API
            
        Returns:
            List of structured forecast entries
        """
        forecast_list = []
        
        for item in data['list']:
            forecast_entry = {
                'datetime': datetime.fromtimestamp(item['dt']).isoformat(),
                'temperature': {
                    'temp': item['main']['temp'],
                    'feels_like': item['main']['feels_like'],
                    'temp_min': item['main']['temp_min'],
                    'temp_max': item['main']['temp_max']
                },
                'weather': {
                    'main': item['weather'][0]['main'],
                    'description': item['weather'][0]['description'],
                    'icon': item['weather'][0]['icon']
                },
                'humidity': item['main']['humidity'],
                'pressure': item['main']['pressure'],
                'wind': {
                    'speed': item['wind'].get('speed', 0),
                    'direction': item['wind'].get('deg', 0)
                },
                'probability_of_precipitation': item.get('pop', 0)
            }
            forecast_list.append(forecast_entry)
        
        return forecast_list
    
    def get_weather_data(self) -> Dict[str, Any]:
        """
        Fetch and parse all weather data.
        
        Returns:
            Complete structured weather data
        """
        try:
            # Fetch current weather
            current_data = self.fetch_current_weather()
            parsed_current = self.parse_current_weather(current_data)
            
            # Fetch forecast
            forecast_data = self.fetch_forecast()
            parsed_forecast = self.parse_forecast(forecast_data)
            
            return {
                'location': parsed_current['location'],
                'current_weather': parsed_current['current'],
                'forecast': parsed_forecast,
                'fetched_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Failed to fetch weather data: {e}")


def main():
    """Main function to run the weather fetcher."""
    try:
        # You can set your API key here or use environment variable
        api_key = "your_api_key_here"  # Replace with your actual API key
        city = "London"  # Change this to your desired city
        
        # Create weather fetcher instance
        weather_fetcher = WeatherFetcher(api_key=api_key, city=city)
        
        # Fetch weather data
        weather_data = weather_fetcher.get_weather_data()
        
        # Print results to stdout
        print(json.dumps(weather_data, indent=2, ensure_ascii=False))
        
    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error fetching weather data: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()