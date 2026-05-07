```python
"""
Configuration File System for Transaction Categorization

This module provides a flexible configuration system that allows users to define:
- Custom categorization rules based on transaction patterns
- Merchant mappings to standardize merchant names and categories
- Hierarchical category structures for organized financial tracking

The system uses JSON configuration files to store rules and mappings,
enabling easy customization without code modifications.

Features:
- Rule-based transaction categorization
- Merchant name normalization and mapping
- Hierarchical category organization
- JSON-based configuration management
- Extensible rule engine for custom logic

Usage: python script.py
"""

import json
import os
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class Transaction:
    """Represents a financial transaction"""
    amount: float
    description: str
    merchant: str = ""
    category: str = ""
    subcategory: str = ""


class ConfigurationManager:
    """Manages JSON configuration files for categorization system"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = config_dir
        self.rules_config = {}
        self.merchant_config = {}
        self.category_config = {}
        self._ensure_config_directory()
        self._load_configurations()
    
    def _ensure_config_directory(self):
        """Create configuration directory if it doesn't exist"""
        try:
            os.makedirs(self.config_dir, exist_ok=True)
        except Exception as e:
            print(f"Error creating config directory: {e}")
    
    def _load_configurations(self):
        """Load all configuration files"""
        try:
            self.rules_config = self._load_config_file("categorization_rules.json", self._get_default_rules())
            self.merchant_config = self._load_config_file("merchant_mappings.json", self._get_default_merchants())
            self.category_config = self._load_config_file("category_hierarchy.json", self._get_default_categories())
        except Exception as e:
            print(f"Error loading configurations: {e}")
    
    def _load_config_file(self, filename: str, default_config: Dict) -> Dict:
        """Load a specific configuration file or create with defaults"""
        filepath = os.path.join(self.config_dir, filename)
        
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Create default configuration file
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2)
                print(f"Created default configuration: {filename}")
                return default_config
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading {filename}: {e}")
            return default_config
    
    def _get_default_rules(self) -> Dict:
        """Return default categorization rules"""
        return {
            "rules": [
                {
                    "id": "grocery_stores",
                    "name": "Grocery Store Detection",
                    "conditions": {
                        "merchant_patterns": [".*grocery.*", ".*market.*", ".*food.*"],
                        "description_patterns": ["groceries", "food shopping"],
                        "amount_range": {"min": 5.0, "max": 500.0}
                    },
                    "category": "Food & Dining",
                    "subcategory": "Groceries",
                    "priority": 10
                },
                {
                    "id": "gas_stations",
                    "name": "Gas Station Detection",
                    "conditions": {
                        "merchant_patterns": [".*shell.*", ".*exxon.*", ".*bp.*", ".*chevron.*"],
                        "description_patterns": ["gas", "fuel", "petroleum"]
                    },
                    "category": "Transportation",
                    "subcategory": "Gas & Fuel",
                    "priority": 15
                },
                {
                    "id": "restaurants",
                    "name": "Restaurant Detection",
                    "conditions": {
                        "merchant_patterns": [".*restaurant.*", ".*cafe.*", ".*bistro.*"],
                        "description_patterns": ["dining", "meal", "takeout"]
                    },
                    "category": "Food & Dining",
                    "subcategory": "Restaurants",
                    "priority": 8
                },
                {
                    "id": "online_shopping",
                    "name": "Online Shopping Detection",
                    "conditions": {
                        "merchant_patterns": ["amazon.*", "ebay.*", ".*online.*"],
                        "description_patterns": ["online purchase", "e-commerce"]
                    },
                    "category": "Shopping",
                    "subcategory": "Online",
                    "priority": 5
                }
            ]
        }
    
    def _get_default_merchants(self) -> Dict:
        """Return default merchant mappings"""
        return {
            "mappings": [
                {
                    "patterns": ["amazon.*", "amzn.*", "amazon.com"],
                    "canonical_name": "Amazon",
                    "category": "Shopping",
                    "subcategory": "Online"
                },
                {
                    "patterns": ["walmart.*", "wal-mart.*", "walmart supercenter"],
                    "canonical_name": "Walmart",
                    "category": "Shopping",
                    "subcategory": "Department Store"
                },
                {
                    "patterns": ["starbucks.*", "sbux.*"],
                    "canonical_name": "Starbucks",
                    "category": "Food & Dining",
                    "subcategory": "Coffee Shops"
                },
                {
                    "patterns": ["shell.*", "shell oil"],
                    "canonical_name": "Shell",
                    "category": "Transportation",
                    "subcategory": "Gas & Fuel"
                },
                {
                    "patterns": ["netflix.*", "netflix.com"],
                    "canonical_name": "Netflix",
                    "category": "Entertainment",
                    "subcategory": "Streaming Services"
                }
            ]
        }
    
    def _get_default_categories(self) -> Dict:
        """Return default category hierarchy"""
        return {
            "hierarchy": {
                "Food & Dining": {
                    "subcategories": [
                        "Groceries",
                        "Restaurants",
                        "Fast Food",
                        "Coffee Shops",
                        "Bars & Nightlife"
                    ],
                    "budget_percentage": 15.0,
                    "color": "#FF6B6B"
                },
                "Transportation": {
                    "subcategories": [
                        "Gas & Fuel",
                        "Public Transportation",
                        "Taxi & Rideshare",
                        "Parking",
                        "Auto Maintenance"
                    ],
                    "budget_percentage": 12.0,
                    "color": "#4ECDC4"
                },
                "Shopping": {
                    "subcategories": [
                        "Online",
                        "Department Store",
                        "Clothing",
                        "Electronics",
                        "Home & Garden"
                    ],
                    "budget_percentage": 10.0,
                    "color": "#45B7D1"
                },
                "Entertainment": {
                    "subcategories": [
                        "Streaming Services",
                        "Movies & Theater",
                        "Games & Hobbies",
                        "Sports & Recreation"
                    ],
                    "budget_percentage": 8.0,
                    "color": "#96CEB4"
                },
                "Bills & Utilities": {
                    "subcategories": [
                        "Electric",
                        "Gas",
                        "Water",
                        "Internet",
                        "Phone",
                        "Insurance"
                    ],
                    "budget_percentage": 25.0,
                    "color": "#FFEAA7"
                },
                "Healthcare": {