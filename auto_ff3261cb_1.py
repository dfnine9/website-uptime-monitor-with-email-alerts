```python
#!/usr/bin/env python3
"""
Financial Transaction Analyzer

This module analyzes spending patterns and detects recurring transactions from financial data.
It creates a configuration file with categorization rules and keyword mappings, then processes
transaction data to identify patterns, categorize expenses, and flag recurring payments.

Features:
- Automatic configuration file generation with customizable rules
- Transaction categorization based on keywords and merchant patterns
- Recurring transaction detection using amount and merchant matching
- Spending pattern analysis with monthly summaries
- JSON-based configuration for easy customization

Usage: python script.py
"""

import json
import csv
import re
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any
import sys
import os


class TransactionAnalyzer:
    def __init__(self, config_file: str = "transaction_config.json"):
        self.config_file = config_file
        self.config = {}
        self.transactions = []
        self.categories = defaultdict(list)
        self.recurring_transactions = []
        
    def create_default_config(self) -> Dict[str, Any]:
        """Create default configuration with categorization rules and keyword mappings."""
        default_config = {
            "categories": {
                "Food & Dining": {
                    "keywords": ["restaurant", "cafe", "pizza", "burger", "starbucks", "mcdonald", 
                               "subway", "domino", "kfc", "taco", "dining", "food", "grubhub", 
                               "doordash", "uber eats"],
                    "patterns": [".*restaurant.*", ".*cafe.*", ".*pizza.*"]
                },
                "Groceries": {
                    "keywords": ["walmart", "target", "kroger", "safeway", "whole foods", 
                               "costco", "grocery", "market", "trader joe", "publix"],
                    "patterns": [".*market.*", ".*grocery.*"]
                },
                "Transportation": {
                    "keywords": ["gas", "fuel", "shell", "exxon", "chevron", "bp", "uber", 
                               "lyft", "taxi", "metro", "bus", "parking", "toll"],
                    "patterns": [".*gas.*", ".*fuel.*", ".*parking.*"]
                },
                "Utilities": {
                    "keywords": ["electric", "water", "gas bill", "internet", "phone", 
                               "cable", "verizon", "att", "comcast", "utility"],
                    "patterns": [".*electric.*", ".*utility.*"]
                },
                "Entertainment": {
                    "keywords": ["netflix", "spotify", "amazon prime", "hulu", "disney", 
                               "movie", "theater", "cinema", "game", "entertainment"],
                    "patterns": [".*entertainment.*", ".*movie.*"]
                },
                "Shopping": {
                    "keywords": ["amazon", "ebay", "store", "shop", "retail", "mall", 
                               "clothing", "shoes", "electronics"],
                    "patterns": [".*shop.*", ".*store.*"]
                },
                "Healthcare": {
                    "keywords": ["hospital", "doctor", "pharmacy", "medical", "health", 
                               "dental", "clinic", "cvs", "walgreens"],
                    "patterns": [".*medical.*", ".*health.*"]
                },
                "Finance": {
                    "keywords": ["bank", "atm", "fee", "interest", "loan", "credit", 
                               "investment", "transfer"],
                    "patterns": [".*bank.*", ".*atm.*"]
                }
            },
            "recurring_detection": {
                "amount_tolerance": 0.05,  # 5% tolerance for amount matching
                "date_window_days": 35,    # Look for transactions within 35 days
                "min_occurrences": 3       # Minimum occurrences to consider recurring
            },
            "analysis_settings": {
                "currency_symbol": "$",
                "date_format": "%Y-%m-%d",
                "exclude_categories": ["Finance"]  # Categories to exclude from spending analysis
            }
        }
        return default_config
    
    def save_config(self) -> None:
        """Save configuration to JSON file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            print(f"✓ Configuration saved to {self.config_file}")
        except Exception as e:
            print(f"✗ Error saving configuration: {e}")
            sys.exit(1)
    
    def load_config(self) -> None:
        """Load configuration from JSON file."""
        try:
            if not os.path.exists(self.config_file):
                print(f"Configuration file not found. Creating default configuration...")
                self.config = self.create_default_config()
                self.save_config()
            else:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                print(f"✓ Configuration loaded from {self.config_file}")
        except Exception as e:
            print(f"✗ Error loading configuration: {e}")
            sys.exit(1)
    
    def generate_sample_data(self) -> List[Dict[str, Any]]:
        """Generate sample transaction data for demonstration."""
        sample_transactions = [
            {"date": "2024-01-15", "description": "STARBUCKS COFFEE #123", "amount": -4.75, "merchant": "Starbucks"},
            {"date": "2024-01-16", "description": "WALMART SUPERCENTER", "amount": -89.32, "merchant": "Walmart"},
            {"date": "2024-01-18", "description": "NETFLIX SUBSCRIPTION", "amount": -15.99, "merchant": "Netflix"},
            {"date": "2024-01-20", "description": "SHELL GAS STATION", "amount": -45.00, "merchant": "Shell"},
            {"date": "2024-02-15", "description": "STARBUCKS COFFEE #123", "amount": -4.75, "merchant": "Starbucks"},
            {"date": "2024-02-16", "description": "WALMART SUPERCENTER", "amount": -92.18, "merchant": "Walmart"},
            {"date": "2024-02-18", "description": "NETFLIX SUBSCRIPTION", "amount": -15.99, "merchant": "Netflix"},
            {"date": "2024-02-22", "description": "AMAZON PURCHASE", "amount": -67.45, "merchant": "Amazon"},
            {"date": "2024-03-15", "description": "STARBUCKS COFFEE #123", "amount": -4.75, "merchant": "Starbucks"},
            {"date": "2024-03-18", "description": "NETFLIX SUBSCRIPTION", "amount": -15.99, "merchant": "Netflix"},
            {"date": "2024-03-20", "description": "ELECTRIC COMPANY", "amount": -125.50, "merchant": "Electric Co"},
            {"date": "2024-03-25", "description": "DOCTOR VISIT", "amount": -150.00, "merchant": "Medical Center"},
        ]
        return sample_transactions
    
    def categorize_transaction(self, transaction: Dict[str, Any]) -> str:
        """Categorize a transaction based on keywords and patterns."""
        description = transaction.get('description', '').lower()
        merchant = transaction.get('merchant', '').lower()
        combined_text = f"{description} {merchant}"
        
        try:
            for category, rules in self.config['categories'].items():
                # Check keywords
                for keyword in rules.get('keywords', []):
                    if keyword.lower() in combined_text:
                        return category
                
                # Check patterns
                for pattern in rules.get('patterns', []):
                    if re.search(pattern.lower(), combined_text):
                        return category
            
            return "Other"
        except Exception as e:
            print(f"Warning: Error categorizing transaction: {e}")
            return "Other"
    
    def detect_recurring_transactions(self) -> List[Dict[str, Any]]: