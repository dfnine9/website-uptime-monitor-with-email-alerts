```python
"""
Email Formatting Module for Weather-Based Clothing Recommendations

This module creates HTML-formatted email templates that combine weather data
with clothing recommendations. It fetches current weather conditions and
generates visually appealing emails with weather icons and styling.

Features:
- Fetches real-time weather data from OpenWeatherMap API
- Generates clothing recommendations based on temperature and conditions
- Creates responsive HTML email templates with embedded CSS
- Includes weather icons and professional styling
- Error handling for API failures and data processing
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import httpx


class WeatherEmailFormatter:
    """Formats weather data and clothing recommendations into HTML emails."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with optional OpenWeatherMap API key."""
        self.api_key = api_key or "demo_key"
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        
    def get_weather_icon(self, condition: str, temp: float) -> str:
        """Return appropriate weather emoji based on condition and temperature."""
        condition_lower = condition.lower()
        
        if "rain" in condition_lower or "drizzle" in condition_lower:
            return "🌧️"
        elif "snow" in condition_lower:
            return "❄️"
        elif "cloud" in condition_lower:
            return "☁️"
        elif "clear" in condition_lower:
            return "☀️" if temp > 20 else "🌤️"
        elif "thunder" in condition_lower:
            return "⛈️"
        elif "mist" in condition_lower or "fog" in condition_lower:
            return "🌫️"
        else:
            return "🌤️"
    
    def get_clothing_recommendations(self, temp: float, condition: str, humidity: float) -> List[str]:
        """Generate clothing recommendations based on weather conditions."""
        recommendations = []
        condition_lower = condition.lower()
        
        # Temperature-based recommendations
        if temp < 0:
            recommendations.extend([
                "Heavy winter coat or parka",
                "Thermal underwear",
                "Warm boots with good grip",
                "Insulated gloves",
                "Warm hat covering ears",
                "Scarf or neck warmer"
            ])
        elif temp < 10:
            recommendations.extend([
                "Warm jacket or coat",
                "Long pants",
                "Closed-toe shoes",
                "Light gloves",
                "Beanie or warm hat"
            ])
        elif temp < 20:
            recommendations.extend([
                "Light jacket or sweater",
                "Long pants or jeans",
                "Comfortable walking shoes",
                "Light scarf (optional)"
            ])
        elif temp < 25:
            recommendations.extend([
                "Light shirt or blouse",
                "Light pants or skirt",
                "Comfortable shoes",
                "Light cardigan for indoors"
            ])
        else:
            recommendations.extend([
                "Light, breathable clothing",
                "Shorts or light pants",
                "Sandals or breathable shoes",
                "Sun hat",
                "Sunglasses"
            ])
        
        # Condition-based additions
        if "rain" in condition_lower or "drizzle" in condition_lower:
            recommendations.extend([
                "Waterproof jacket or raincoat",
                "Umbrella",
                "Water-resistant shoes"
            ])
        
        if "snow" in condition_lower:
            recommendations.extend([
                "Waterproof boots",
                "Extra warm layers"
            ])
        
        if humidity > 70:
            recommendations.append("Breathable, moisture-wicking fabrics")
        
        if "sun" in condition_lower or "clear" in condition_lower:
            recommendations.extend([
                "Sunscreen",
                "UV-protective clothing for extended outdoor time"
            ])
        
        return recommendations[:8]  # Limit to 8 recommendations
    
    async def fetch_weather_data(self, city: str) -> Dict:
        """Fetch weather data from OpenWeatherMap API."""
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "q": city,
                    "appid": self.api_key,
                    "units": "metric"
                }
                
                response = await client.get(self.base_url, params=params)
                
                if response.status_code == 401:
                    # Return mock data for demo purposes
                    return self.get_mock_weather_data(city)
                
                response.raise_for_status()
                return response.json()
                
        except httpx.RequestError as e:
            print(f"Network error fetching weather data: {e}")
            return self.get_mock_weather_data(city)
        except httpx.HTTPStatusError as e:
            print(f"HTTP error fetching weather data: {e}")
            return self.get_mock_weather_data(city)
        except Exception as e:
            print(f"Unexpected error fetching weather data: {e}")
            return self.get_mock_weather_data(city)
    
    def get_mock_weather_data(self, city: str) -> Dict:
        """Return mock weather data for demonstration."""
        return {
            "name": city,
            "main": {
                "temp": 18.5,
                "feels_like": 19.2,
                "humidity": 65,
                "pressure": 1013
            },
            "weather": [
                {
                    "main": "Clouds",
                    "description": "scattered clouds"
                }
            ],
            "wind": {
                "speed": 3.5
            },
            "visibility": 10000
        }
    
    def create_html_template(self, weather_data: Dict, recommendations: List[str]) -> str:
        """Create HTML email template with weather data and clothing recommendations."""
        city = weather_data.get("name", "Unknown City")
        temp = weather_data["main"]["temp"]
        feels_like = weather_data["main"]["feels_like"]
        humidity = weather_data["main"]["humidity"]
        condition = weather_data["weather"][0]["description"].title()
        weather_main = weather_data["weather"][0]["main"]
        wind_speed = weather_data.get("wind", {}).get("speed", 0)
        
        weather_icon = self.get_weather_icon(weather_main, temp)
        current_date = datetime.now().strftime("%B %d, %Y")
        
        recommendations_html = ""
        for i, rec in enumerate(recommendations, 1):
            recommendations_html += f"""
                <li style="margin: 8px 0; padding: 8px; background-color: #f8f9fa; border-radius: 5px; border-left: 3px solid #007bff;">
                    {rec}
                </li>
            """
        
        html_template = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Weather & Clothing Report - {city}</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%