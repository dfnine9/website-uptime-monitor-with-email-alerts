#!/usr/bin/env python3
"""
Stock Price Monitor with Email Notifications

This module fetches real-time stock prices using Alpha Vantage API and implements
email notification logic for price alerts. It monitors specified stocks and sends
alerts when price thresholds are met.

Features:
- Fetches stock prices from Alpha Vantage API
- Configurable price alert thresholds
- Email notifications via SMTP
- Error handling and logging
- Self-contained execution

Usage: python script.py
"""

import json
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.request import urlopen
from urllib.parse import urlencode
import time
import os

class StockMonitor:
    def __init__(self):
        # Free Alpha Vantage API key (demo key, replace with your own)
        self.api_key = "demo"
        self.base_url = "https://www.alphavantage.co/query"
        
        # Email configuration
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email_user = os.getenv("EMAIL_USER", "your_email@gmail.com")
        self.email_password = os.getenv("EMAIL_PASS", "your_app_password")
        self.recipient = os.getenv("RECIPIENT_EMAIL", "recipient@gmail.com")
        
        # Stock watchlist with alert thresholds
        self.watchlist = {
            "AAPL": {"upper": 200.00, "lower": 150.00},
            "GOOGL": {"upper": 150.00, "lower": 120.00},
            "TSLA": {"upper": 250.00, "lower": 180.00}
        }
    
    def fetch_stock_price(self, symbol):
        """Fetch current stock price from Alpha Vantage API"""
        try:
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": self.api_key
            }
            
            url = f"{self.base_url}?{urlencode(params)}"
            
            with urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode())
            
            # Extract price from API response
            if "Global Quote" in data:
                price = float(data["Global Quote"]["05. price"])
                change = float(data["Global Quote"]["09. change"])
                change_percent = data["Global Quote"]["10. change percent"].replace("%", "")
                
                return {
                    "symbol": symbol,
                    "price": price,
                    "change": change,
                    "change_percent": change_percent,
                    "success": True
                }
            else:
                print(f"Error: Invalid API response for {symbol}: {data}")
                return {"success": False, "error": "Invalid API response"}
                
        except Exception as e:
            print(f"Error fetching price for {symbol}: {e}")
            return {"success": False, "error": str(e)}
    
    def send_email_alert(self, subject, body):
        """Send email notification"""
        try:
            message = MIMEMultipart()
            message["From"] = self.email_user
            message["To"] = self.recipient
            message["Subject"] = subject
            
            message.attach(MIMEText(body, "plain"))
            
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.email_user, self.email_password)
                server.sendmail(self.email_user, self.recipient, message.as_string())
            
            print(f"Email alert sent: {subject}")
            return True
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def check_price_alerts(self, stock_data):
        """Check if stock price triggers any alerts"""
        if not stock_data["success"]:
            return
        
        symbol = stock_data["symbol"]
        price = stock_data["price"]
        
        if symbol not in self.watchlist:
            return
        
        thresholds = self.watchlist[symbol]
        
        # Check upper threshold
        if price >= thresholds["upper"]:
            subject = f"🚨 {symbol} Price Alert - Above ${thresholds['upper']}"
            body = f"""
Stock Alert: {symbol}
Current Price: ${price:.2f}
Change: ${stock_data['change']:.2f} ({stock_data['change_percent']}%)
Alert Threshold: ${thresholds['upper']:.2f}

The stock has reached your upper alert threshold!
            """
            self.send_email_alert(subject, body)
        
        # Check lower threshold
        elif price <= thresholds["lower"]:
            subject = f"📉 {symbol} Price Alert - Below ${thresholds['lower']}"
            body = f"""
Stock Alert: {symbol}
Current Price: ${price:.2f}
Change: ${stock_data['change']:.2f} ({stock_data['change_percent']}%)
Alert Threshold: ${thresholds['lower']:.2f}

The stock has reached your lower alert threshold!
            """
            self.send_email_alert(subject, body)
    
    def monitor_stocks(self):
        """Main monitoring loop"""
        print("🔍 Stock Price Monitor Started")
        print(f"Monitoring: {', '.join(self.watchlist.keys())}")
        print("-" * 60)
        
        for symbol in self.watchlist:
            try:
                print(f"Fetching data for {symbol}...")
                stock_data = self.fetch_stock_price(symbol)
                
                if stock_data["success"]:
                    price = stock_data["price"]
                    change = stock_data["change"]
                    change_percent = stock_data["change_percent"]
                    
                    # Display current price
                    status_emoji = "🟢" if change >= 0 else "🔴"
                    print(f"{status_emoji} {symbol}: ${price:.2f} "
                          f"({change:+.2f}, {change_percent}%)")
                    
                    # Check for alerts
                    self.check_price_alerts(stock_data)
                    
                else:
                    print(f"❌ Failed to fetch {symbol}: {stock_data.get('error', 'Unknown error')}")
                
                # Rate limiting for free API
                time.sleep(12)  # Alpha Vantage free tier: 5 calls per minute
                
            except KeyboardInterrupt:
                print("\n⏹️  Monitoring stopped by user")
                break
            except Exception as e:
                print(f"❌ Unexpected error monitoring {symbol}: {e}")
                continue
        
        print("\n📊 Stock monitoring completed")

def main():
    """Main execution function"""
    try:
        monitor = StockMonitor()
        monitor.monitor_stocks()
        
    except KeyboardInterrupt:
        print("\n👋 Stock monitor terminated")
    except Exception as e:
        print(f"❌ Critical error: {e}")

if __name__ == "__main__":
    main()