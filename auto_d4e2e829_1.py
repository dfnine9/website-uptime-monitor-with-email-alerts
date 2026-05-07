```python
"""
Expense Management Configuration System

This module provides a comprehensive configuration file system for expense management
that allows users to define custom categorization rules, add expense categories,
and set spending thresholds for budget alerts. The system uses JSON for configuration
storage and provides a command-line interface for managing expense tracking rules.

Features:
- Custom categorization rules based on keywords and patterns
- Dynamic expense category management
- Configurable spending thresholds and budget alerts
- JSON-based configuration persistence
- Command-line interface for easy interaction

Usage:
    python script.py

The script will create a default configuration file and provide options to:
- Add new expense categories
- Define categorization rules
- Set spending thresholds
- View current configuration
- Test categorization rules
"""

import json
import os
import re
from typing import Dict, List, Any, Optional
from datetime import datetime


class ExpenseConfigManager:
    """Manages expense categorization rules and budget thresholds."""
    
    def __init__(self, config_file: str = "expense_config.json"):
        self.config_file = config_file
        self.config = self._load_or_create_config()
    
    def _load_or_create_config(self) -> Dict[str, Any]:
        """Load existing config or create default configuration."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            else:
                return self._create_default_config()
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading config: {e}")
            print("Creating new default configuration...")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default configuration structure."""
        default_config = {
            "categories": {
                "food": {
                    "name": "Food & Dining",
                    "keywords": ["restaurant", "cafe", "food", "grocery", "dining", "pizza", "burger"],
                    "patterns": [r".*restaurant.*", r".*cafe.*", r".*food.*"],
                    "threshold": 500.00,
                    "color": "#FF6B6B"
                },
                "transportation": {
                    "name": "Transportation",
                    "keywords": ["gas", "fuel", "uber", "lyft", "taxi", "bus", "metro", "parking"],
                    "patterns": [r".*gas.*station.*", r".*fuel.*", r".*parking.*"],
                    "threshold": 300.00,
                    "color": "#4ECDC4"
                },
                "entertainment": {
                    "name": "Entertainment",
                    "keywords": ["movie", "theater", "netflix", "spotify", "game", "concert"],
                    "patterns": [r".*theater.*", r".*entertainment.*"],
                    "threshold": 200.00,
                    "color": "#45B7D1"
                },
                "shopping": {
                    "name": "Shopping",
                    "keywords": ["amazon", "target", "walmart", "mall", "store", "clothing"],
                    "patterns": [r".*amazon.*", r".*store.*"],
                    "threshold": 400.00,
                    "color": "#96CEB4"
                },
                "utilities": {
                    "name": "Utilities",
                    "keywords": ["electric", "water", "internet", "phone", "cable"],
                    "patterns": [r".*electric.*", r".*utility.*"],
                    "threshold": 250.00,
                    "color": "#FFEAA7"
                }
            },
            "global_settings": {
                "default_category": "uncategorized",
                "case_sensitive": False,
                "alert_threshold_percentage": 0.8,
                "monthly_budget": 2000.00,
                "currency": "USD"
            },
            "alert_rules": {
                "email_notifications": False,
                "console_alerts": True,
                "alert_frequency": "immediate"
            },
            "created_date": datetime.now().isoformat(),
            "version": "1.0"
        }
        self._save_config(default_config)
        return default_config
    
    def _save_config(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Save configuration to file."""
        try:
            config_to_save = config or self.config
            config_to_save["last_modified"] = datetime.now().isoformat()
            
            with open(self.config_file, 'w') as f:
                json.dump(config_to_save, f, indent=2)
            print(f"Configuration saved to {self.config_file}")
        except IOError as e:
            print(f"Error saving configuration: {e}")
    
    def add_category(self, category_id: str, name: str, keywords: List[str], 
                    patterns: List[str] = None, threshold: float = 0.0, 
                    color: str = "#DDDDDD") -> None:
        """Add a new expense category."""
        try:
            if category_id in self.config["categories"]:
                print(f"Category '{category_id}' already exists. Use update_category to modify.")
                return
            
            self.config["categories"][category_id] = {
                "name": name,
                "keywords": keywords,
                "patterns": patterns or [],
                "threshold": threshold,
                "color": color
            }
            self._save_config()
            print(f"Category '{name}' added successfully with ID '{category_id}'")
        except Exception as e:
            print(f"Error adding category: {e}")
    
    def update_category(self, category_id: str, **kwargs) -> None:
        """Update an existing category."""
        try:
            if category_id not in self.config["categories"]:
                print(f"Category '{category_id}' not found.")
                return
            
            for key, value in kwargs.items():
                if key in self.config["categories"][category_id]:
                    self.config["categories"][category_id][key] = value
                    print(f"Updated {key} for category '{category_id}'")
                else:
                    print(f"Invalid field '{key}' for category update")
            
            self._save_config()
        except Exception as e:
            print(f"Error updating category: {e}")
    
    def set_spending_threshold(self, category_id: str, threshold: float) -> None:
        """Set spending threshold for a category."""
        try:
            if category_id not in self.config["categories"]:
                print(f"Category '{category_id}' not found.")
                return
            
            self.config["categories"][category_id]["threshold"] = threshold
            self._save_config()
            print(f"Spending threshold for '{category_id}' set to ${threshold:.2f}")
        except Exception as e:
            print(f"Error setting threshold: {e}")
    
    def add_categorization_rule(self, category_id: str, keywords: List[str] = None, 
                               patterns: List[str] = None) -> None:
        """Add new categorization rules to an existing category."""
        try:
            if category_id not in self.config["categories"]:
                print(f"Category '{category_id}' not found.")
                return
            
            if keywords:
                self.config["categories"][category_id]["keywords"].extend(keywords)
                print(f"Added keywords {keywords} to category '{category_id}'")
            
            if patterns:
                self.config["categories"][category_id]["patterns"].extend(patterns)
                print(f"Added patterns {patterns} to category '{category_id}'")
            
            self._save_config()
        except Exception as e:
            print(f"Error adding categorization rule: {e}")
    
    def categorize_expense(self, description: str, amount: float = 0.0) -> Dict[str, Any]:
        """Categorize an expense based on description."""
        try:
            description_lower = description.lower() if not self.config["global_settings"]["case_sensitive"]