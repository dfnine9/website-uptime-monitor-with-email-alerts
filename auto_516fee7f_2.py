```python
#!/usr/bin/env python3
"""
Budget Alert System

A comprehensive budget monitoring and alert system that tracks actual spending against 
predefined budget limits. The system provides real-time notifications via email and 
console output when spending thresholds are exceeded.

Features:
- Configurable budget categories with custom spending limits
- Multiple alert threshold levels (warning, critical)
- Email notifications using SMTP
- Console logging with colored output
- JSON-based configuration for easy customization
- Detailed spending reports and analytics

Usage:
    python script.py

The script will load budget configuration, simulate or load actual spending data,
compare against limits, and trigger appropriate alerts when thresholds are exceeded.
"""

import json
import smtplib
import logging
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import sys
import os


class BudgetAlertSystem:
    """Main budget alert system class."""
    
    def __init__(self, config_file: str = "budget_config.json"):
        """Initialize the budget alert system."""
        self.config_file = config_file
        self.config = self._load_config()
        self.spending_data = {}
        self.alerts_sent = []
        self._setup_logging()
    
    def _load_config(self) -> Dict:
        """Load configuration from JSON file or create default config."""
        default_config = {
            "budget_categories": {
                "groceries": {"limit": 500.0, "warning_threshold": 0.8, "critical_threshold": 0.95},
                "entertainment": {"limit": 200.0, "warning_threshold": 0.75, "critical_threshold": 0.9},
                "utilities": {"limit": 300.0, "warning_threshold": 0.8, "critical_threshold": 0.95},
                "transportation": {"limit": 400.0, "warning_threshold": 0.8, "critical_threshold": 0.9},
                "dining_out": {"limit": 250.0, "warning_threshold": 0.7, "critical_threshold": 0.85}
            },
            "email_settings": {
                "enabled": False,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "sender_email": "budget@example.com",
                "sender_password": "your_app_password",
                "recipient_email": "user@example.com"
            },
            "alert_settings": {
                "console_alerts": True,
                "email_alerts": False,
                "alert_frequency": "daily"
            }
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                print(f"✓ Loaded configuration from {self.config_file}")
                return config
            else:
                with open(self.config_file, 'w') as f:
                    json.dump(default_config, f, indent=2)
                print(f"✓ Created default configuration file: {self.config_file}")
                return default_config
        except Exception as e:
            print(f"⚠ Error loading config, using defaults: {e}")
            return default_config
    
    def _setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('budget_alerts.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_spending_data(self, data_file: str = "spending_data.json") -> None:
        """Load actual spending data from file or generate sample data."""
        try:
            if os.path.exists(data_file):
                with open(data_file, 'r') as f:
                    self.spending_data = json.load(f)
                print(f"✓ Loaded spending data from {data_file}")
            else:
                # Generate sample spending data for demonstration
                self.spending_data = self._generate_sample_spending()
                with open(data_file, 'w') as f:
                    json.dump(self.spending_data, f, indent=2)
                print(f"✓ Generated sample spending data and saved to {data_file}")
        except Exception as e:
            self.logger.error(f"Error loading spending data: {e}")
            self.spending_data = self._generate_sample_spending()
    
    def _generate_sample_spending(self) -> Dict:
        """Generate sample spending data for demonstration."""
        import random
        
        sample_data = {}
        categories = self.config["budget_categories"]
        
        for category, budget_info in categories.items():
            # Generate spending between 60% and 120% of budget limit
            limit = budget_info["limit"]
            spending = round(random.uniform(limit * 0.6, limit * 1.2), 2)
            
            sample_data[category] = {
                "current_spending": spending,
                "transactions": [
                    {
                        "date": (datetime.now() - timedelta(days=i)).isoformat(),
                        "amount": round(random.uniform(10, 100), 2),
                        "description": f"Sample transaction {i+1}"
                    }
                    for i in range(random.randint(3, 8))
                ],
                "last_updated": datetime.now().isoformat()
            }
        
        return sample_data
    
    def check_budget_limits(self) -> List[Dict]:
        """Check all budget categories against spending limits."""
        alerts = []
        
        print("\n" + "="*60)
        print("BUDGET MONITORING REPORT")
        print("="*60)
        print(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        for category, budget_info in self.config["budget_categories"].items():
            try:
                limit = budget_info["limit"]
                warning_threshold = budget_info["warning_threshold"]
                critical_threshold = budget_info["critical_threshold"]
                
                current_spending = self.spending_data.get(category, {}).get("current_spending", 0)
                percentage_used = (current_spending / limit) * 100 if limit > 0 else 0
                
                # Determine alert level
                alert_level = None
                if percentage_used >= (critical_threshold * 100):
                    alert_level = "CRITICAL"
                elif percentage_used >= (warning_threshold * 100):
                    alert_level = "WARNING"
                
                # Create alert if needed
                if alert_level:
                    alert = {
                        "category": category,
                        "level": alert_level,
                        "current_spending": current_spending,
                        "budget_limit": limit,
                        "percentage_used": percentage_used,
                        "amount_remaining": limit - current_spending,
                        "timestamp": datetime.now().isoformat()
                    }
                    alerts.append(alert)
                
                # Console output
                status_icon = "🔴" if alert_level == "CRITICAL" else "🟡" if alert_level == "WARNING" else "🟢"
                print(f"{status_icon} {category.upper().replace('_', ' ')}")
                print(f"   Budget Limit: ${limit:,.2f}")
                print(f"   Current Spending: ${current_spending:,.2f}")
                print(f"   Percentage Used: {percentage_used:.1f}%")
                print(f"   Remaining: ${limit - current_spending:,.2f}")
                if alert_level:
                    print(f"   ⚠ ALERT: {alert_level} threshold exceeded!")
                print()
                
            except Exception as e:
                self.logger.error(f"Error checking budget for {category}: {e}")