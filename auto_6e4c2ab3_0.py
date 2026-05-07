```python
"""
Weather Data Fetcher and Severe Condition Parser

This module fetches current weather data from the OpenWeatherMap API,
identifies severe weather conditions (storms, high winds, extreme temperatures),
and stores the parsed data in a structured format.

Severe weather conditions detected:
- Thunderstorms, tornadoes, hurricanes
- Wind speeds > 25 mph (40 km/h)  
- Temperatures below 32°F (0°C) or above 100°F (38°C)
- Heavy rain, snow, or hail conditions

Usage:
    python script.py

Requirements:
    - OpenWeatherMap API key (set as environment variable OPENWEATHER_API_KEY)
    - httpx library for HTTP requests
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any

try:
    import httpx
except ImportError:
    print("Error: httpx library required. Install with: pip install httpx")
    sys.exit(1)


class WeatherDataFetcher:
    """Fetches and processes weather data from OpenWeatherMap API."""
    
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
    SEVERE_WIND_THRESHOLD = 25  # mph
    EXTREME_TEMP_LOW = 32  # °F
    EXTREME_TEMP_HIGH = 100  # °F
    
    SEVERE_CONDITIONS = {
        'thunderstorm', 'tornado', 'hurricane', 'typhoon', 'cyclone',
        'heavy rain', 'heavy snow', 'blizzard', 'hail', 'squall'
    }
    
    def __init__(self, api_key: str):
        """Initialize with OpenWeatherMap API key."""
        self.api_key = api_key
        self.client = httpx.Client(timeout=30.0)
    
    def fetch_weather_data(self, city: str = "New York", country_code: str = "US") -> Optional[Dict[str, Any]]:
        """
        Fetch weather data for specified location.
        
        Args:
            city: City name
            country_code: ISO country code
            
        Returns:
            Weather data dictionary or None if error
        """
        params = {
            'q': f"{city},{country_code}",
            'appid': self.api_key,
            'units': 'imperial'  # Fahrenheit and mph
        }
        
        try:
            response = self.client.get(self.BASE_URL, params=params)
            response.raise_for_status()
            return response.json()
        
        except httpx.HTTPStatusError as e:
            print(f"HTTP error fetching weather data: {e.response.status_code}")
            return None
        except httpx.RequestError as e:
            print(f"Request error: {e}")
            return None
        except json.JSONDecodeError:
            print("Error: Invalid JSON response from API")
            return None
    
    def parse_severe_conditions(self, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse weather data to identify severe conditions.
        
        Args:
            weather_data: Raw weather data from API
            
        Returns:
            Structured data with severe condition flags
        """
        if not weather_data:
            return {}
        
        # Extract key weather metrics
        main_data = weather_data.get('main', {})
        wind_data = weather_data.get('wind', {})
        weather_conditions = weather_data.get('weather', [])
        
        temp_f = main_data.get('temp', 0)
        wind_speed_mph = wind_data.get('speed', 0)
        
        # Check for severe conditions
        severe_flags = {
            'extreme_cold': temp_f < self.EXTREME_TEMP_LOW,
            'extreme_heat': temp_f > self.EXTREME_TEMP_HIGH,
            'high_winds': wind_speed_mph > self.SEVERE_WIND_THRESHOLD,
            'severe_weather': False,
            'weather_alerts': []
        }
        
        # Check weather condition descriptions
        for condition in weather_conditions:
            description = condition.get('description', '').lower()
            main_condition = condition.get('main', '').lower()
            
            if any(severe_cond in description or severe_cond in main_condition 
                   for severe_cond in self.SEVERE_CONDITIONS):
                severe_flags['severe_weather'] = True
                severe_flags['weather_alerts'].append(description)
        
        # Structure the complete data
        structured_data = {
            'location': {
                'city': weather_data.get('name', 'Unknown'),
                'country': weather_data.get('sys', {}).get('country', 'Unknown'),
                'coordinates': {
                    'lat': weather_data.get('coord', {}).get('lat'),
                    'lon': weather_data.get('coord', {}).get('lon')
                }
            },
            'timestamp': datetime.utcnow().isoformat(),
            'current_conditions': {
                'temperature_f': temp_f,
                'feels_like_f': main_data.get('feels_like', 0),
                'humidity_percent': main_data.get('humidity', 0),
                'pressure_hpa': main_data.get('pressure', 0),
                'wind_speed_mph': wind_speed_mph,
                'wind_direction_deg': wind_data.get('deg', 0),
                'visibility_meters': weather_data.get('visibility', 0),
                'weather_description': weather_conditions[0].get('description', 'Unknown') if weather_conditions else 'Unknown'
            },
            'severe_conditions': severe_flags,
            'risk_assessment': self._assess_risk_level(severe_flags, temp_f, wind_speed_mph)
        }
        
        return structured_data
    
    def _assess_risk_level(self, severe_flags: Dict[str, Any], temp_f: float, wind_speed_mph: float) -> str:
        """Assess overall weather risk level."""
        if severe_flags['severe_weather']:
            return 'HIGH'
        elif (severe_flags['extreme_cold'] or severe_flags['extreme_heat'] or 
              severe_flags['high_winds']):
            return 'MODERATE'
        elif temp_f < 40 or temp_f > 90 or wind_speed_mph > 15:
            return 'LOW'
        else:
            return 'MINIMAL'
    
    def close(self):
        """Close HTTP client."""
        self.client.close()


def main():
    """Main execution function."""
    # Get API key from environment
    api_key = os.getenv('OPENWEATHER_API_KEY')
    if not api_key:
        print("Error: OPENWEATHER_API_KEY environment variable not set")
        print("Get your free API key from: https://openweathermap.org/api")
        sys.exit(1)
    
    # Initialize weather fetcher
    weather_fetcher = WeatherDataFetcher(api_key)
    
    try:
        # Test cities with potentially severe weather
        test_locations = [
            ("New York", "US"),
            ("Miami", "US"), 
            ("Chicago", "US"),
            ("Phoenix", "US"),
            ("Anchorage", "US")
        ]
        
        all_weather_data = []
        
        for city, country in test_locations:
            print(f"\nFetching weather data for {city}, {country}...")
            
            # Fetch raw weather data
            raw_data = weather_fetcher.fetch_weather_data(city, country)
            if not raw_data:
                print(f"Failed to fetch data for {city}")
                continue
            
            # Parse severe conditions
            structured_data = weather_fetcher.parse_severe_conditions(raw_data)
            all_weather_data.append(structured_data)
            
            # Print results
            location = structured_data['location']
            conditions = structured_data['current_conditions'] 
            severe = structured_data['severe_conditions']