```python
"""
Weather Data Fetcher

This module fetches current weather data from the OpenWeatherMap API and parses
key meteorological metrics including temperature, precipitation, and wind conditions.

The script uses only standard library modules plus httpx for HTTP requests.
It includes comprehensive error handling and outputs formatted weather data to stdout.

Usage: python script.py

Note: You'll need to set your OpenWeatherMap API key in the API_KEY variable below.
Get a free API key at: https://openweathermap.org/api
"""

import json
import sys
from typing import Dict, Any, Optional

try:
    import httpx
except ImportError:
    print("Error: httpx library is required. Install with: pip install httpx")
    sys.exit(1)


class WeatherFetcher:
    """Fetches and parses weather data from OpenWeatherMap API."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        
    def fetch_weather_data(self, city: str, units: str = "metric") -> Optional[Dict[str, Any]]:
        """
        Fetch weather data for a given city.
        
        Args:
            city: Name of the city
            units: Temperature units ('metric', 'imperial', 'kelvin')
            
        Returns:
            Dictionary containing weather data or None if error
        """
        params = {
            'q': city,
            'appid': self.api_key,
            'units': units
        }
        
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(self.base_url, params=params)
                response.raise_for_status()
                return response.json()
                
        except httpx.TimeoutException:
            print(f"Error: Request timed out while fetching weather data for {city}")
            return None
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                print("Error: Invalid API key. Please check your OpenWeatherMap API key.")
            elif e.response.status_code == 404:
                print(f"Error: City '{city}' not found.")
            else:
                print(f"Error: HTTP {e.response.status_code} - {e.response.text}")
            return None
        except httpx.RequestError as e:
            print(f"Error: Network error occurred - {e}")
            return None
        except json.JSONDecodeError:
            print("Error: Invalid JSON response from API")
            return None
        except Exception as e:
            print(f"Error: Unexpected error occurred - {e}")
            return None
    
    def parse_weather_metrics(self, weather_data: Dict[str, Any], units: str = "metric") -> Dict[str, Any]:
        """
        Parse key weather metrics from API response.
        
        Args:
            weather_data: Raw weather data from API
            units: Temperature units used in the request
            
        Returns:
            Dictionary with parsed metrics
        """
        try:
            # Temperature metrics
            temp_unit = "°C" if units == "metric" else "°F" if units == "imperial" else "K"
            temperature = {
                'current': weather_data['main']['temp'],
                'feels_like': weather_data['main']['feels_like'],
                'min': weather_data['main']['temp_min'],
                'max': weather_data['main']['temp_max'],
                'unit': temp_unit
            }
            
            # Precipitation metrics
            precipitation = {
                'rain_1h': weather_data.get('rain', {}).get('1h', 0),
                'rain_3h': weather_data.get('rain', {}).get('3h', 0),
                'snow_1h': weather_data.get('snow', {}).get('1h', 0),
                'snow_3h': weather_data.get('snow', {}).get('3h', 0),
                'unit': 'mm'
            }
            
            # Wind metrics
            wind_unit = "m/s" if units == "metric" else "mph"
            wind = {
                'speed': weather_data.get('wind', {}).get('speed', 0),
                'direction': weather_data.get('wind', {}).get('deg', 0),
                'gust': weather_data.get('wind', {}).get('gust', 0),
                'unit': wind_unit
            }
            
            # Additional metrics
            additional = {
                'humidity': weather_data['main']['humidity'],
                'pressure': weather_data['main']['pressure'],
                'visibility': weather_data.get('visibility', 0) / 1000,  # Convert to km
                'cloudiness': weather_data.get('clouds', {}).get('all', 0),
                'description': weather_data['weather'][0]['description'].title()
            }
            
            return {
                'location': f"{weather_data['name']}, {weather_data['sys']['country']}",
                'temperature': temperature,
                'precipitation': precipitation,
                'wind': wind,
                'additional': additional
            }
            
        except KeyError as e:
            print(f"Error: Missing expected data field in API response - {e}")
            return {}
        except Exception as e:
            print(f"Error: Failed to parse weather metrics - {e}")
            return {}
    
    def format_output(self, metrics: Dict[str, Any]) -> str:
        """Format weather metrics for console output."""
        if not metrics:
            return "No weather data available to display."
        
        output = []
        output.append("=" * 50)
        output.append(f"WEATHER REPORT: {metrics['location']}")
        output.append("=" * 50)
        
        # Temperature
        temp = metrics['temperature']
        output.append(f"\n🌡️  TEMPERATURE:")
        output.append(f"   Current: {temp['current']}{temp['unit']}")
        output.append(f"   Feels like: {temp['feels_like']}{temp['unit']}")
        output.append(f"   Range: {temp['min']}{temp['unit']} - {temp['max']}{temp['unit']}")
        
        # Weather description
        output.append(f"\n☁️  CONDITIONS: {metrics['additional']['description']}")
        
        # Precipitation
        precip = metrics['precipitation']
        output.append(f"\n🌧️  PRECIPITATION:")
        if precip['rain_1h'] > 0 or precip['rain_3h'] > 0:
            if precip['rain_1h'] > 0:
                output.append(f"   Rain (1h): {precip['rain_1h']} {precip['unit']}")
            if precip['rain_3h'] > 0:
                output.append(f"   Rain (3h): {precip['rain_3h']} {precip['unit']}")
        elif precip['snow_1h'] > 0 or precip['snow_3h'] > 0:
            if precip['snow_1h'] > 0:
                output.append(f"   Snow (1h): {precip['snow_1h']} {precip['unit']}")
            if precip['snow_3h'] > 0:
                output.append(f"   Snow (3h): {precip['snow_3h']} {precip['unit']}")
        else:
            output.append("   None")
        
        # Wind
        wind = metrics['wind']
        output.append(f"\n💨 WIND:")
        output.append(f"   Speed: {wind['speed']} {wind['unit']}")
        output.append(f"   Direction: {wind['direction']}°")
        if wind['gust'] > 0:
            output.append(f"   Gusts: {wind['gust']} {wind['unit']}")
        
        # Additional metrics
        add = metrics['additional']
        output.append(f"\n📊 ADDITIONAL:")
        output.append(f"   Humidity: {add['humidity']}%")
        output.append(f