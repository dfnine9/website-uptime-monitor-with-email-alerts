```python
#!/usr/bin/env python3
"""
Daily Summary Email Automation Script

This script fetches data from various sources, generates HTML email summaries,
and sends them via SMTP. It includes data fetching capabilities, HTML template
generation, and email delivery functionality.

Dependencies: httpx, anthropic (beyond standard library)
Usage: python script.py
"""

import smtplib
import json
import asyncio
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from datetime import datetime, timedelta
from typing import Dict, List, Any
import os
import sys

try:
    import httpx
except ImportError:
    print("Error: httpx not installed. Run: pip install httpx")
    sys.exit(1)

class DataFetcher:
    """Handles fetching data from various sources"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def fetch_news(self) -> List[Dict[str, Any]]:
        """Fetch latest news headlines"""
        try:
            # Using NewsAPI free tier (requires API key)
            api_key = os.getenv('NEWS_API_KEY', 'demo')
            url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"
            
            response = await self.client.get(url)
            if response.status_code == 200:
                data = response.json()
                return data.get('articles', [])[:5]  # Top 5 articles
            else:
                return self._mock_news()
        except Exception as e:
            print(f"Error fetching news: {e}")
            return self._mock_news()
    
    def _mock_news(self) -> List[Dict[str, Any]]:
        """Return mock news data when API fails"""
        return [
            {
                "title": "Sample News Article 1",
                "description": "This is a sample news description for testing purposes.",
                "url": "https://example.com/news1",
                "publishedAt": datetime.now().isoformat()
            },
            {
                "title": "Sample News Article 2", 
                "description": "Another sample news description for the daily summary.",
                "url": "https://example.com/news2",
                "publishedAt": datetime.now().isoformat()
            }
        ]
    
    async def fetch_weather(self) -> Dict[str, Any]:
        """Fetch weather information"""
        try:
            # Using OpenWeatherMap API (requires API key)
            api_key = os.getenv('WEATHER_API_KEY', 'demo')
            city = os.getenv('WEATHER_CITY', 'New York')
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            
            response = await self.client.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                return self._mock_weather()
        except Exception as e:
            print(f"Error fetching weather: {e}")
            return self._mock_weather()
    
    def _mock_weather(self) -> Dict[str, Any]:
        """Return mock weather data when API fails"""
        return {
            "name": "Sample City",
            "main": {"temp": 22, "humidity": 65},
            "weather": [{"main": "Clear", "description": "clear sky"}],
            "wind": {"speed": 3.5}
        }
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

class HTMLTemplateGenerator:
    """Generates HTML email templates"""
    
    @staticmethod
    def generate_summary_email(news_data: List[Dict], weather_data: Dict) -> str:
        """Generate HTML email template with fetched data"""
        
        current_date = datetime.now().strftime("%B %d, %Y")
        
        # Generate news section
        news_html = ""
        for article in news_data:
            news_html += f"""
            <div style="margin-bottom: 20px; padding: 15px; border-left: 4px solid #007acc; background-color: #f8f9fa;">
                <h3 style="margin: 0 0 10px 0; color: #333;">
                    <a href="{article.get('url', '#')}" style="text-decoration: none; color: #007acc;">
                        {article.get('title', 'No Title')}
                    </a>
                </h3>
                <p style="margin: 0; color: #666; line-height: 1.5;">
                    {article.get('description', 'No description available')}
                </p>
                <small style="color: #999;">
                    Published: {article.get('publishedAt', 'Unknown')[:10]}
                </small>
            </div>
            """
        
        # Generate weather section
        temp = weather_data.get('main', {}).get('temp', 'N/A')
        humidity = weather_data.get('main', {}).get('humidity', 'N/A')
        description = weather_data.get('weather', [{}])[0].get('description', 'N/A')
        city = weather_data.get('name', 'Unknown City')
        wind_speed = weather_data.get('wind', {}).get('speed', 'N/A')
        
        html_template = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Daily Summary - {current_date}</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px;">
            <header style="background: linear-gradient(135deg, #007acc, #0056b3); color: white; padding: 30px; text-align: center; border-radius: 10px; margin-bottom: 30px;">
                <h1 style="margin: 0; font-size: 2.5em;">Daily Summary</h1>
                <p style="margin: 10px 0 0 0; font-size: 1.2em; opacity: 0.9;">{current_date}</p>
            </header>
            
            <section style="margin-bottom: 40px;">
                <h2 style="color: #007acc; border-bottom: 2px solid #007acc; padding-bottom: 10px;">📰 Latest News</h2>
                {news_html}
            </section>
            
            <section style="margin-bottom: 40px;">
                <h2 style="color: #007acc; border-bottom: 2px solid #007acc; padding-bottom: 10px;">🌤️ Weather Update</h2>
                <div style="background-color: #e8f4f8; padding: 20px; border-radius: 10px; border: 1px solid #b8dce8;">
                    <h3 style="margin: 0 0 15px 0; color: #333;">Current conditions in {city}</h3>
                    <div style="display: flex; flex-wrap: wrap; gap: 20px;">
                        <div style="flex: 1; min-width: 200px;">
                            <p style="margin: 5px 0;"><strong>Temperature:</strong> {temp}°C</p>
                            <p style="margin: 5px 0;"><strong>Condition:</strong> {description.title()}</p>
                        </div>
                        <div style="flex: 1; min-width: 200px;">
                            <p style="margin: 5px 0;"><strong>Humidity:</strong> {humidity}%</p>
                            <p style="margin: 5px 0;"><strong>Wind Speed:</strong>