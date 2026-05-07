```python
"""
E-commerce Price Scraper

A self-contained Python script that scrapes product prices from e-commerce websites
using requests and BeautifulSoup. Extracts price data using CSS selectors and 
maintains historical price data in a local JSON file with timestamps.

Features:
- Scrapes prices from multiple e-commerce sites
- Uses configurable CSS selectors for different sites
- Stores historical data with timestamps
- Handles errors gracefully
- Self-contained with minimal dependencies

Usage: python script.py
"""

import json
import re
import time
from datetime import datetime
from urllib.parse import urlparse
import httpx
from bs4 import BeautifulSoup


class PriceScraper:
    def __init__(self, data_file='price_history.json'):
        self.data_file = data_file
        self.session = httpx.Client(
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            },
            timeout=30.0
        )
        
        # Common price selectors for popular e-commerce sites
        self.price_selectors = {
            'amazon.com': ['.a-price-whole', '.a-offscreen', '.a-price .a-offscreen'],
            'ebay.com': ['.notranslate', '.u-flL.condText', '.display-price'],
            'walmart.com': ['[data-automation-id="product-price"]', '.price-characteristic'],
            'target.com': ['[data-test="product-price"]', '.h-text-red'],
            'bestbuy.com': ['.pricing-current-price', '.sr-only:contains("current price")'],
            'default': ['.price', '.cost', '.amount', '[class*="price"]', '[class*="cost"]']
        }
    
    def load_history(self):
        """Load existing price history from JSON file."""
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            print(f"Warning: Corrupted data file {self.data_file}, starting fresh")
            return {}
    
    def save_history(self, data):
        """Save price history to JSON file."""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def get_domain_selectors(self, url):
        """Get appropriate CSS selectors based on domain."""
        domain = urlparse(url).netloc.lower()
        for site, selectors in self.price_selectors.items():
            if site in domain:
                return selectors
        return self.price_selectors['default']
    
    def extract_price(self, text):
        """Extract numeric price from text using regex."""
        if not text:
            return None
        
        # Remove currency symbols and extract number
        price_pattern = r'[\$£€¥₹]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
        match = re.search(price_pattern, text.replace(',', ''))
        
        if match:
            try:
                return float(match.group(1).replace(',', ''))
            except ValueError:
                return None
        return None
    
    def scrape_price(self, url):
        """Scrape price from a single URL."""
        try:
            print(f"Scraping: {url}")
            
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            selectors = self.get_domain_selectors(url)
            
            for selector in selectors:
                elements = soup.select(selector)
                for element in elements:
                    price_text = element.get_text(strip=True)
                    price = self.extract_price(price_text)
                    
                    if price and price > 0:
                        print(f"Found price: ${price:.2f}")
                        return price
            
            print("No price found with configured selectors")
            return None
            
        except httpx.TimeoutException:
            print(f"Timeout scraping {url}")
            return None
        except httpx.HTTPStatusError as e:
            print(f"HTTP error {e.response.status_code} for {url}")
            return None
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None
    
    def update_price_history(self, url, price):
        """Update price history for a URL."""
        history = self.load_history()
        timestamp = datetime.now().isoformat()
        
        if url not in history:
            history[url] = {
                'domain': urlparse(url).netloc,
                'prices': []
            }
        
        # Add new price entry
        history[url]['prices'].append({
            'price': price,
            'timestamp': timestamp
        })
        
        # Keep only last 100 entries per URL
        history[url]['prices'] = history[url]['prices'][-100:]
        
        self.save_history(history)
        return history[url]
    
    def scrape_urls(self, urls):
        """Scrape prices from multiple URLs."""
        results = {}
        
        for url in urls:
            price = self.scrape_price(url)
            
            if price:
                history = self.update_price_history(url, price)
                results[url] = {
                    'current_price': price,
                    'price_count': len(history['prices'])
                }
                
                # Show price trend if we have historical data
                if len(history['prices']) > 1:
                    prev_price = history['prices'][-2]['price']
                    change = price - prev_price
                    change_pct = (change / prev_price) * 100
                    
                    trend = "↑" if change > 0 else "↓" if change < 0 else "→"
                    print(f"Price change: {trend} ${change:+.2f} ({change_pct:+.1f}%)")
            else:
                results[url] = {'error': 'Could not extract price'}
            
            # Be respectful with request timing
            time.sleep(1)
        
        return results
    
    def show_history(self, url=None):
        """Display price history for URL(s)."""
        history = self.load_history()
        
        if not history:
            print("No price history found")
            return
        
        urls_to_show = [url] if url else history.keys()
        
        for url in urls_to_show:
            if url in history:
                print(f"\nPrice history for {url}:")
                print(f"Domain: {history[url]['domain']}")
                
                prices = history[url]['prices'][-10:]  # Last 10 entries
                for entry in prices:
                    timestamp = entry['timestamp'][:19]  # Remove microseconds
                    print(f"  {timestamp}: ${entry['price']:.2f}")
            else:
                print(f"No history found for {url}")


def main():
    """Main function demonstrating the price scraper."""
    scraper = PriceScraper()
    
    # Example URLs (replace with actual product URLs)
    test_urls = [
        # Example URLs - replace with real product pages
        "https://www.amazon.com/dp/B08N5WRWNW",  # Example product
        "https://www.walmart.com/ip/123456789",   # Example product
    ]
    
    print("E-commerce Price Scraper")
    print("=" * 50)
    
    # Show existing history
    print("\nExisting price history:")
    scraper.show_history()