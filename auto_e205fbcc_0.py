```python
#!/usr/bin/env python3
"""
Weather and Calendar Integration Script

This script fetches current weather data from the OpenWeatherMap API and retrieves
upcoming calendar events from the Google Calendar API, then combines them into a
structured data format for analysis and display.

Features:
- Retrieves current weather conditions and forecast
- Fetches upcoming calendar events (next 7 days)
- Combines data into structured JSON format
- Includes comprehensive error handling
- Self-contained with minimal dependencies

Dependencies: httpx (for HTTP requests)
APIs Required: OpenWeatherMap API key, Google Calendar API credentials
"""

import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

try:
    import httpx
except ImportError:
    print("Error: httpx not installed. Install with: pip install httpx")
    sys.exit(1)


class WeatherCalendarIntegrator:
    """Integrates weather data and calendar events into structured format."""
    
    def __init__(self, weather_api_key: str, google_credentials: Dict[str, Any]):
        """
        Initialize with API credentials.
        
        Args:
            weather_api_key: OpenWeatherMap API key
            google_credentials: Google API credentials dict
        """
        self.weather_api_key = weather_api_key
        self.google_credentials = google_credentials
        self.base_weather_url = "https://api.openweathermap.org/data/2.5"
        self.google_calendar_url = "https://www.googleapis.com/calendar/v3"
        
    def fetch_weather_data(self, city: str = "New York") -> Optional[Dict[str, Any]]:
        """
        Fetch current weather and forecast data.
        
        Args:
            city: City name for weather lookup
            
        Returns:
            Dict containing weather data or None if error
        """
        try:
            with httpx.Client(timeout=10.0) as client:
                # Current weather
                current_params = {
                    'q': city,
                    'appid': self.weather_api_key,
                    'units': 'metric'
                }
                current_response = client.get(
                    f"{self.base_weather_url}/weather",
                    params=current_params
                )
                current_response.raise_for_status()
                current_data = current_response.json()
                
                # 5-day forecast
                forecast_response = client.get(
                    f"{self.base_weather_url}/forecast",
                    params=current_params
                )
                forecast_response.raise_for_status()
                forecast_data = forecast_response.json()
                
                return {
                    'current': {
                        'temperature': current_data['main']['temp'],
                        'feels_like': current_data['main']['feels_like'],
                        'humidity': current_data['main']['humidity'],
                        'pressure': current_data['main']['pressure'],
                        'description': current_data['weather'][0]['description'],
                        'wind_speed': current_data['wind']['speed'],
                        'visibility': current_data.get('visibility', 0) / 1000,  # Convert to km
                        'timestamp': datetime.utcnow().isoformat()
                    },
                    'forecast': [
                        {
                            'datetime': item['dt_txt'],
                            'temperature': item['main']['temp'],
                            'description': item['weather'][0]['description'],
                            'precipitation_probability': item.get('pop', 0) * 100
                        }
                        for item in forecast_data['list'][:24]  # Next 24 forecasts (5 days)
                    ]
                }
                
        except httpx.RequestError as e:
            print(f"Weather API request error: {e}")
            return None
        except httpx.HTTPStatusError as e:
            print(f"Weather API HTTP error: {e.response.status_code}")
            return None
        except KeyError as e:
            print(f"Weather API response parsing error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected weather API error: {e}")
            return None
    
    def fetch_calendar_events(self, calendar_id: str = "primary", days_ahead: int = 7) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch upcoming calendar events.
        
        Args:
            calendar_id: Google Calendar ID (default: primary)
            days_ahead: Number of days to fetch events for
            
        Returns:
            List of calendar events or None if error
        """
        try:
            # Get access token (simplified - in production, use proper OAuth flow)
            access_token = self.google_credentials.get('access_token')
            if not access_token:
                print("Error: Google access token not provided")
                return None
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Calculate time range
            now = datetime.utcnow()
            time_max = now + timedelta(days=days_ahead)
            
            params = {
                'timeMin': now.isoformat() + 'Z',
                'timeMax': time_max.isoformat() + 'Z',
                'singleEvents': 'true',
                'orderBy': 'startTime',
                'maxResults': 50
            }
            
            with httpx.Client(timeout=10.0) as client:
                response = client.get(
                    f"{self.google_calendar_url}/calendars/{calendar_id}/events",
                    headers=headers,
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                
                events = []
                for item in data.get('items', []):
                    start_time = item.get('start', {})
                    end_time = item.get('end', {})
                    
                    events.append({
                        'id': item.get('id'),
                        'summary': item.get('summary', 'No Title'),
                        'description': item.get('description', ''),
                        'location': item.get('location', ''),
                        'start_datetime': start_time.get('dateTime', start_time.get('date')),
                        'end_datetime': end_time.get('dateTime', end_time.get('date')),
                        'attendees': [
                            attendee.get('email') for attendee in item.get('attendees', [])
                        ],
                        'is_all_day': 'date' in start_time
                    })
                
                return events
                
        except httpx.RequestError as e:
            print(f"Calendar API request error: {e}")
            return None
        except httpx.HTTPStatusError as e:
            print(f"Calendar API HTTP error: {e.response.status_code}")
            return None
        except KeyError as e:
            print(f"Calendar API response parsing error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected calendar API error: {e}")
            return None
    
    def combine_data(self, weather_data: Dict[str, Any], calendar_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Combine weather and calendar data into structured format.
        
        Args:
            weather_data: Weather information
            calendar_events: List of calendar events
            
        Returns:
            Combined structured data
        """
        try:
            combined_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'weather': weather_data,
                'calendar': {
                    'events_count': len(calendar_events),
                    'events': calendar_events
                },
                'insights': self._generate_insights(weather_data, calendar_events)
            }
            
            return combined_data
            
        except Exception as e:
            print(f"Error combining data: {e}")
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'weather': weather_data,
                'calendar': {'events_count': len(calendar_events