```python
"""
Email Price Alert System

A self-contained price monitoring system that sends formatted email notifications
when product prices drop to or below target thresholds. Monitors multiple products
and sends detailed alerts with current vs target prices and purchase links.

Usage:
    python script.py

Features:
- Configurable SMTP email settings
- Product price monitoring with customizable targets
- HTML-formatted email alerts with product details
- Error handling and logging
- Self-contained with minimal dependencies
"""

import smtplib
import json
import time
import sys
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urlparse
import re

try:
    import httpx
except ImportError:
    print("Error: httpx not installed. Install with: pip install httpx")
    sys.exit(1)


class PriceAlertSystem:
    def __init__(self, smtp_config: Dict[str, str]):
        """Initialize the price alert system with SMTP configuration."""
        self.smtp_config = smtp_config
        self.products = []
        self.client = httpx.Client(timeout=30.0)
        
    def add_product(self, name: str, url: str, target_price: float, 
                   price_selector: str = None, current_price: float = None):
        """Add a product to monitor."""
        product = {
            'name': name,
            'url': url,
            'target_price': target_price,
            'price_selector': price_selector,
            'current_price': current_price,
            'last_checked': None,
            'alert_sent': False
        }
        self.products.append(product)
        print(f"Added product: {name} (Target: ${target_price})")
    
    def extract_price_from_text(self, text: str) -> Optional[float]:
        """Extract price from text using regex patterns."""
        try:
            # Common price patterns
            patterns = [
                r'\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',  # $123.45, $1,234.56
                r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*\$',  # 123.45$
                r'USD\s*(\d+(?:,\d{3})*(?:\.\d{2})?)', # USD 123.45
                r'(\d+(?:,\d{3})*(?:\.\d{2})?)(?:\s*USD)', # 123.45 USD
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    price_str = match.group(1).replace(',', '')
                    return float(price_str)
            return None
        except (ValueError, AttributeError):
            return None
    
    def check_product_price(self, product: Dict) -> Optional[float]:
        """Check current price for a product."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = self.client.get(product['url'], headers=headers, follow_redirects=True)
            response.raise_for_status()
            
            # If we have a current_price set (for demo), use it
            if product.get('current_price') is not None:
                return product['current_price']
            
            # Try to extract price from page content
            price = self.extract_price_from_text(response.text)
            return price
            
        except Exception as e:
            print(f"Error checking price for {product['name']}: {e}")
            return None
    
    def create_email_content(self, product: Dict, current_price: float) -> str:
        """Create HTML email content for price alert."""
        savings = product['target_price'] - current_price if current_price < product['target_price'] else 0
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background-color: #28a745; color: white; padding: 20px; border-radius: 8px 8px 0 0; margin: -20px -20px 20px -20px; }}
                .product-name {{ font-size: 24px; font-weight: bold; margin-bottom: 10px; }}
                .price-section {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                .current-price {{ font-size: 28px; font-weight: bold; color: #28a745; }}
                .target-price {{ font-size: 18px; color: #6c757d; text-decoration: line-through; }}
                .savings {{ font-size: 18px; color: #dc3545; font-weight: bold; }}
                .btn {{ display: inline-block; background-color: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold; margin: 15px 0; }}
                .btn:hover {{ background-color: #0056b3; }}
                .details {{ background-color: #e9ecef; padding: 15px; border-radius: 5px; margin: 15px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Price Alert Triggered!</h1>
                    <p>Your target price has been reached</p>
                </div>
                
                <div class="product-name">{product['name']}</div>
                
                <div class="price-section">
                    <div class="current-price">${current_price:.2f}</div>
                    <div class="target-price">Target: ${product['target_price']:.2f}</div>
                    {f'<div class="savings">You save: ${savings:.2f}</div>' if savings > 0 else ''}
                </div>
                
                <a href="{product['url']}" class="btn">🛒 Buy Now</a>
                
                <div class="details">
                    <h3>Details:</h3>
                    <p><strong>Product:</strong> {product['name']}</p>
                    <p><strong>Current Price:</strong> ${current_price:.2f}</p>
                    <p><strong>Target Price:</strong> ${product['target_price']:.2f}</p>
                    <p><strong>Direct Link:</strong> <a href="{product['url']}">{product['url'][:50]}...</a></p>
                    <p><strong>Alert Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <p style="color: #6c757d; font-size: 12px; margin-top: 20px;">
                    This alert was generated by your Price Monitoring System. 
                    Prices may change rapidly, so act quickly if you're interested.
                </p>
            </div>
        </body>
        </html>
        """
        return html_content
    
    def send_email_alert(self, product: Dict, current_price: float) -> bool:
        """Send email alert for price drop."""
        try:
            msg = MimeMultipart('alternative')
            msg['Subject'] = f"🔔 Price Alert: