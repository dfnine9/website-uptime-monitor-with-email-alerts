```python
#!/usr/bin/env python3
"""
Price Monitoring Service

A self-contained price monitoring system that tracks product prices from multiple sources,
compares them against user-defined target thresholds, calculates percentage changes,
and triggers alerts when prices drop below specified limits.

Features:
- Real-time price fetching from configurable sources
- Threshold-based alert system
- Percentage change calculations
- JSON-based configuration
- Comprehensive error handling
- Stdout logging with timestamps

Usage: python script.py
"""

import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
import re

try:
    import httpx
except ImportError:
    print("ERROR: httpx not installed. Install with: pip install httpx")
    exit(1)

# Configure logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class PriceMonitor:
    """Main price monitoring service class."""
    
    def __init__(self, config_file: str = "price_config.json"):
        """Initialize the price monitor with configuration."""
        self.config_file = config_file
        self.config = self._load_config()
        self.price_history: Dict[str, List[Tuple[datetime, float]]] = {}
        self.client = httpx.Client(timeout=30.0)
        
    def _load_config(self) -> Dict:
        """Load monitoring configuration from JSON file."""
        default_config = {
            "products": [
                {
                    "name": "Example Product",
                    "url": "https://httpbin.org/json",
                    "price_selector": "$.slideshow.slides[0].title",
                    "target_price": 100.0,
                    "alert_threshold": 0.15
                }
            ],
            "check_interval": 300,
            "user_agent": "PriceMonitor/1.0"
        }
        
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                logger.info(f"Loaded configuration from {self.config_file}")
                return config
        except FileNotFoundError:
            logger.warning(f"Config file {self.config_file} not found, using defaults")
            # Create default config file
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            return default_config
    
    def _extract_price_from_text(self, text: str) -> Optional[float]:
        """Extract price from text using regex patterns."""
        # Common price patterns
        patterns = [
            r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)',  # $123.45, $1,234.56
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:USD|dollars?)',  # 123.45 USD
            r'Price:?\s*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)',  # Price: $123.45
            r'(\d+(?:\.\d{2})?)',  # Simple number
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                price_str = match.group(1).replace(',', '')
                try:
                    return float(price_str)
                except ValueError:
                    continue
        return None
    
    def _fetch_price(self, product: Dict) -> Optional[float]:
        """Fetch current price for a product."""
        try:
            headers = {
                'User-Agent': self.config.get('user_agent', 'PriceMonitor/1.0'),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
            
            response = self.client.get(product['url'], headers=headers)
            response.raise_for_status()
            
            # For demo purposes with httpbin.org/json, extract a mock price
            if 'httpbin.org' in product['url']:
                # Mock price that varies slightly
                import hashlib
                seed = int(hashlib.md5(str(time.time()).encode()).hexdigest()[:8], 16)
                base_price = product.get('target_price', 100.0)
                variation = (seed % 20 - 10) / 100.0  # ±10% variation
                mock_price = base_price * (1 + variation)
                logger.info(f"Mock price generated for demo: ${mock_price:.2f}")
                return mock_price
            
            # Try to extract price from response text
            price = self._extract_price_from_text(response.text)
            if price is None:
                logger.warning(f"Could not extract price from {product['url']}")
                return None
                
            logger.info(f"Fetched price for {product['name']}: ${price:.2f}")
            return price
            
        except httpx.RequestError as e:
            logger.error(f"Network error fetching {product['url']}: {e}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} for {product['url']}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching price for {product['name']}: {e}")
            return None
    
    def _calculate_percentage_change(self, old_price: float, new_price: float) -> float:
        """Calculate percentage change between two prices."""
        if old_price == 0:
            return 0.0
        return ((new_price - old_price) / old_price) * 100
    
    def _check_alert_conditions(self, product: Dict, current_price: float, previous_price: Optional[float]):
        """Check if alert conditions are met and trigger alerts."""
        target_price = product.get('target_price', 0)
        alert_threshold = product.get('alert_threshold', 0.1)
        
        # Check if price dropped below target
        if current_price <= target_price:
            logger.warning(f"🎯 TARGET REACHED: {product['name']} is now ${current_price:.2f} (target: ${target_price:.2f})")
            print(f"ALERT: {product['name']} reached target price of ${target_price:.2f}!")
        
        # Check for significant price drops
        if previous_price:
            percentage_change = self._calculate_percentage_change(previous_price, current_price)
            
            if percentage_change <= -(alert_threshold * 100):
                logger.warning(f"📉 PRICE DROP ALERT: {product['name']} dropped {abs(percentage_change):.1f}% to ${current_price:.2f}")
                print(f"ALERT: {product['name']} price dropped {abs(percentage_change):.1f}% to ${current_price:.2f}!")
            elif percentage_change > 0:
                logger.info(f"📈 Price increased for {product['name']}: +{percentage_change:.1f}% to ${current_price:.2f}")
    
    def _update_price_history(self, product_name: str, price: float):
        """Update price history for a product."""
        if product_name not in self.price_history:
            self.price_history[product_name] = []
        
        current_time = datetime.now()
        self.price_history[product_name].append((current_time, price))
        
        # Keep only last 100 entries to prevent memory issues
        if len(self.price_history[product_name]) > 100:
            self.price_history[