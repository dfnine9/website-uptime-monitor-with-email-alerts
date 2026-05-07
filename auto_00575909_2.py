```python
"""
Email Weather System Module

A self-contained email formatting and delivery system that fetches weather data,
generates personalized recommendations, and sends formatted HTML emails via SMTP.

Features:
- Fetches weather data from OpenWeatherMap API
- Generates AI-powered weather recommendations using Anthropic Claude
- Templates data into responsive HTML email format
- Integrates with SMTP services (Gmail, Outlook, custom)
- Comprehensive error handling for API failures and email delivery issues
- Configurable email templates and SMTP settings

Usage:
    python script.py

Requirements:
    - httpx: HTTP client for API requests
    - anthropic: AI recommendations (optional, falls back to static recommendations)
    - Standard library modules: smtplib, email, json, os
"""

import smtplib
import json
import os
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from email.mime.base import MimeBase
from email import encoders
from datetime import datetime, timedelta
import time

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    print("Warning: httpx not available. Using mock data.")

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("Warning: anthropic not available. Using static recommendations.")


class WeatherEmailSystem:
    """Main weather email system class."""
    
    def __init__(self):
        """Initialize the weather email system."""
        # Configuration
        self.weather_api_key = os.getenv('OPENWEATHER_API_KEY', 'demo_key')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY', '')
        
        # SMTP Configuration
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.email_user = os.getenv('EMAIL_USER', 'sender@example.com')
        self.email_password = os.getenv('EMAIL_PASSWORD', 'password')
        
        # Initialize clients
        if HTTPX_AVAILABLE:
            self.http_client = httpx.Client(timeout=10.0)
        
        if ANTHROPIC_AVAILABLE and self.anthropic_api_key:
            self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_api_key)
        else:
            self.anthropic_client = None
    
    def fetch_weather_data(self, city="London", country_code="GB"):
        """
        Fetch weather data from OpenWeatherMap API.
        
        Args:
            city (str): City name
            country_code (str): Country code (e.g., "GB", "US")
            
        Returns:
            dict: Weather data or mock data if API unavailable
        """
        if not HTTPX_AVAILABLE or self.weather_api_key == 'demo_key':
            print("Using mock weather data")
            return self._get_mock_weather_data(city)
        
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': f"{city},{country_code}",
                'appid': self.weather_api_key,
                'units': 'metric'
            }
            
            response = self.http_client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            print(f"Successfully fetched weather data for {city}")
            return self._parse_weather_data(data)
            
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            print("Falling back to mock data")
            return self._get_mock_weather_data(city)
    
    def _get_mock_weather_data(self, city):
        """Generate mock weather data for testing."""
        return {
            'city': city,
            'country': 'GB',
            'temperature': 18,
            'feels_like': 16,
            'humidity': 65,
            'pressure': 1013,
            'description': 'partly cloudy',
            'wind_speed': 12,
            'wind_direction': 'NW',
            'visibility': 10,
            'uv_index': 5,
            'timestamp': datetime.now().isoformat()
        }
    
    def _parse_weather_data(self, data):
        """Parse OpenWeatherMap API response."""
        try:
            return {
                'city': data['name'],
                'country': data['sys']['country'],
                'temperature': round(data['main']['temp']),
                'feels_like': round(data['main']['feels_like']),
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'description': data['weather'][0]['description'].title(),
                'wind_speed': round(data['wind']['speed'] * 3.6),  # Convert m/s to km/h
                'wind_direction': self._wind_direction(data['wind'].get('deg', 0)),
                'visibility': data.get('visibility', 10000) // 1000,  # Convert m to km
                'uv_index': 5,  # Mock UV index (not in basic API)
                'timestamp': datetime.now().isoformat()
            }
        except KeyError as e:
            print(f"Error parsing weather data: missing key {e}")
            return self._get_mock_weather_data(data.get('name', 'Unknown'))
    
    def _wind_direction(self, degrees):
        """Convert wind direction degrees to compass direction."""
        directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                     "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
        index = round(degrees / 22.5) % 16
        return directions[index]
    
    def generate_recommendations(self, weather_data):
        """
        Generate weather-based recommendations using AI or fallback logic.
        
        Args:
            weather_data (dict): Weather information
            
        Returns:
            dict: Recommendations for clothing, activities, and alerts
        """
        if self.anthropic_client:
            return self._generate_ai_recommendations(weather_data)
        else:
            return self._generate_static_recommendations(weather_data)
    
    def _generate_ai_recommendations(self, weather_data):
        """Generate recommendations using Anthropic Claude."""
        try:
            prompt = f"""
            Based on the following weather data, provide practical recommendations:
            
            City: {weather_data['city']}
            Temperature: {weather_data['temperature']}°C (feels like {weather_data['feels_like']}°C)
            Conditions: {weather_data['description']}
            Humidity: {weather_data['humidity']}%
            Wind: {weather_data['wind_speed']} km/h {weather_data['wind_direction']}
            
            Please provide:
            1. Clothing recommendations
            2. Activity suggestions
            3. Any weather alerts or precautions
            
            Keep recommendations practical and concise.
            """
            
            message = self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            
            recommendations_text = message.content[0].text
            return self._parse_ai_recommendations(recommendations_text)
            
        except Exception as e:
            print(f"Error generating AI recommendations: {e}")
            return self._generate_static_recommendations(weather_data)
    
    def _parse_ai_recommendations(self, text):
        """Parse AI-generated recommendations into structured format."""
        lines = text.strip().split('\n')
        
        clothing = []
        activities = []
        alerts = []
        
        current_section = None
        
        for line in lines:
            line =