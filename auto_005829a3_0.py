```python
"""
Weather Data Fetcher

This module fetches current weather data from the OpenWeatherMap API and parses
key meteorological information including temperature, precipitation probability,
wind speed, and weather conditions into structured variables.

The script uses the OpenWeatherMap Current Weather API to retrieve real-time
weather data for a specified location and outputs the parsed results to stdout.

Dependencies:
- httpx: For making HTTP requests to the API
- json: For parsing API responses (standard library)
- sys: For error handling and exit codes (standard library)

Usage:
    python script.py

Note: Requires a valid OpenWeatherMap API key. Sign up at https://openweathermap.org/api
"""

import json
import sys
try:
    import httpx
except ImportError:
    print("Error: httpx library not found. Install with: pip install httpx")
    sys.exit(1)


class WeatherFetcher:
    """Handles weather data retrieval and parsing from OpenWeatherMap API."""
    
    def __init__(self, api_key: str, city: str = "London", units: str = "metric"):
        """
        Initialize the weather fetcher.
        
        Args:
            api_key (str): OpenWeatherMap API key
            city (str): City name to fetch weather for
            units (str): Temperature units (metric, imperial, kelvin)
        """
        self.api_key = api_key
        self.city = city
        self.units = units
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
    
    def fetch_weather_data(self):
        """
        Fetch weather data from OpenWeatherMap API.
        
        Returns:
            dict: Parsed weather data with structured variables
        """
        params = {
            'q': self.city,
            'appid': self.api_key,
            'units': self.units
        }
        
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(self.base_url, params=params)
                response.raise_for_status()
                
                raw_data = response.json()
                return self._parse_weather_data(raw_data)
                
        except httpx.TimeoutException:
            raise Exception("Request timeout - API server not responding")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise Exception("Invalid API key")
            elif e.response.status_code == 404:
                raise Exception(f"City '{self.city}' not found")
            else:
                raise Exception(f"HTTP error {e.response.status_code}: {e.response.text}")
        except httpx.RequestError as e:
            raise Exception(f"Network error: {str(e)}")
        except json.JSONDecodeError:
            raise Exception("Invalid JSON response from API")
    
    def _parse_weather_data(self, raw_data: dict):
        """
        Parse raw API response into structured weather variables.
        
        Args:
            raw_data (dict): Raw JSON response from API
            
        Returns:
            dict: Structured weather data
        """
        try:
            # Extract temperature data
            temp_data = raw_data.get('main', {})
            temperature = temp_data.get('temp')
            feels_like = temp_data.get('feels_like')
            temp_min = temp_data.get('temp_min')
            temp_max = temp_data.get('temp_max')
            humidity = temp_data.get('humidity')
            
            # Extract wind data
            wind_data = raw_data.get('wind', {})
            wind_speed = wind_data.get('speed', 0)
            wind_direction = wind_data.get('deg')
            
            # Extract weather conditions
            weather_list = raw_data.get('weather', [])
            weather_main = weather_list[0].get('main', 'Unknown') if weather_list else 'Unknown'
            weather_description = weather_list[0].get('description', 'No description') if weather_list else 'No description'
            
            # Extract precipitation probability (note: current weather API doesn't include this)
            # For current weather, we can check for rain/snow in last 3h
            rain_data = raw_data.get('rain', {})
            snow_data = raw_data.get('snow', {})
            precipitation_1h = rain_data.get('1h', 0) + snow_data.get('1h', 0)
            precipitation_3h = rain_data.get('3h', 0) + snow_data.get('3h', 0)
            
            # Cloud coverage as proxy for precipitation probability
            clouds = raw_data.get('clouds', {}).get('all', 0)
            
            # Additional data
            pressure = temp_data.get('pressure')
            visibility = raw_data.get('visibility', 0) / 1000 if raw_data.get('visibility') else None  # Convert to km
            
            return {
                'city': raw_data.get('name', self.city),
                'country': raw_data.get('sys', {}).get('country', 'Unknown'),
                'temperature': temperature,
                'feels_like': feels_like,
                'temp_min': temp_min,
                'temp_max': temp_max,
                'humidity': humidity,
                'pressure': pressure,
                'wind_speed': wind_speed,
                'wind_direction': wind_direction,
                'weather_condition': weather_main,
                'weather_description': weather_description,
                'precipitation_1h': precipitation_1h,
                'precipitation_3h': precipitation_3h,
                'cloud_coverage': clouds,
                'visibility_km': visibility,
                'units': self.units
            }
            
        except (KeyError, IndexError, TypeError) as e:
            raise Exception(f"Error parsing weather data: {str(e)}")


def print_weather_report(weather_data: dict):
    """
    Print formatted weather report to stdout.
    
    Args:
        weather_data (dict): Structured weather data
    """
    units_symbol = "°C" if weather_data['units'] == 'metric' else "°F" if weather_data['units'] == 'imperial' else "K"
    speed_unit = "m/s" if weather_data['units'] == 'metric' else "mph" if weather_data['units'] == 'imperial' else "m/s"
    
    print("=" * 50)
    print(f"WEATHER REPORT FOR {weather_data['city'].upper()}, {weather_data['country']}")
    print("=" * 50)
    print()
    
    print("TEMPERATURE:")
    print(f"  Current: {weather_data['temperature']}{units_symbol}")
    print(f"  Feels like: {weather_data['feels_like']}{units_symbol}")
    print(f"  Min/Max: {weather_data['temp_min']}{units_symbol} / {weather_data['temp_max']}{units_symbol}")
    print()
    
    print("WEATHER CONDITIONS:")
    print(f"  Condition: {weather_data['weather_condition']}")
    print(f"  Description: {weather_data['weather_description'].title()}")
    print(f"  Cloud coverage: {weather_data['cloud_coverage']}%")
    print()
    
    print("WIND:")
    print(f"  Speed: {weather_data['wind_speed']} {speed_unit}")
    if weather_data['wind_direction'] is not None:
        print(f"  Direction: {weather_data['wind_direction']}°")
    print()
    
    print("PRECIPITATION:")
    print(f"  Last 1 hour: {weather_data['precipitation_1h']} mm")
    print(f"  Last 3 hours: {weather_data['precipitation_3h']} mm")
    print()
    
    print("OTHER:")
    print(f"  Humidity: {weather_data['humidity']}%")
    print(f"  Pressure: {weather_data['pressure']} hPa")
    if weather_data['visibility_km'] is not None:
        print(f"