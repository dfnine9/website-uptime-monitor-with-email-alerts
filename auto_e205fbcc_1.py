```python
"""
Weather & Calendar HTML Email Template Generator

This module creates a beautifully styled HTML email template that displays:
- Current weather information (temperature, conditions, forecast)
- Calendar events for the day
- Clean, responsive design with embedded CSS

The template is generated with sample data and outputs HTML that can be
sent via email or saved as a file.

Dependencies: Standard library only
Usage: python script.py
"""

import json
import datetime
from typing import Dict, List, Any


def generate_weather_data() -> Dict[str, Any]:
    """Generate sample weather data."""
    try:
        return {
            "current": {
                "temperature": 72,
                "condition": "Partly Cloudy",
                "humidity": 65,
                "wind_speed": 8,
                "location": "San Francisco, CA"
            },
            "forecast": [
                {"day": "Today", "high": 75, "low": 58, "condition": "Partly Cloudy", "icon": "⛅"},
                {"day": "Tomorrow", "high": 78, "low": 61, "condition": "Sunny", "icon": "☀️"},
                {"day": "Wednesday", "high": 73, "low": 59, "condition": "Cloudy", "icon": "☁️"},
                {"day": "Thursday", "high": 69, "low": 55, "condition": "Light Rain", "icon": "🌦️"},
                {"day": "Friday", "high": 71, "low": 57, "condition": "Partly Cloudy", "icon": "⛅"}
            ]
        }
    except Exception as e:
        print(f"Error generating weather data: {e}")
        return {}


def generate_calendar_events() -> List[Dict[str, Any]]:
    """Generate sample calendar events."""
    try:
        today = datetime.date.today()
        return [
            {
                "time": "09:00 AM",
                "title": "Team Standup",
                "location": "Conference Room A",
                "duration": "30 min"
            },
            {
                "time": "11:00 AM",
                "title": "Client Presentation",
                "location": "Zoom Meeting",
                "duration": "1 hour"
            },
            {
                "time": "02:30 PM",
                "title": "Project Review",
                "location": "Office 201",
                "duration": "45 min"
            },
            {
                "time": "04:00 PM",
                "title": "One-on-One with Manager",
                "location": "Manager's Office",
                "duration": "30 min"
            }
        ]
    except Exception as e:
        print(f"Error generating calendar events: {e}")
        return []


def create_html_template(weather_data: Dict[str, Any], calendar_events: List[Dict[str, Any]]) -> str:
    """Create the HTML email template with weather and calendar data."""
    try:
        current_date = datetime.date.today().strftime("%B %d, %Y")
        current_weather = weather_data.get("current", {})
        forecast = weather_data.get("forecast", [])
        
        # Generate forecast HTML
        forecast_html = ""
        for day_forecast in forecast:
            forecast_html += f"""
            <div class="forecast-day">
                <div class="forecast-icon">{day_forecast.get('icon', '☀️')}</div>
                <div class="forecast-day-name">{day_forecast.get('day', 'N/A')}</div>
                <div class="forecast-temps">
                    <span class="high">{day_forecast.get('high', 0)}°</span>
                    <span class="low">{day_forecast.get('low', 0)}°</span>
                </div>
                <div class="forecast-condition">{day_forecast.get('condition', 'N/A')}</div>
            </div>
            """
        
        # Generate calendar events HTML
        events_html = ""
        for event in calendar_events:
            events_html += f"""
            <div class="event">
                <div class="event-time">{event.get('time', 'N/A')}</div>
                <div class="event-details">
                    <div class="event-title">{event.get('title', 'Untitled Event')}</div>
                    <div class="event-meta">
                        <span class="event-location">📍 {event.get('location', 'TBD')}</span>
                        <span class="event-duration">⏱️ {event.get('duration', 'N/A')}</span>
                    </div>
                </div>
            </div>
            """
        
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Weather & Calendar Update</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            background-color: #f5f7fa;
            color: #333;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 600px;
            margin: 20px auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 28px;
            font-weight: 300;
            margin-bottom: 5px;
        }}
        
        .header .date {{
            font-size: 16px;
            opacity: 0.9;
        }}
        
        .weather-section {{
            padding: 30px;
            background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
            color: white;
        }}
        
        .current-weather {{
            text-align: center;
            margin-bottom: 30px;
        }}
        
        .current-temp {{
            font-size: 48px;
            font-weight: 100;
            margin-bottom: 10px;
        }}
        
        .current-condition {{
            font-size: 20px;
            margin-bottom: 5px;
        }}
        
        .current-location {{
            font-size: 14px;
            opacity: 0.9;
        }}
        
        .weather-details {{
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
            padding: 15px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
        }}
        
        .weather-detail {{
            text-align: center;
        }}
        
        .weather-detail-label {{
            font-size: 12px;
            opacity: 0.8;
            margin-bottom: 5px;
        }}
        
        .weather-detail-value {{
            font-size: 16px;
            font-weight: 500;
        }}
        
        .forecast {{
            display: flex;
            justify-content: space-between;
            margin-top: 20px;
        }}
        
        .forecast-day {{
            text-align: center;
            flex: 1;
            padding: 10px;
        }}
        
        .forecast-icon {{
            font-size: 24px;
            margin-bottom: 8px;
        }}