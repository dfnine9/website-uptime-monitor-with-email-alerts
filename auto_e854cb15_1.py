```python
"""
Transaction Categorization Configuration System

This module provides a flexible configuration system for categorizing financial transactions.
Users can customize categorization rules through YAML configuration files, including:
- Custom keywords for each category
- Amount thresholds for automatic categorization
- Merchant name mappings for brand recognition
- Category priorities and fallback rules

The system supports dynamic loading of configuration files and real-time updates
to categorization logic without code changes.
"""

import json
import os
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class CategoryRule:
    """Represents a single categorization rule"""
    name: str
    keywords: List[str]
    merchant_patterns: List[str]
    amount_min: Optional[float] = None
    amount_max: Optional[float] = None
    priority: int = 0
    case_sensitive: bool = False


@dataclass
class ConfigurationSettings:
    """Main configuration settings structure"""
    categories: List[CategoryRule]
    merchant_mappings: Dict[str, str]
    default_category: str = "Other"
    amount_thresholds: Dict[str, Dict[str, float]] = None


class ConfigurationManager:
    """Manages transaction categorization configuration"""
    
    def __init__(self, config_file: str = "categorization_config.json"):
        self.config_file = config_file
        self.config: Optional[ConfigurationSettings] = None
        self.load_configuration()
    
    def create_default_config(self) -> ConfigurationSettings:
        """Create a default configuration with common categories"""
        try:
            default_categories = [
                CategoryRule(
                    name="Groceries",
                    keywords=["grocery", "market", "food", "supermarket"],
                    merchant_patterns=["walmart", "kroger", "safeway", "whole foods"],
                    priority=1
                ),
                CategoryRule(
                    name="Gas",
                    keywords=["gas", "fuel", "petrol", "station"],
                    merchant_patterns=["shell", "exxon", "chevron", "bp"],
                    amount_max=200.0,
                    priority=2
                ),
                CategoryRule(
                    name="Restaurants",
                    keywords=["restaurant", "cafe", "diner", "bar", "pub"],
                    merchant_patterns=["mcdonald", "starbucks", "subway"],
                    priority=1
                ),
                CategoryRule(
                    name="Utilities",
                    keywords=["electric", "water", "gas bill", "internet", "phone"],
                    merchant_patterns=["pge", "comcast", "verizon", "att"],
                    amount_min=20.0,
                    amount_max=500.0,
                    priority=3
                ),
                CategoryRule(
                    name="Entertainment",
                    keywords=["movie", "theater", "netflix", "spotify", "game"],
                    merchant_patterns=["netflix", "spotify", "steam", "amazon prime"],
                    priority=1
                ),
                CategoryRule(
                    name="Healthcare",
                    keywords=["medical", "doctor", "pharmacy", "hospital", "clinic"],
                    merchant_patterns=["cvs", "walgreens", "kaiser"],
                    priority=2
                ),
                CategoryRule(
                    name="Transportation",
                    keywords=["uber", "lyft", "taxi", "bus", "train", "metro"],
                    merchant_patterns=["uber", "lyft", "metro"],
                    amount_max=100.0,
                    priority=2
                ),
                CategoryRule(
                    name="Shopping",
                    keywords=["amazon", "target", "mall", "store", "retail"],
                    merchant_patterns=["amazon", "target", "bestbuy", "costco"],
                    priority=0
                )
            ]
            
            merchant_mappings = {
                "amzn": "Amazon",
                "wmt": "Walmart", 
                "tgt": "Target",
                "costco": "Costco",
                "wholefds": "Whole Foods",
                "starbucks": "Starbucks",
                "mcdonalds": "McDonald's",
                "in-n-out": "In-N-Out",
                "chevron": "Chevron",
                "shell": "Shell",
                "exxonmobil": "ExxonMobil",
                "bp": "BP",
                "netflix": "Netflix",
                "spotify": "Spotify",
                "uber": "Uber",
                "lyft": "Lyft"
            }
            
            amount_thresholds = {
                "large_purchase": {"min": 500.0},
                "small_purchase": {"max": 10.0},
                "medium_purchase": {"min": 10.0, "max": 500.0}
            }
            
            return ConfigurationSettings(
                categories=default_categories,
                merchant_mappings=merchant_mappings,
                amount_thresholds=amount_thresholds
            )
        except Exception as e:
            print(f"Error creating default configuration: {e}")
            raise
    
    def save_configuration(self, config: ConfigurationSettings = None) -> None:
        """Save configuration to file"""
        try:
            config_to_save = config or self.config
            if not config_to_save:
                raise ValueError("No configuration to save")
            
            # Convert dataclasses to dictionaries for JSON serialization
            config_dict = {
                "categories": [asdict(cat) for cat in config_to_save.categories],
                "merchant_mappings": config_to_save.merchant_mappings,
                "default_category": config_to_save.default_category,
                "amount_thresholds": config_to_save.amount_thresholds or {}
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config_dict, f, indent=2)
            
            print(f"Configuration saved to {self.config_file}")
        except Exception as e:
            print(f"Error saving configuration: {e}")
            raise
    
    def load_configuration(self) -> None:
        """Load configuration from file or create default"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config_dict = json.load(f)
                
                # Convert dictionaries back to dataclasses
                categories = [CategoryRule(**cat_dict) for cat_dict in config_dict.get("categories", [])]
                
                self.config = ConfigurationSettings(
                    categories=categories,
                    merchant_mappings=config_dict.get("merchant_mappings", {}),
                    default_category=config_dict.get("default_category", "Other"),
                    amount_thresholds=config_dict.get("amount_thresholds", {})
                )
                print(f"Configuration loaded from {self.config_file}")
            else:
                print(f"Configuration file {self.config_file} not found. Creating default configuration.")
                self.config = self.create_default_config()
                self.save_configuration()
        except Exception as e:
            print(f"Error loading configuration: {e}")
            print("Creating default configuration...")
            self.config = self.create_default_config()
            self.save_configuration()
    
    def add_category(self, name: str, keywords: List[str], merchant_patterns: List[str] = None, 
                    amount_min: float = None, amount_max: float = None, priority: int = 0) -> None:
        """Add a new category rule"""
        try:
            if not self.config:
                raise ValueError("Configuration not loaded")
            
            # Check if category already exists
            for existing_cat in self.config.categories:
                if existing_cat.name.lower() == name.lower():
                    raise ValueError(f"Category '{name}' already exists")
            
            new_category = CategoryRule(
                name=name,
                keywords=keywords,
                merchant_patterns=merchant_patterns or [],
                amount_min=amount_min,
                amount_max=amount_max,
                priority=priority