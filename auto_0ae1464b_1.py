```python
"""
Transaction Categorization System

This module provides a keyword-based transaction categorization system that automatically
classifies financial transactions into predefined categories (food, transport, utilities, etc.)
based on description text matching. The system uses configurable keyword rules stored in
JSON format and provides flexible matching capabilities.

Features:
- Predefined categories with customizable keyword rules
- Case-insensitive keyword matching
- JSON configuration file for easy rule management
- Transaction classification with confidence scoring
- Batch processing capabilities
- Comprehensive error handling

Usage:
    python script.py

The script will create a sample configuration file, demonstrate transaction categorization,
and save updated rules to 'transaction_categories.json'.
"""

import json
import re
from typing import Dict, List, Tuple, Optional
import os


class TransactionCategorizer:
    """
    A keyword-based transaction categorization system that matches transaction
    descriptions to predefined categories using configurable rules.
    """
    
    def __init__(self, config_file: str = "transaction_categories.json"):
        """
        Initialize the categorizer with a configuration file.
        
        Args:
            config_file: Path to the JSON configuration file
        """
        self.config_file = config_file
        self.categories = {}
        self.load_or_create_config()
    
    def load_or_create_config(self) -> None:
        """Load configuration from file or create default configuration."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.categories = json.load(f)
                print(f"Loaded configuration from {self.config_file}")
            else:
                self.create_default_config()
                print(f"Created default configuration in {self.config_file}")
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading configuration: {e}")
            print("Creating default configuration...")
            self.create_default_config()
    
    def create_default_config(self) -> None:
        """Create default category configuration with predefined rules."""
        self.categories = {
            "food": {
                "keywords": [
                    "restaurant", "cafe", "coffee", "pizza", "burger", "food",
                    "grocery", "supermarket", "deli", "bakery", "bistro",
                    "mcdonald", "subway", "starbucks", "dunkin", "taco",
                    "chinese", "italian", "mexican", "thai", "sushi",
                    "market", "walmart", "target", "costco", "whole foods"
                ],
                "description": "Food and dining expenses"
            },
            "transport": {
                "keywords": [
                    "gas", "fuel", "station", "uber", "lyft", "taxi", "bus",
                    "train", "subway", "metro", "parking", "toll", "airline",
                    "flight", "car rental", "automotive", "mechanic", "tire",
                    "shell", "exxon", "chevron", "bp", "mobil", "citgo"
                ],
                "description": "Transportation and vehicle expenses"
            },
            "utilities": {
                "keywords": [
                    "electric", "electricity", "gas company", "water", "sewer",
                    "internet", "cable", "phone", "cellular", "verizon",
                    "at&t", "comcast", "xfinity", "spectrum", "utility",
                    "energy", "power", "heating", "cooling"
                ],
                "description": "Utility bills and services"
            },
            "shopping": {
                "keywords": [
                    "amazon", "ebay", "store", "mall", "retail", "clothing",
                    "shoes", "electronics", "best buy", "apple", "nike",
                    "department", "pharmacy", "cvs", "walgreens", "shopping"
                ],
                "description": "Retail and online shopping"
            },
            "healthcare": {
                "keywords": [
                    "doctor", "hospital", "medical", "pharmacy", "dental",
                    "vision", "health", "clinic", "medicare", "insurance",
                    "prescription", "medicine", "therapy"
                ],
                "description": "Healthcare and medical expenses"
            },
            "entertainment": {
                "keywords": [
                    "movie", "theater", "cinema", "netflix", "spotify", "hulu",
                    "disney", "gaming", "xbox", "playstation", "steam",
                    "concert", "show", "ticket", "entertainment", "music"
                ],
                "description": "Entertainment and recreation"
            },
            "financial": {
                "keywords": [
                    "bank", "atm", "fee", "interest", "loan", "credit card",
                    "payment", "transfer", "deposit", "withdrawal", "charge"
                ],
                "description": "Banking and financial services"
            },
            "other": {
                "keywords": [],
                "description": "Uncategorized transactions"
            }
        }
        self.save_config()
    
    def save_config(self) -> None:
        """Save current configuration to JSON file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.categories, f, indent=2, ensure_ascii=False)
            print(f"Configuration saved to {self.config_file}")
        except IOError as e:
            print(f"Error saving configuration: {e}")
    
    def categorize_transaction(self, description: str, amount: float = 0.0) -> Tuple[str, float]:
        """
        Categorize a transaction based on its description.
        
        Args:
            description: Transaction description text
            amount: Transaction amount (optional, for future use)
            
        Returns:
            Tuple of (category_name, confidence_score)
        """
        if not description or not isinstance(description, str):
            return "other", 0.0
        
        description_lower = description.lower()
        best_category = "other"
        best_score = 0.0
        
        try:
            for category, config in self.categories.items():
                if category == "other":
                    continue
                
                keywords = config.get("keywords", [])
                matches = 0
                total_keywords = len(keywords)
                
                if total_keywords == 0:
                    continue
                
                for keyword in keywords:
                    if keyword.lower() in description_lower:
                        matches += 1
                
                # Calculate confidence score
                if matches > 0:
                    score = matches / total_keywords
                    if score > best_score:
                        best_score = score
                        best_category = category
            
            return best_category, best_score
            
        except Exception as e:
            print(f"Error during categorization: {e}")
            return "other", 0.0
    
    def add_keyword(self, category: str, keyword: str) -> bool:
        """
        Add a keyword to a category.
        
        Args:
            category: Target category name
            keyword: Keyword to add
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if category not in self.categories:
                print(f"Category '{category}' not found")
                return False
            
            if keyword.lower() not in [k.lower() for k in self.categories[category]["keywords"]]:
                self.categories[category]["keywords"].append(keyword.lower())
                self.save_config()
                print(f"Added keyword '{keyword}' to category '{category}'")
                return True
            else:
                print(f"Keyword '{keyword}' already exists in category '{category}'")
                return False
                
        except Exception as e:
            print(f"Error adding keyword: {e}")
            return False
    
    def remove_keyword(self, category: str, keyword: str) -> bool:
        """
        Remove a keyword from a category.
        
        Args:
            category: Target category name
            keyword: Keyword to remove
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if category not in self.categories:
                print(f"Category '{category}' not found")