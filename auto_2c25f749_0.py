#!/usr/bin/env python3
"""
Web Scraper for Product Price Extraction

This module provides a self-contained web scraper that extracts product prices 
from target URLs and stores them in a local JSON database with timestamps.
The scraper uses pattern matching to identify price elements and maintains
a persistent database of price history for tracking purposes.

Dependencies: httpx (for HTTP requests)
Usage: python script.py
"""

import json
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import sys

try:
    import httpx
except ImportError:
    print("Error: httpx not installed. Install with: pip install httpx")
    sys.exit(1)


class PriceScraper:
    def __init__(self, db_file: str = "price_database.json"):
        self.db_file = Path(db_file)
        self.session = httpx.Client(
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            },
            timeout=30.0
        )
        self.price_patterns = [
            r'\$(\d+(?:\.\d{2})?)',  # $19.99
            r'(\d+(?:\.\d{2})?)\s*USD',  # 19.99 USD
            r'Price:\s*\$?(\d+(?:\.\d{2})?)',  # Price: $19.99
            r'"price":\s*"?(\d+(?:\.\d{2}))"?',  # "price": "19.99"
            r'data-price="(\d+(?:\.\d{2})?)"',  # data-price="19.99"
        ]
    
    def load_database(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load existing price database or create new one."""
        try:
            if self.db_file.exists():
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading database: {e}")
            return {}
    
    def save_database(self, data: Dict[str, List[Dict[str, Any]]]) -> None:
        """Save price database to JSON file."""
        try:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving database: {e}")
    
    def extract_price(self, html_content: str) -> Optional[float]:
        """Extract price from HTML content using regex patterns."""
        try:
            for pattern in self.price_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                if matches:
                    # Return first valid price found
                    price_str = matches[0].replace(',', '')
                    return float(price_str)
            return None
        except Exception as e:
            print(f"Error extracting price: {e}")
            return None
    
    def scrape_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrape a single URL for product price."""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            price = self.extract_price(response.text)
            
            if price is not None:
                return {
                    'url': url,
                    'price': price,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'success'
                }
            else:
                return {
                    'url': url,
                    'price': None,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'no_price_found'
                }
                
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return {
                'url': url,
                'price': None,
                'timestamp': datetime.now().isoformat(),
                'status': f'error: {str(e)}'
            }
    
    def scrape_multiple_urls(self, urls: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """Scrape multiple URLs and update database."""
        database = self.load_database()
        
        for url in urls:
            print(f"Scraping: {url}")
            result = self.scrape_url(url)
            
            if result:
                if url not in database:
                    database[url] = []
                database[url].append(result)
                
                if result['status'] == 'success':
                    print(f"  ✓ Price found: ${result['price']}")
                else:
                    print(f"  ✗ {result['status']}")
            
            # Rate limiting
            time.sleep(1)
        
        self.save_database(database)
        return database
    
    def close(self):
        """Clean up HTTP session."""
        self.session.close()


def main():
    """Main execution function."""
    # Example URLs for demonstration (replace with actual target URLs)
    target_urls = [
        "https://httpbin.org/html",  # Test URL
        "https://example.com",       # Test URL
    ]
    
    scraper = PriceScraper()
    
    try:
        print("Starting price scraper...")
        print(f"Database file: {scraper.db_file}")
        print("-" * 50)
        
        results = scraper.scrape_multiple_urls(target_urls)
        
        print("-" * 50)
        print("Scraping completed!")
        print(f"Total URLs processed: {len(target_urls)}")
        
        # Display summary
        for url, entries in results.items():
            latest = entries[-1] if entries else None
            if latest:
                print(f"\nURL: {url}")
                print(f"Latest price: ${latest['price']}" if latest['price'] else "No price found")
                print(f"Status: {latest['status']}")
                print(f"Timestamp: {latest['timestamp']}")
        
        # Show database stats
        total_entries = sum(len(entries) for entries in results.values())
        print(f"\nDatabase contains {total_entries} total entries")
        
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
    except Exception as e:
        print(f"Error in main execution: {e}")
    finally:
        scraper.close()


if __name__ == "__main__":
    main()