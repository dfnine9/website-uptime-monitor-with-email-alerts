```python
"""
Expense Categorization Configuration Generator

This module creates a comprehensive configuration file for expense categorization
that maps keywords and patterns to common expense categories. The configuration
includes rules for groceries, gas, dining, utilities, and other common expense
types, with support for merchant names, transaction descriptions, and amount-based
rules.

The generated configuration can be used by expense tracking applications to
automatically categorize transactions based on merchant names, transaction
descriptions, and spending patterns.
"""

import json
import re
import sys
from typing import Dict, List, Any, Optional


class ExpenseCategorizer:
    """Manages expense categorization rules and keyword mappings."""
    
    def __init__(self):
        self.config = self._create_base_config()
    
    def _create_base_config(self) -> Dict[str, Any]:
        """Create the base configuration structure with categorization rules."""
        return {
            "version": "1.0",
            "description": "Expense categorization rules and keyword mappings",
            "categories": {
                "groceries": {
                    "keywords": [
                        "walmart", "target", "kroger", "safeway", "publix", "wegmans",
                        "whole foods", "trader joe", "aldi", "costco", "sam's club",
                        "grocery", "supermarket", "market", "food lion", "harris teeter",
                        "giant", "shoprite", "stop shop", "king soopers", "fred meyer",
                        "heb", "winco", "meijer", "hy-vee", "ingles", "bi-lo"
                    ],
                    "patterns": [
                        r"grocery.*store",
                        r".*market.*",
                        r".*food.*mart",
                        r".*supermarket.*"
                    ],
                    "merchant_codes": ["5411", "5499"],
                    "description": "Food and household essentials",
                    "subcategories": {
                        "organic": ["whole foods", "trader joe", "organic"],
                        "bulk": ["costco", "sam's club", "bulk"],
                        "convenience": ["7-eleven", "wawa", "convenience"]
                    }
                },
                "gas": {
                    "keywords": [
                        "shell", "exxon", "mobil", "chevron", "bp", "citgo", "sunoco",
                        "marathon", "phillips 66", "valero", "conoco", "speedway",
                        "circle k", "7-eleven", "wawa", "gas", "fuel", "station",
                        "pump", "petro", "gulf", "arco", "texaco"
                    ],
                    "patterns": [
                        r".*gas.*station",
                        r".*fuel.*",
                        r".*petro.*",
                        r"pump\s*\d+"
                    ],
                    "merchant_codes": ["5541", "5542"],
                    "description": "Gasoline and automotive fuel",
                    "subcategories": {
                        "premium": ["premium", "plus", "supreme"],
                        "diesel": ["diesel"],
                        "convenience_store": ["convenience", "c-store"]
                    }
                },
                "dining": {
                    "keywords": [
                        "mcdonald", "burger king", "wendy", "taco bell", "kfc",
                        "pizza hut", "domino", "subway", "starbucks", "dunkin",
                        "chipotle", "panda express", "chick-fil-a", "restaurant",
                        "cafe", "diner", "bistro", "grill", "tavern", "bar",
                        "pizzeria", "steakhouse", "sushi", "thai", "chinese",
                        "italian", "mexican", "indian", "japanese", "korean"
                    ],
                    "patterns": [
                        r".*restaurant.*",
                        r".*cafe.*",
                        r".*bar.*grill",
                        r".*pizza.*",
                        r".*coffee.*"
                    ],
                    "merchant_codes": ["5812", "5814"],
                    "description": "Restaurants and food delivery",
                    "subcategories": {
                        "fast_food": ["mcdonald", "burger king", "wendy", "taco bell", "kfc"],
                        "coffee": ["starbucks", "dunkin", "coffee", "espresso"],
                        "delivery": ["uber eats", "doordash", "grubhub", "postmates"],
                        "fine_dining": ["steakhouse", "fine dining", "upscale"]
                    }
                },
                "utilities": {
                    "keywords": [
                        "electric", "electricity", "power", "gas company", "water",
                        "sewer", "internet", "cable", "phone", "cellular", "verizon",
                        "at&t", "comcast", "spectrum", "cox", "utility", "pge",
                        "southern company", "duke energy", "con edison", "xcel"
                    ],
                    "patterns": [
                        r".*electric.*company",
                        r".*power.*company",
                        r".*utility.*",
                        r".*telecom.*"
                    ],
                    "merchant_codes": ["4814", "4816", "4899"],
                    "description": "Utilities and essential services",
                    "subcategories": {
                        "electricity": ["electric", "power", "pge", "duke energy"],
                        "gas": ["gas company", "natural gas"],
                        "water": ["water", "sewer", "municipal"],
                        "internet": ["internet", "broadband", "comcast", "spectrum"],
                        "phone": ["phone", "cellular", "verizon", "at&t"]
                    }
                },
                "transportation": {
                    "keywords": [
                        "uber", "lyft", "taxi", "cab", "metro", "subway", "bus",
                        "train", "parking", "toll", "bridge", "tunnel", "transit",
                        "airline", "flight", "airport", "rental car", "car rental"
                    ],
                    "patterns": [
                        r".*transport.*",
                        r".*transit.*",
                        r".*parking.*",
                        r".*toll.*"
                    ],
                    "merchant_codes": ["4121", "4131", "4111"],
                    "description": "Transportation and travel",
                    "subcategories": {
                        "rideshare": ["uber", "lyft"],
                        "public_transit": ["metro", "subway", "bus", "train"],
                        "parking": ["parking", "meter", "garage"],
                        "air_travel": ["airline", "flight", "airport"]
                    }
                },
                "shopping": {
                    "keywords": [
                        "amazon", "ebay", "walmart", "target", "best buy", "home depot",
                        "lowes", "macy", "nordstrom", "kohls", "tj maxx", "marshall",
                        "ross", "outlet", "mall", "department store", "retail"
                    ],
                    "patterns": [
                        r".*retail.*",
                        r".*store.*",
                        r".*shop.*"
                    ],
                    "merchant_codes": ["5999", "5311", "5331"],
                    "description": "General retail and shopping",
                    "subcategories": {
                        "online": ["amazon", "ebay", "online"],
                        "clothing": ["macy", "nordstrom", "kohls", "clothing"],
                        "electronics": ["best buy", "electronics"],
                        "home_improvement": ["home depot", "lowes", "hardware"]
                    }
                },
                "healthcare": {
                    "keywords": [
                        "hospital", "clinic", "doctor", "physician", "dentist",
                        "pharmacy", "cvs", "walgreens", "rite aid", "medical",
                        "health", "dental", "vision", "prescription", "copay"
                    ],
                    "patterns": [
                        r".*medical.*",
                        r".*health.*",
                        r".*pharmacy.*",
                        r"dr\.