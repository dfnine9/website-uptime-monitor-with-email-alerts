```python
"""
Bank Transaction Categorization System

This module provides a comprehensive system for categorizing bank transactions based on
customizable rules, regex patterns, and merchant mappings. It includes:

- Configuration file management for category rules
- Regex pattern matching for transaction descriptions
- Merchant-specific mappings for accurate categorization
- Default categorization fallbacks
- Transaction processing with confidence scoring

The system is designed to be easily customizable through JSON configuration files
that users can modify to improve categorization accuracy for their specific
banking formats and transaction patterns.
"""

import json
import re
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
import sys


class TransactionCategorizer:
    def __init__(self, config_file: str = "categorization_config.json"):
        self.config_file = config_file
        self.config = self._load_or_create_config()
        self.compiled_patterns = self._compile_patterns()
    
    def _load_or_create_config(self) -> Dict[str, Any]:
        """Load existing config or create default configuration."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                print(f"Loaded configuration from {self.config_file}")
                return config
            else:
                config = self._create_default_config()
                self._save_config(config)
                print(f"Created default configuration file: {self.config_file}")
                return config
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading config: {e}")
            print("Using default configuration...")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default categorization configuration."""
        return {
            "categories": {
                "food_dining": {
                    "name": "Food & Dining",
                    "keywords": ["restaurant", "cafe", "pizza", "burger", "food", "dining", "kitchen", "grill", "bistro"],
                    "regex_patterns": [
                        r".*(?:restaurant|cafe|pizza|burger|food|dining).*",
                        r".*(?:mcdonald|kfc|subway|starbucks|domino).*",
                        r".*(?:kitchen|grill|bistro|eatery).*"
                    ],
                    "merchant_mappings": {
                        "MCDONALD'S": "food_dining",
                        "STARBUCKS": "food_dining",
                        "SUBWAY": "food_dining",
                        "PIZZA HUT": "food_dining",
                        "KFC": "food_dining"
                    }
                },
                "groceries": {
                    "name": "Groceries",
                    "keywords": ["grocery", "supermarket", "market", "walmart", "target", "costco", "safeway"],
                    "regex_patterns": [
                        r".*(?:grocery|supermarket|market).*",
                        r".*(?:walmart|target|costco|safeway|kroger).*",
                        r".*(?:whole foods|trader joe).*"
                    ],
                    "merchant_mappings": {
                        "WALMART": "groceries",
                        "TARGET": "groceries",
                        "COSTCO": "groceries",
                        "SAFEWAY": "groceries",
                        "KROGER": "groceries"
                    }
                },
                "gas_fuel": {
                    "name": "Gas & Fuel",
                    "keywords": ["gas", "fuel", "shell", "exxon", "bp", "chevron", "mobil"],
                    "regex_patterns": [
                        r".*(?:gas|fuel|station).*",
                        r".*(?:shell|exxon|bp|chevron|mobil).*",
                        r".*(?:petroleum|gasoline).*"
                    ],
                    "merchant_mappings": {
                        "SHELL": "gas_fuel",
                        "EXXON": "gas_fuel",
                        "BP": "gas_fuel",
                        "CHEVRON": "gas_fuel",
                        "MOBIL": "gas_fuel"
                    }
                },
                "entertainment": {
                    "name": "Entertainment",
                    "keywords": ["movie", "cinema", "theater", "netflix", "spotify", "gaming", "entertainment"],
                    "regex_patterns": [
                        r".*(?:movie|cinema|theater|theatre).*",
                        r".*(?:netflix|spotify|hulu|disney).*",
                        r".*(?:gaming|xbox|playstation|steam).*"
                    ],
                    "merchant_mappings": {
                        "NETFLIX": "entertainment",
                        "SPOTIFY": "entertainment",
                        "AMC THEATERS": "entertainment",
                        "STEAM": "entertainment"
                    }
                },
                "shopping": {
                    "name": "Shopping",
                    "keywords": ["amazon", "ebay", "shopping", "retail", "store", "mall"],
                    "regex_patterns": [
                        r".*(?:amazon|ebay|shopping).*",
                        r".*(?:retail|store|mall|outlet).*",
                        r".*(?:clothing|apparel|fashion).*"
                    ],
                    "merchant_mappings": {
                        "AMAZON": "shopping",
                        "EBAY": "shopping",
                        "MACY'S": "shopping",
                        "NORDSTROM": "shopping"
                    }
                },
                "transportation": {
                    "name": "Transportation",
                    "keywords": ["uber", "lyft", "taxi", "bus", "train", "metro", "parking"],
                    "regex_patterns": [
                        r".*(?:uber|lyft|taxi|cab).*",
                        r".*(?:bus|train|metro|transit).*",
                        r".*(?:parking|toll|transport).*"
                    ],
                    "merchant_mappings": {
                        "UBER": "transportation",
                        "LYFT": "transportation",
                        "METRO": "transportation"
                    }
                },
                "healthcare": {
                    "name": "Healthcare",
                    "keywords": ["hospital", "clinic", "pharmacy", "medical", "doctor", "dentist"],
                    "regex_patterns": [
                        r".*(?:hospital|clinic|medical).*",
                        r".*(?:pharmacy|cvs|walgreens).*",
                        r".*(?:doctor|dentist|physician).*"
                    ],
                    "merchant_mappings": {
                        "CVS PHARMACY": "healthcare",
                        "WALGREENS": "healthcare"
                    }
                },
                "utilities": {
                    "name": "Utilities",
                    "keywords": ["electric", "gas", "water", "internet", "phone", "utility"],
                    "regex_patterns": [
                        r".*(?:electric|electricity|power).*",
                        r".*(?:gas|water|sewer|utility).*",
                        r".*(?:internet|phone|telecom).*"
                    ],
                    "merchant_mappings": {
                        "PG&E": "utilities",
                        "COMCAST": "utilities",
                        "VERIZON": "utilities"
                    }
                },
                "financial": {
                    "name": "Financial Services",
                    "keywords": ["bank", "atm", "fee", "interest", "transfer", "payment"],
                    "regex_patterns": [
                        r".*(?:bank|atm|fee).*",
                        r".*(?:interest|dividend|investment).*",
                        r".*(?:transfer|payment|wire).*"
                    ],
                    "merchant_mappings": {
                        "BANK OF AMERICA": "financial",
                        "WELLS FARGO": "financial",
                        "CHASE": "financial"
                    }
                }
            },
            "default_category": "other",