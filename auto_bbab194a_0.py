```python
#!/usr/bin/env python3
"""
Bank Statement CSV Parser and Expense Categorizer

This module parses CSV bank statements to identify unique transaction patterns
and automatically generates categorization rules for common expense types.
It analyzes transaction descriptions to create keyword mappings for:
- Groceries & Food
- Gas & Transportation  
- Restaurants & Dining
- Utilities & Bills
- Shopping & Retail
- Healthcare & Medical
- Entertainment & Recreation
- Financial Services

The output is a JSON rules file that can be used for automated expense
categorization in personal finance applications.

Usage: python script.py
"""

import csv
import json
import re
from collections import defaultdict, Counter
from pathlib import Path


def clean_description(description):
    """Clean and normalize transaction descriptions."""
    if not description:
        return ""
    
    # Remove common prefixes and suffixes
    cleaned = re.sub(r'^(DEBIT|CREDIT|POS|ATM|CHECK|DEPOSIT)\s*', '', description.upper())
    cleaned = re.sub(r'\s*(PURCHASE|PAYMENT|TRANSFER|WITHDRAWAL)$', '', cleaned)
    
    # Remove dates, numbers, and special characters
    cleaned = re.sub(r'\d{2}/\d{2}', '', cleaned)
    cleaned = re.sub(r'\d{4,}', '', cleaned)
    cleaned = re.sub(r'[#*]+\d+', '', cleaned)
    cleaned = re.sub(r'[^\w\s]', ' ', cleaned)
    
    # Clean whitespace and return
    return ' '.join(cleaned.split())


def extract_merchant_name(description):
    """Extract likely merchant name from transaction description."""
    cleaned = clean_description(description)
    
    # Common patterns to identify merchant names
    merchant_patterns = [
        r'^([A-Z\s]{3,30})\s+\d',  # Merchant name followed by numbers
        r'^([A-Z\s]{3,30})\s+[A-Z]{2}$',  # Merchant name followed by state code
        r'^([A-Z\s]{3,30})$',  # Just the merchant name
    ]
    
    for pattern in merchant_patterns:
        match = re.match(pattern, cleaned)
        if match:
            return match.group(1).strip()
    
    # Fallback: return first few words
    words = cleaned.split()[:3]
    return ' '.join(words) if words else cleaned


def categorize_by_keywords():
    """Define expense categories with their associated keywords."""
    return {
        "Groceries & Food": {
            "keywords": [
                "WALMART", "TARGET", "KROGER", "SAFEWAY", "WHOLE FOODS", "TRADER JOES",
                "COSTCO", "SAMS CLUB", "PUBLIX", "WEGMANS", "HARRIS TEETER",
                "FOOD LION", "GIANT", "STOP SHOP", "ALBERTSONS", "MEIJER",
                "HEB", "WINCO", "ALDI", "LIDL", "MARKET", "GROCERY"
            ],
            "patterns": ["SUPERMARKET", "GROCERY", "FOOD MART"]
        },
        "Restaurants & Dining": {
            "keywords": [
                "MCDONALDS", "BURGER KING", "SUBWAY", "STARBUCKS", "DUNKIN",
                "KFC", "TACO BELL", "PIZZA HUT", "DOMINOS", "PAPA JOHNS",
                "CHIPOTLE", "PANERA", "WENDYS", "ARBYS", "SONIC",
                "CHILIS", "APPLEBEES", "OLIVE GARDEN", "OUTBACK", "RED LOBSTER",
                "RESTAURANT", "CAFE", "DINER", "GRILL", "BAR"
            ],
            "patterns": ["RESTAURANT", "CAFE", "BISTRO", "EATERY", "DINING"]
        },
        "Gas & Transportation": {
            "keywords": [
                "SHELL", "EXXON", "CHEVRON", "BP", "MOBIL", "TEXACO",
                "CITGO", "SUNOCO", "MARATHON", "SPEEDWAY", "WAWA",
                "SHEETZ", "CIRCLE K", "GAS STATION", "FUEL",
                "UBER", "LYFT", "TAXI", "BUS", "TRAIN", "METRO"
            ],
            "patterns": ["GAS", "FUEL", "GASOLINE", "STATION"]
        },
        "Utilities & Bills": {
            "keywords": [
                "ELECTRIC", "POWER", "WATER", "SEWER", "GAS COMPANY",
                "INTERNET", "CABLE", "PHONE", "CELLULAR", "WIRELESS",
                "COMCAST", "VERIZON", "ATT", "T-MOBILE", "SPRINT",
                "UTILITY", "MUNICIPAL", "CITY OF"
            ],
            "patterns": ["ELECTRIC", "UTILITY", "MUNICIPAL", "WATER DEPT"]
        },
        "Healthcare & Medical": {
            "keywords": [
                "PHARMACY", "CVS", "WALGREENS", "RITE AID", "MEDICAL",
                "HOSPITAL", "CLINIC", "DOCTOR", "DENTIST", "DENTAL",
                "OPTOMETRY", "VISION", "INSURANCE", "HEALTH"
            ],
            "patterns": ["MEDICAL", "PHARMACY", "DENTAL", "HEALTH"]
        },
        "Shopping & Retail": {
            "keywords": [
                "AMAZON", "EBAY", "MACYS", "KOHLS", "JC PENNEY",
                "NORDSTROM", "BEST BUY", "HOME DEPOT", "LOWES",
                "OFFICE DEPOT", "STAPLES", "TOYS R US", "GAMESTOP"
            ],
            "patterns": ["STORE", "SHOP", "RETAIL", "MALL"]
        },
        "Entertainment & Recreation": {
            "keywords": [
                "NETFLIX", "SPOTIFY", "HULU", "DISNEY", "HBO",
                "MOVIE", "THEATER", "CINEMA", "GYM", "FITNESS",
                "PARK", "RECREATION", "SPORTS", "GAME"
            ],
            "patterns": ["ENTERTAINMENT", "RECREATION", "THEATER", "GYM"]
        },
        "Financial Services": {
            "keywords": [
                "BANK", "ATM", "TRANSFER", "INTEREST", "FEE",
                "OVERDRAFT", "LOAN", "MORTGAGE", "CREDIT CARD",
                "PAYMENT", "CHECK", "DEPOSIT"
            ],
            "patterns": ["BANK", "FINANCIAL", "LOAN", "MORTGAGE"]
        }
    }


def categorize_transaction(description, category_rules):
    """Categorize a transaction based on description patterns."""
    cleaned_desc = clean_description(description).upper()
    
    for category, rules in category_rules.items():
        # Check keywords
        for keyword in rules.get("keywords", []):
            if keyword in cleaned_desc:
                return category
        
        # Check patterns
        for pattern in rules.get("patterns", []):
            if pattern in cleaned_desc:
                return category
    
    return "Other"


def parse_csv_statements(file_path):
    """Parse CSV bank statement file and extract transactions."""
    transactions = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # Try to detect delimiter
            sample = file.read(1024)
            file.seek(0)
            
            delimiter = ','
            if sample.count(';') > sample.count(','):
                delimiter = ';'
            elif sample.count('\t') > sample.count(','):
                delimiter = '\t'
            
            reader = csv.DictReader(file, delimiter=delimiter)
            
            for row in reader:
                # Try common column names for description and amount
                description = None
                amount = None
                date = None
                
                # Look for description column
                desc_columns = ['description', 'memo', 'payee', 'merchant', 'details']