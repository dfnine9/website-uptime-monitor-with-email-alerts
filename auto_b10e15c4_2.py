```python
"""
Expense Tracker Configuration System

A self-contained Python application that provides a comprehensive configuration system
for expense tracking with customizable categories, keywords, and spending alerts.

Features:
- Interactive configuration management for expense categories
- Customizable keyword mapping for automatic expense categorization
- Spending threshold alerts with notification system
- JSON-based persistent configuration storage
- Command-line interface for easy interaction

Usage: python script.py
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any
import re


class ExpenseConfigManager:
    """Manages expense tracking configuration including categories, keywords, and alerts."""
    
    def __init__(self, config_file: str = "expense_config.json"):
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file or create default config."""
        default_config = {
            "categories": {
                "food": {
                    "keywords": ["restaurant", "grocery", "coffee", "lunch", "dinner", "fast food", "delivery"],
                    "threshold": 500.00,
                    "alert_enabled": True
                },
                "transportation": {
                    "keywords": ["gas", "fuel", "uber", "lyft", "taxi", "bus", "train", "parking"],
                    "threshold": 300.00,
                    "alert_enabled": True
                },
                "utilities": {
                    "keywords": ["electric", "water", "gas bill", "internet", "phone", "cable"],
                    "threshold": 200.00,
                    "alert_enabled": True
                },
                "entertainment": {
                    "keywords": ["movie", "theater", "netflix", "spotify", "games", "concert"],
                    "threshold": 150.00,
                    "alert_enabled": False
                },
                "shopping": {
                    "keywords": ["amazon", "walmart", "target", "mall", "clothes", "electronics"],
                    "threshold": 400.00,
                    "alert_enabled": True
                }
            },
            "global_settings": {
                "currency": "USD",
                "alert_frequency": "monthly",
                "email_notifications": False,
                "created_date": datetime.now().isoformat()
            },
            "spending_history": {}
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                # Merge with defaults to ensure all required keys exist
                for key in default_config:
                    if key not in loaded_config:
                        loaded_config[key] = default_config[key]
                return loaded_config
            else:
                return default_config
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading config: {e}. Using default configuration.")
            return default_config
    
    def _save_config(self) -> None:
        """Save current configuration to JSON file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            print(f"Configuration saved to {self.config_file}")
        except IOError as e:
            print(f"Error saving configuration: {e}")
    
    def add_category(self, category_name: str, keywords: List[str], 
                    threshold: float, alert_enabled: bool = True) -> None:
        """Add a new expense category with keywords and threshold."""
        try:
            category_name = category_name.lower().strip()
            if not category_name:
                raise ValueError("Category name cannot be empty")
            
            if not keywords:
                raise ValueError("At least one keyword is required")
            
            if threshold < 0:
                raise ValueError("Threshold must be non-negative")
            
            # Clean and validate keywords
            cleaned_keywords = [kw.lower().strip() for kw in keywords if kw.strip()]
            
            self.config["categories"][category_name] = {
                "keywords": cleaned_keywords,
                "threshold": float(threshold),
                "alert_enabled": alert_enabled
            }
            
            print(f"✓ Category '{category_name}' added successfully")
            print(f"  Keywords: {', '.join(cleaned_keywords)}")
            print(f"  Threshold: ${threshold:.2f}")
            print(f"  Alerts: {'Enabled' if alert_enabled else 'Disabled'}")
            
        except (ValueError, TypeError) as e:
            print(f"Error adding category: {e}")
    
    def update_category_keywords(self, category_name: str, keywords: List[str], 
                               action: str = "replace") -> None:
        """Update keywords for an existing category."""
        try:
            category_name = category_name.lower().strip()
            if category_name not in self.config["categories"]:
                raise ValueError(f"Category '{category_name}' does not exist")
            
            cleaned_keywords = [kw.lower().strip() for kw in keywords if kw.strip()]
            if not cleaned_keywords:
                raise ValueError("At least one valid keyword is required")
            
            current_keywords = self.config["categories"][category_name]["keywords"]
            
            if action == "replace":
                self.config["categories"][category_name]["keywords"] = cleaned_keywords
                print(f"✓ Keywords for '{category_name}' replaced")
            elif action == "add":
                new_keywords = list(set(current_keywords + cleaned_keywords))
                self.config["categories"][category_name]["keywords"] = new_keywords
                print(f"✓ Keywords added to '{category_name}'")
            elif action == "remove":
                updated_keywords = [kw for kw in current_keywords if kw not in cleaned_keywords]
                if not updated_keywords:
                    raise ValueError("Cannot remove all keywords from category")
                self.config["categories"][category_name]["keywords"] = updated_keywords
                print(f"✓ Keywords removed from '{category_name}'")
            else:
                raise ValueError("Action must be 'replace', 'add', or 'remove'")
            
            print(f"  Current keywords: {', '.join(self.config['categories'][category_name]['keywords'])}")
            
        except (ValueError, KeyError) as e:
            print(f"Error updating keywords: {e}")
    
    def set_spending_threshold(self, category_name: str, threshold: float, 
                             alert_enabled: Optional[bool] = None) -> None:
        """Set spending threshold and alert status for a category."""
        try:
            category_name = category_name.lower().strip()
            if category_name not in self.config["categories"]:
                raise ValueError(f"Category '{category_name}' does not exist")
            
            if threshold < 0:
                raise ValueError("Threshold must be non-negative")
            
            self.config["categories"][category_name]["threshold"] = float(threshold)
            
            if alert_enabled is not None:
                self.config["categories"][category_name]["alert_enabled"] = alert_enabled
            
            print(f"✓ Threshold for '{category_name}' set to ${threshold:.2f}")
            alert_status = self.config["categories"][category_name]["alert_enabled"]
            print(f"  Alerts: {'Enabled' if alert_status else 'Disabled'}")
            
        except (ValueError, TypeError) as e:
            print(f"Error setting threshold: {e}")
    
    def categorize_expense(self, description: str) -> Optional[str]:
        """Automatically categorize an expense based on description keywords."""
        try:
            description_lower = description.lower()
            
            # Score each category based on keyword matches
            category_scores = {}
            for category, details in self.config["categories"].items():
                score = 0
                for keyword in details["keywords"]:
                    if keyword in description_lower:
                        # Longer keywords get higher scores
                        score += len(keyword)
                
                if score > 0:
                    category_scores[category] = score