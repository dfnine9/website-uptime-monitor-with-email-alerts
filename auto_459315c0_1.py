```python
"""
Email Template Formatting System for Weather Data

This module provides a comprehensive email template formatting system that converts
weather data into both HTML and plain text email formats. Features include:
- Professional styling with CSS
- City-specific sections for organized data presentation  
- Responsive design optimized for mobile viewing
- Self-contained implementation using only standard library
- Comprehensive error handling and validation

The system generates complete email templates ready for distribution via email
clients or automated systems.
"""

import json
import datetime
from typing import Dict, List, Any, Optional


class WeatherEmailFormatter:
    """Professional email template formatter for weather data."""
    
    def __init__(self):
        self.html_template = self._create_html_template()
        self.css_styles = self._create_css_styles()
    
    def _create_css_styles(self) -> str:
        """Create responsive CSS styles for the email template."""
        return """
        <style>
            @media screen and (max-width: 600px) {
                .container { width: 100% !important; padding: 10px !important; }
                .city-section { margin: 10px 0 !important; }
                .weather-grid { display: block !important; }
                .weather-item { margin: 5px 0 !important; padding: 10px !important; }
                .temperature { font-size: 24px !important; }
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f5f7fa;
                color: #333;
                line-height: 1.6;
            }
            
            .container {
                max-width: 800px;
                margin: 0 auto;
                background-color: white;
                padding: 20px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            
            .header {
                text-align: center;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 8px 8px 0 0;
                margin: -20px -20px 20px -20px;
            }
            
            .header h1 {
                margin: 0;
                font-size: 28px;
                font-weight: 300;
            }
            
            .date {
                margin: 10px 0 0 0;
                font-size: 14px;
                opacity: 0.9;
            }
            
            .city-section {
                margin: 25px 0;
                border: 1px solid #e1e8ed;
                border-radius: 8px;
                overflow: hidden;
            }
            
            .city-header {
                background-color: #f8f9fa;
                padding: 15px 20px;
                border-bottom: 1px solid #e1e8ed;
                font-weight: 600;
                font-size: 18px;
                color: #495057;
            }
            
            .weather-content {
                padding: 20px;
            }
            
            .weather-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin: 15px 0;
            }
            
            .weather-item {
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 6px;
                border-left: 4px solid #667eea;
                text-align: center;
            }
            
            .temperature {
                font-size: 32px;
                font-weight: bold;
                color: #667eea;
                margin: 5px 0;
            }
            
            .condition {
                font-size: 16px;
                color: #6c757d;
                margin: 5px 0;
                text-transform: capitalize;
            }
            
            .details {
                font-size: 14px;
                color: #868e96;
                margin: 10px 0 0 0;
            }
            
            .detail-item {
                margin: 5px 0;
            }
            
            .footer {
                text-align: center;
                padding: 20px;
                border-top: 1px solid #e1e8ed;
                color: #6c757d;
                font-size: 14px;
                margin-top: 30px;
            }
            
            .alert {
                background-color: #fff3cd;
                border: 1px solid #ffeaa7;
                color: #856404;
                padding: 12px 15px;
                border-radius: 4px;
                margin: 15px 0;
            }
        </style>
        """
    
    def _create_html_template(self) -> str:
        """Create the base HTML template structure."""
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Weather Report</title>
            {styles}
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🌤️ Weather Report</h1>
                    <div class="date">{date}</div>
                </div>
                
                {content}
                
                <div class="footer">
                    <p>Generated by Weather Email System | {timestamp}</p>
                    <p>Stay informed, stay prepared! 🌈</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def format_html_email(self, weather_data: List[Dict[str, Any]]) -> str:
        """
        Convert weather data to HTML email format.
        
        Args:
            weather_data: List of weather data dictionaries for different cities
            
        Returns:
            Formatted HTML email string
        """
        try:
            content_sections = []
            
            for city_data in weather_data:
                city_name = city_data.get('city', 'Unknown City')
                weather_info = city_data.get('weather', {})
                
                # Create weather grid items
                weather_items = []
                
                # Temperature item
                temp = weather_info.get('temperature', 'N/A')
                condition = weather_info.get('condition', 'Unknown')
                weather_items.append(f"""
                    <div class="weather-item">
                        <div class="temperature">{temp}°</div>
                        <div class="condition">{condition}</div>
                    </div>
                """)
                
                # Additional weather details
                details = []
                if 'humidity' in weather_info:
                    details.append(f"💧 Humidity: {weather_info['humidity']}%")
                if 'wind_speed' in weather_info:
                    details.append(f"💨 Wind: {weather_info['wind_speed']} mph")
                if 'pressure' in weather_info:
                    details.append(f"🌡️ Pressure: {weather_info['pressure']} hPa")
                if 'visibility' in weather_info:
                    details.append(f"👁️ Visibility: {weather_info['visibility']} km")
                
                if details:
                    detail_items = ''.join([f'<div class="detail-item">{detail}</div>' for detail in details])
                    weather_items.append(f"""
                        <div class="weather-item">
                            <div class="details">{detail_items}</div>
                        </div>
                    """)
                
                # Add alerts if present
                alerts_html = ""
                if 'alerts' in weather_info and weather_info['alerts']:
                    alerts_content =