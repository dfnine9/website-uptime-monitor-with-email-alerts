```python
#!/usr/bin/env python3
"""
Transaction Classification Configuration Generator

This module creates a comprehensive configuration file for financial transaction
classification. It defines spending categories, keyword mappings, and regex patterns
to automatically categorize bank transactions, credit card purchases, and other
financial data.

The configuration includes:
- Hierarchical spending categories (primary and subcategories)
- Keyword-to-category mappings for merchant identification
- Regex patterns for transaction description parsing
- Priority rules for handling ambiguous classifications
- Custom rules for specific financial institutions

Usage:
    python script.py

The script generates a JSON configuration file that can be used by transaction
processing systems to automatically classify and categorize financial data.
"""

import json
import re
import sys
from typing import Dict, List, Any


def create_spending_categories() -> Dict[str, Any]:
    """Create hierarchical spending categories structure."""
    try:
        categories = {
            "housing": {
                "name": "Housing & Utilities",
                "subcategories": {
                    "rent_mortgage": "Rent/Mortgage",
                    "utilities": "Utilities",
                    "home_maintenance": "Home Maintenance",
                    "property_tax": "Property Tax",
                    "home_insurance": "Home Insurance",
                    "hoa_fees": "HOA Fees"
                }
            },
            "transportation": {
                "name": "Transportation",
                "subcategories": {
                    "gas_fuel": "Gas & Fuel",
                    "car_payment": "Car Payment",
                    "car_insurance": "Car Insurance",
                    "car_maintenance": "Car Maintenance",
                    "public_transport": "Public Transportation",
                    "rideshare": "Rideshare/Taxi",
                    "parking": "Parking"
                }
            },
            "food": {
                "name": "Food & Dining",
                "subcategories": {
                    "groceries": "Groceries",
                    "restaurants": "Restaurants",
                    "fast_food": "Fast Food",
                    "coffee": "Coffee/Beverages",
                    "alcohol": "Alcohol",
                    "delivery": "Food Delivery"
                }
            },
            "healthcare": {
                "name": "Healthcare",
                "subcategories": {
                    "medical": "Medical Services",
                    "dental": "Dental",
                    "vision": "Vision/Optical",
                    "pharmacy": "Pharmacy",
                    "health_insurance": "Health Insurance",
                    "fitness": "Fitness/Gym"
                }
            },
            "entertainment": {
                "name": "Entertainment & Recreation",
                "subcategories": {
                    "streaming": "Streaming Services",
                    "movies": "Movies/Theater",
                    "games": "Gaming",
                    "hobbies": "Hobbies",
                    "sports": "Sports/Recreation",
                    "travel": "Travel/Vacation"
                }
            },
            "shopping": {
                "name": "Shopping",
                "subcategories": {
                    "clothing": "Clothing",
                    "electronics": "Electronics",
                    "home_goods": "Home Goods",
                    "personal_care": "Personal Care",
                    "gifts": "Gifts",
                    "online_shopping": "Online Shopping"
                }
            },
            "financial": {
                "name": "Financial Services",
                "subcategories": {
                    "banking_fees": "Banking Fees",
                    "investment": "Investment",
                    "loans": "Loans/Credit",
                    "insurance": "Insurance",
                    "taxes": "Taxes",
                    "financial_advisor": "Financial Advisory"
                }
            },
            "education": {
                "name": "Education",
                "subcategories": {
                    "tuition": "Tuition",
                    "books": "Books/Supplies",
                    "courses": "Online Courses",
                    "professional_dev": "Professional Development"
                }
            },
            "business": {
                "name": "Business Expenses",
                "subcategories": {
                    "office_supplies": "Office Supplies",
                    "software": "Software/Subscriptions",
                    "marketing": "Marketing/Advertising",
                    "business_travel": "Business Travel",
                    "professional_services": "Professional Services"
                }
            },
            "income": {
                "name": "Income",
                "subcategories": {
                    "salary": "Salary/Wages",
                    "freelance": "Freelance Income",
                    "investment_income": "Investment Income",
                    "refunds": "Refunds",
                    "other_income": "Other Income"
                }
            },
            "uncategorized": {
                "name": "Uncategorized",
                "subcategories": {
                    "unknown": "Unknown",
                    "other": "Other"
                }
            }
        }
        return categories
    except Exception as e:
        print(f"Error creating spending categories: {e}", file=sys.stderr)
        return {}


def create_keyword_mappings() -> Dict[str, str]:
    """Create keyword-to-category mappings for transaction classification."""
    try:
        mappings = {
            # Housing & Utilities
            "rent": "housing.rent_mortgage",
            "mortgage": "housing.rent_mortgage",
            "electric": "housing.utilities",
            "gas company": "housing.utilities",
            "water": "housing.utilities",
            "internet": "housing.utilities",
            "cable": "housing.utilities",
            "phone": "housing.utilities",
            "home depot": "housing.home_maintenance",
            "lowes": "housing.home_maintenance",
            "property tax": "housing.property_tax",
            "hoa": "housing.hoa_fees",
            
            # Transportation
            "shell": "transportation.gas_fuel",
            "exxon": "transportation.gas_fuel",
            "chevron": "transportation.gas_fuel",
            "bp": "transportation.gas_fuel",
            "mobil": "transportation.gas_fuel",
            "car payment": "transportation.car_payment",
            "auto loan": "transportation.car_payment",
            "geico": "transportation.car_insurance",
            "state farm": "transportation.car_insurance",
            "progressive": "transportation.car_insurance",
            "jiffy lube": "transportation.car_maintenance",
            "uber": "transportation.rideshare",
            "lyft": "transportation.rideshare",
            "parking": "transportation.parking",
            
            # Food & Dining
            "walmart": "food.groceries",
            "kroger": "food.groceries",
            "safeway": "food.groceries",
            "whole foods": "food.groceries",
            "trader joes": "food.groceries",
            "costco": "food.groceries",
            "mcdonalds": "food.fast_food",
            "burger king": "food.fast_food",
            "taco bell": "food.fast_food",
            "subway": "food.fast_food",
            "starbucks": "food.coffee",
            "dunkin": "food.coffee",
            "doordash": "food.delivery",
            "uber eats": "food.delivery",
            "grubhub": "food.delivery",
            
            # Healthcare
            "cvs": "healthcare.pharmacy",
            "walgreens": "healthcare.pharmacy",
            "rite aid": "healthcare.pharmacy",
            "planet fitness": "healthcare.fitness",
            "24 hour fitness": "healthcare.fitness",
            "la fitness": "healthcare.fitness",
            
            # Entertainment
            "netflix": "entertainment.streaming",
            "hulu": "entertainment.streaming",
            "spotify": "entertainment.streaming",
            "amazon prime": "entertainment.streaming",
            "disney": "entertainment.streaming",
            "amc": "entertainment.movies",
            "regal": "entertainment.movies",
            "steam": "entertainment.games",
            "playstation": "entertainment.games",
            "xbox": "entertainment.games",
            
            # Shopping
            "amazon": "shopping.online_shopping",
            "target": "shopping.home_goods",
            "best buy