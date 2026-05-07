```python
"""
Weather-Based Clothing Recommendation Engine

This module provides a clothing recommendation system that suggests appropriate
outfits based on current weather conditions including temperature, precipitation
probability, and wind speed. It fetches weather data and applies conditional
logic to recommend suitable clothing combinations.

Features:
- Temperature-based layering recommendations
- Rain probability assessment for waterproof gear
- Wind speed considerations for protective clothing
- Seasonal outfit suggestions
- Error handling for weather API failures

Usage: python script.py
"""

import json
import sys
from typing import Dict, List, Tuple, Optional


class WeatherClothingRecommender:
    """Weather-based clothing recommendation engine."""
    
    def __init__(self):
        """Initialize the clothing recommendation engine."""
        self.temperature_ranges = {
            'freezing': (-50, 32),      # Below 32°F
            'cold': (32, 50),           # 32-50°F
            'cool': (50, 65),           # 50-65°F
            'mild': (65, 75),           # 65-75°F
            'warm': (75, 85),           # 75-85°F
            'hot': (85, 100),           # 85-100°F
            'extreme_hot': (100, 150)   # Above 100°F
        }
        
        self.clothing_database = {
            'base_layers': {
                'freezing': ['thermal underwear', 'merino wool base layer', 'fleece-lined leggings'],
                'cold': ['long-sleeve shirt', 'thermal top', 'warm leggings'],
                'cool': ['light sweater', 'long-sleeve shirt', 'jeans'],
                'mild': ['t-shirt', 'light blouse', 'casual pants'],
                'warm': ['tank top', 'short-sleeve shirt', 'shorts'],
                'hot': ['lightweight t-shirt', 'tank top', 'shorts'],
                'extreme_hot': ['moisture-wicking shirt', 'breathable tank', 'light shorts']
            },
            'outer_layers': {
                'freezing': ['heavy winter coat', 'parka', 'insulated jacket'],
                'cold': ['winter jacket', 'wool coat', 'fleece jacket'],
                'cool': ['light jacket', 'cardigan', 'hoodie'],
                'mild': ['light sweater', 'denim jacket'],
                'warm': [],
                'hot': [],
                'extreme_hot': []
            },
            'accessories': {
                'freezing': ['winter hat', 'insulated gloves', 'scarf', 'warm socks'],
                'cold': ['beanie', 'gloves', 'scarf', 'warm socks'],
                'cool': ['light scarf', 'gloves'],
                'mild': [],
                'warm': ['sunglasses', 'cap'],
                'hot': ['sunglasses', 'sun hat', 'sunscreen'],
                'extreme_hot': ['wide-brim hat', 'sunglasses', 'cooling towel']
            },
            'footwear': {
                'freezing': ['insulated boots', 'winter boots', 'thick socks'],
                'cold': ['warm boots', 'closed-toe shoes', 'warm socks'],
                'cool': ['sneakers', 'boots', 'closed-toe shoes'],
                'mild': ['sneakers', 'loafers', 'casual shoes'],
                'warm': ['sneakers', 'sandals', 'breathable shoes'],
                'hot': ['sandals', 'breathable sneakers', 'open-toe shoes'],
                'extreme_hot': ['ventilated sandals', 'mesh sneakers']
            },
            'rain_gear': {
                'light': ['light rain jacket', 'water-resistant shoes'],
                'moderate': ['waterproof jacket', 'rain boots', 'umbrella'],
                'heavy': ['full rain suit', 'waterproof boots', 'umbrella', 'rain hat']
            },
            'wind_gear': {
                'breezy': ['light windbreaker'],
                'windy': ['windproof jacket', 'secure hat'],
                'very_windy': ['heavy windproof coat', 'face protection', 'secure accessories']
            }
        }
    
    def get_temperature_category(self, temp_f: float) -> str:
        """Categorize temperature into clothing-relevant ranges."""
        for category, (min_temp, max_temp) in self.temperature_ranges.items():
            if min_temp <= temp_f < max_temp:
                return category
        return 'mild'  # Default fallback
    
    def get_rain_category(self, rain_probability: float) -> Optional[str]:
        """Categorize rain probability for gear recommendations."""
        if rain_probability >= 70:
            return 'heavy'
        elif rain_probability >= 40:
            return 'moderate'
        elif rain_probability >= 20:
            return 'light'
        return None
    
    def get_wind_category(self, wind_speed: float) -> Optional[str]:
        """Categorize wind speed for protective clothing."""
        if wind_speed >= 25:  # mph
            return 'very_windy'
        elif wind_speed >= 15:
            return 'windy'
        elif wind_speed >= 8:
            return 'breezy'
        return None
    
    def generate_recommendations(self, weather_data: Dict) -> Dict[str, List[str]]:
        """Generate clothing recommendations based on weather conditions."""
        try:
            temp_f = weather_data.get('temperature', 70)
            rain_prob = weather_data.get('rain_probability', 0)
            wind_speed = weather_data.get('wind_speed', 0)
            humidity = weather_data.get('humidity', 50)
            
            temp_category = self.get_temperature_category(temp_f)
            rain_category = self.get_rain_category(rain_prob)
            wind_category = self.get_wind_category(wind_speed)
            
            recommendations = {
                'base_layers': self.clothing_database['base_layers'][temp_category].copy(),
                'outer_layers': self.clothing_database['outer_layers'][temp_category].copy(),
                'accessories': self.clothing_database['accessories'][temp_category].copy(),
                'footwear': self.clothing_database['footwear'][temp_category].copy(),
                'special_considerations': []
            }
            
            # Add rain gear if needed
            if rain_category:
                rain_gear = self.clothing_database['rain_gear'][rain_category]
                recommendations['outer_layers'].extend(rain_gear)
                recommendations['special_considerations'].append(
                    f"Rain expected ({rain_prob}% chance) - waterproof gear recommended"
                )
            
            # Add wind protection if needed
            if wind_category:
                wind_gear = self.clothing_database['wind_gear'][wind_category]
                recommendations['outer_layers'].extend(wind_gear)
                recommendations['special_considerations'].append(
                    f"Windy conditions ({wind_speed} mph) - wind protection recommended"
                )
            
            # High humidity adjustments
            if humidity > 80:
                recommendations['special_considerations'].append(
                    f"High humidity ({humidity}%) - choose breathable, moisture-wicking fabrics"
                )
                if temp_category in ['warm', 'hot', 'extreme_hot']:
                    recommendations['base_layers'] = [
                        item for item in recommendations['base_layers'] 
                        if 'moisture-wicking' in item or 'breathable' in item
                    ] or ['moisture-wicking shirt']
            
            # Remove duplicates and empty categories
            for category in recommendations:
                if isinstance(recommendations[category], list):
                    recommendations[category] = list(set(recommendations[category]))
            
            return recommendations
            
        except Exception as e:
            raise Exception(f"Error generating recommendations: {str(e)}")
    
    def format_outfit_suggestion(self, recommendations: Dict[str, List[str]], 
                               weather_data: Dict) -> str:
        """Format the clothing recommendations into a readable outfit suggestion."""
        try:
            temp_f = weather_data.