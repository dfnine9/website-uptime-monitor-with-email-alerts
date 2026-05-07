#!/usr/bin/env python3
"""
Weather Data Fetcher

This module fetches current weather data from the OpenWeatherMap API for a specified location.
It retrieves temperature, precipitation probability, wind speed, and humidity information.

The script requires an OpenWeatherMap API key to function properly.
Sign up at https://openweathermap.org/api to get a free API key.

Usage:
    python script.py

Dependencies:
    - httpx (for HTTP requests)
    - Standard library modules (json, sys)
"""

import json
import sys
import httpx


def get_weather_data(location, api_key):
    """
    Fetch weather data from OpenWeatherMap API.
    
    Args:
        location (str): City name or coordinates
        api_key (str): OpenWeatherMap API key
        
    Returns:
        dict: Weather data or None if request fails
    """
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": location,
        "appid": api_key,
        "units": "metric"  # Use Celsius
    }
    
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(base_url, params=params)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
        return None
    except httpx.RequestError as e:
        print(f"Request error occurred: {e}")
        return None
    except json.JSONDecodeError:
        print("Error: Invalid JSON response from API")
        return None


def format_weather_output(weather_data):
    """
    Format weather data for display.
    
    Args:
        weather_data (dict): Raw weather data from API
        
    Returns:
        str: Formatted weather information
    """
    if not weather_data:
        return "No weather data available"
    
    try:
        location = f"{weather_data['name']}, {weather_data['sys']['country']}"
        temperature = weather_data['main']['temp']
        humidity = weather_data['main']['humidity']
        wind_speed = weather_data['wind']['speed']
        
        # Precipitation probability is not available in current weather endpoint
        # Using cloudiness as an indicator
        cloudiness = weather_data['clouds']['all']
        description = weather_data['weather'][0]['description'].title()
        
        output = f"""
Weather Report for {location}
{'=' * 40}
Temperature: {temperature}°C
Humidity: {humidity}%
Wind Speed: {wind_speed} m/s
Cloudiness: {cloudiness}%
Conditions: {description}
        """
        
        return output.strip()
        
    except KeyError as e:
        return f"Error parsing weather data: Missing key {e}"


def main():
    """Main function to run the weather data fetcher."""
    # You need to set your OpenWeatherMap API key here
    API_KEY = "your_api_key_here"
    
    if API_KEY == "your_api_key_here":
        print("Error: Please set your OpenWeatherMap API key in the script")
        print("Get one free at: https://openweathermap.org/api")
        sys.exit(1)
    
    # Get location from user input
    try:
        location = input("Enter city name (or press Enter for London): ").strip()
        if not location:
            location = "London"
        
        print(f"\nFetching weather data for {location}...")
        
        weather_data = get_weather_data(location, API_KEY)
        
        if weather_data:
            formatted_output = format_weather_output(weather_data)
            print(formatted_output)
        else:
            print("Failed to retrieve weather data")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()