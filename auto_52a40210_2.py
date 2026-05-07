```python
"""
Weather Report Generator with Clothing Recommendations

This module fetches weather data and generates formatted HTML email templates
with daily overviews, hourly breakdowns, and outfit suggestions based on
temperature and weather conditions.

Dependencies: httpx (for HTTP requests)
Usage: python script.py
"""

import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional

try:
    import httpx
except ImportError:
    print("Error: httpx is required but not installed. Install with: pip install httpx")
    sys.exit(1)


class WeatherReportGenerator:
    def __init__(self):
        self.weather_api_base = "https://api.open-meteo.com/v1/forecast"
        
    def get_clothing_recommendation(self, temp_celsius: float, weather_code: int) -> Dict[str, str]:
        """Generate clothing recommendations based on temperature and weather conditions."""
        
        # Weather code mapping (simplified)
        precipitation_codes = {0, 1, 2, 3, 45, 48, 51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 71, 73, 75, 77, 80, 81, 82, 85, 86, 95, 96, 99}
        
        temp_f = (temp_celsius * 9/5) + 32
        
        # Base clothing recommendations by temperature
        if temp_f >= 80:
            base_outfit = "Light cotton t-shirt, shorts, sandals"
            accessories = "Sunglasses, hat"
        elif temp_f >= 70:
            base_outfit = "Light shirt, pants or shorts, comfortable shoes"
            accessories = "Light jacket (optional)"
        elif temp_f >= 60:
            base_outfit = "Long-sleeve shirt, pants, closed shoes"
            accessories = "Light sweater or cardigan"
        elif temp_f >= 50:
            base_outfit = "Sweater, pants, closed shoes"
            accessories = "Light jacket or coat"
        elif temp_f >= 40:
            base_outfit = "Warm sweater, pants, boots"
            accessories = "Jacket or coat, scarf"
        elif temp_f >= 30:
            base_outfit = "Heavy sweater, warm pants, insulated boots"
            accessories = "Winter coat, hat, gloves"
        else:
            base_outfit = "Multiple layers, thermal underwear, winter boots"
            accessories = "Heavy winter coat, warm hat, insulated gloves"
        
        # Adjust for precipitation
        if weather_code in precipitation_codes:
            accessories += ", umbrella or rain jacket"
            
        return {
            "outfit": base_outfit,
            "accessories": accessories,
            "temperature": f"{temp_f:.1f}°F ({temp_celsius:.1f}°C)"
        }
    
    def get_weather_description(self, weather_code: int) -> str:
        """Convert weather code to human-readable description."""
        weather_descriptions = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Fog",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            71: "Slight snow",
            73: "Moderate snow",
            75: "Heavy snow",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            95: "Thunderstorm"
        }
        return weather_descriptions.get(weather_code, "Unknown weather condition")
    
    def fetch_weather_data(self, latitude: float = 40.7128, longitude: float = -74.0060) -> Optional[Dict]:
        """Fetch weather data from Open-Meteo API. Defaults to NYC coordinates."""
        
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": "temperature_2m,weather_code,precipitation_probability",
            "daily": "temperature_2m_max,temperature_2m_min,weather_code",
            "timezone": "auto",
            "forecast_days": 1
        }
        
        try:
            with httpx.Client() as client:
                response = client.get(self.weather_api_base, params=params, timeout=10.0)
                response.raise_for_status()
                return response.json()
        except httpx.RequestError as e:
            print(f"Error fetching weather data: {e}")
            return None
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e}")
            return None
    
    def generate_html_report(self, weather_data: Dict, location_name: str = "New York City") -> str:
        """Generate HTML email template with weather and clothing recommendations."""
        
        if not weather_data:
            return "<html><body><h1>Error: Unable to fetch weather data</h1></body></html>"
        
        try:
            daily_data = weather_data["daily"]
            hourly_data = weather_data["hourly"]
            
            # Get today's data
            today_date = datetime.now().strftime("%Y-%m-%d")
            max_temp = daily_data["temperature_2m_max"][0]
            min_temp = daily_data["temperature_2m_min"][0]
            daily_weather_code = daily_data["weather_code"][0]
            
            # Get current hour index (approximate)
            current_hour = datetime.now().hour
            
            # Generate daily overview
            daily_recommendation = self.get_clothing_recommendation(
                (max_temp + min_temp) / 2, daily_weather_code
            )
            weather_desc = self.get_weather_description(daily_weather_code)
            
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Weather & Outfit Report - {today_date}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .section {{
            margin: 25px 0;
            padding: 20px;
            border-left: 4px solid #4CAF50;
            background-color: #f9f9f9;
        }}
        .hourly-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        .hourly-item {{
            background-color: white;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #ddd;
            text-align: center;
        }}
        .temp-high {{ color: #e74c3c; font-weight: bold; }}
        .temp-low {{ color: #3498db; font-weight: bold; }}
        .outfit-item {{ 
            background-color: #e8f5e8;
            padding: 10px;
            margin: 8px 0;
            border-radius: