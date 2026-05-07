```python
"""
Email Notification Module for Price Threshold Alerts

This module monitors stock prices and sends SMTP email alerts when specified
price thresholds are breached. It fetches real-time stock data and compares
against predefined thresholds, sending formatted email notifications with
stock symbol, current price, threshold type, and timestamp.

Features:
- Real-time stock price monitoring
- SMTP email notifications
- Configurable price thresholds
- Error handling and logging
- Self-contained with minimal dependencies
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json
import time
import sys

# Mock stock data for demonstration (replace with real API in production)
MOCK_STOCK_DATA = {
    "AAPL": 175.50,
    "GOOGL": 142.30,
    "TSLA": 245.67,
    "MSFT": 378.90,
    "AMZN": 145.23
}

class StockPriceMonitor:
    def __init__(self, smtp_server="smtp.gmail.com", smtp_port=587):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.thresholds = {}
        
    def add_threshold(self, symbol, threshold_price, threshold_type, email_config):
        """Add a price threshold to monitor"""
        if symbol not in self.thresholds:
            self.thresholds[symbol] = []
        
        self.thresholds[symbol].append({
            "price": threshold_price,
            "type": threshold_type,  # "above" or "below"
            "email_config": email_config,
            "triggered": False
        })
        
    def get_stock_price(self, symbol):
        """Get current stock price (mock implementation)"""
        try:
            # In production, replace with real API call
            return MOCK_STOCK_DATA.get(symbol, 0.0)
        except Exception as e:
            print(f"Error fetching price for {symbol}: {e}")
            return None
            
    def send_email_alert(self, symbol, current_price, threshold_info):
        """Send SMTP email alert for threshold breach"""
        try:
            email_config = threshold_info["email_config"]
            
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = f"Price Alert: {symbol} Threshold Breached"
            message["From"] = email_config["sender_email"]
            message["To"] = email_config["recipient_email"]
            
            # Create timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Email body
            text = f"""
Price Alert Notification

Stock Symbol: {symbol}
Current Price: ${current_price:.2f}
Threshold Type: {threshold_info['type']}
Threshold Price: ${threshold_info['price']:.2f}
Timestamp: {timestamp}

This is an automated notification from your stock price monitoring system.
            """
            
            html = f"""
<html>
  <body>
    <h2>Price Alert Notification</h2>
    <table border="1" cellpadding="5">
      <tr><td><strong>Stock Symbol</strong></td><td>{symbol}</td></tr>
      <tr><td><strong>Current Price</strong></td><td>${current_price:.2f}</td></tr>
      <tr><td><strong>Threshold Type</strong></td><td>{threshold_info['type']}</td></tr>
      <tr><td><strong>Threshold Price</strong></td><td>${threshold_info['price']:.2f}</td></tr>
      <tr><td><strong>Timestamp</strong></td><td>{timestamp}</td></tr>
    </table>
    <p><em>This is an automated notification from your stock price monitoring system.</em></p>
  </body>
</html>
            """
            
            # Attach parts
            part1 = MIMEText(text, "plain")
            part2 = MIMEText(html, "html")
            message.attach(part1)
            message.attach(part2)
            
            # Create secure connection and send email
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(email_config["sender_email"], email_config["app_password"])
                text = message.as_string()
                server.sendmail(
                    email_config["sender_email"], 
                    email_config["recipient_email"], 
                    text
                )
                
            print(f"✓ Email alert sent for {symbol} at ${current_price:.2f}")
            return True
            
        except Exception as e:
            print(f"✗ Failed to send email alert for {symbol}: {e}")
            return False
            
    def check_thresholds(self):
        """Check all monitored symbols for threshold breaches"""
        alerts_sent = 0
        
        for symbol, threshold_list in self.thresholds.items():
            try:
                current_price = self.get_stock_price(symbol)
                
                if current_price is None:
                    continue
                    
                print(f"Checking {symbol}: ${current_price:.2f}")
                
                for threshold_info in threshold_list:
                    if threshold_info["triggered"]:
                        continue
                        
                    threshold_price = threshold_info["price"]
                    threshold_type = threshold_info["type"]
                    
                    # Check if threshold is breached
                    breach_detected = False
                    
                    if threshold_type == "above" and current_price > threshold_price:
                        breach_detected = True
                    elif threshold_type == "below" and current_price < threshold_price:
                        breach_detected = True
                        
                    if breach_detected:
                        print(f"⚠️  Threshold breached for {symbol}!")
                        print(f"   Current: ${current_price:.2f}, Threshold: {threshold_type} ${threshold_price:.2f}")
                        
                        # Send email alert
                        if self.send_email_alert(symbol, current_price, threshold_info):
                            threshold_info["triggered"] = True
                            alerts_sent += 1
                            
            except Exception as e:
                print(f"Error checking thresholds for {symbol}: {e}")
                
        return alerts_sent

def main():
    """Main function to demonstrate the price monitoring system"""
    print("Stock Price Threshold Monitor Starting...")
    print("=" * 50)
    
    try:
        # Initialize monitor
        monitor = StockPriceMonitor()
        
        # Email configuration (replace with your actual email settings)
        email_config = {
            "sender_email": "your_email@gmail.com",
            "app_password": "your_app_password",  # Use app password for Gmail
            "recipient_email": "recipient@gmail.com"
        }
        
        # Add some example thresholds
        monitor.add_threshold("AAPL", 180.00, "above", email_config)
        monitor.add_threshold("AAPL", 170.00, "below", email_config)
        monitor.add_threshold("GOOGL", 150.00, "above", email_config)
        monitor.add_threshold("TSLA", 240.00, "below", email_config)
        
        print("Configured thresholds:")
        for symbol, thresholds in monitor.thresholds.items():
            for t in thresholds:
                print(f"  {symbol}: {t['type']} ${t['price']:.2f}")
        
        print("\nStarting price monitoring...")
        print("-" * 30)
        
        # Monitor prices (single check for demo)
        alerts_sent = monitor.check_thresholds()
        
        print("-" * 30)
        print(f"Monitoring complete. Alerts sent: {alerts_sent}")
        
        # Show current prices