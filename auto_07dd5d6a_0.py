```python
#!/usr/bin/env python3
"""
Bank Statement Transaction Categorizer

This module parses CSV bank statements and categorizes transactions based on
merchant name patterns. It extracts transaction data (date, description, amount)
and creates intelligent category mappings using keyword pattern matching.

The script automatically detects common CSV formats and builds a comprehensive
category mapping dictionary for financial transaction analysis.

Usage: python script.py
"""

import csv
import re
import sys
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Any


def detect_csv_format(file_path: str) -> Tuple[List[str], str]:
    """
    Detect CSV format and return headers with delimiter.
    
    Args:
        file_path: Path to CSV file
        
    Returns:
        Tuple of (headers, delimiter)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # Try different delimiters
            sample = file.read(1024)
            file.seek(0)
            
            delimiter = ','
            if sample.count(';') > sample.count(','):
                delimiter = ';'
            elif sample.count('\t') > sample.count(','):
                delimiter = '\t'
            
            reader = csv.reader(file, delimiter=delimiter)
            headers = next(reader)
            return headers, delimiter
            
    except Exception as e:
        print(f"Error detecting CSV format: {e}")
        return [], ','


def parse_amount(amount_str: str) -> float:
    """
    Parse amount string to float, handling various formats.
    
    Args:
        amount_str: String representation of amount
        
    Returns:
        Float amount
    """
    try:
        # Remove currency symbols and spaces
        cleaned = re.sub(r'[^\d.,\-+]', '', str(amount_str))
        
        # Handle negative amounts in parentheses
        if cleaned.startswith('(') and cleaned.endswith(')'):
            cleaned = '-' + cleaned[1:-1]
        
        # Handle comma as thousand separator vs decimal
        if ',' in cleaned and '.' in cleaned:
            # Assume comma is thousand separator
            cleaned = cleaned.replace(',', '')
        elif cleaned.count(',') == 1 and len(cleaned.split(',')[1]) == 2:
            # Comma as decimal separator
            cleaned = cleaned.replace(',', '.')
        elif cleaned.count(',') > 1:
            # Multiple commas, assume thousand separators
            cleaned = cleaned.replace(',', '')
            
        return float(cleaned)
        
    except (ValueError, TypeError):
        return 0.0


def parse_date(date_str: str) -> str:
    """
    Parse date string to standardized format.
    
    Args:
        date_str: String representation of date
        
    Returns:
        Standardized date string (YYYY-MM-DD)
    """
    try:
        # Common date formats
        formats = [
            '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%m-%d-%Y',
            '%d-%m-%Y', '%Y/%m/%d', '%d.%m.%Y', '%m.%d.%Y'
        ]
        
        for fmt in formats:
            try:
                parsed = datetime.strptime(str(date_str).strip(), fmt)
                return parsed.strftime('%Y-%m-%d')
            except ValueError:
                continue
                
        return str(date_str)  # Return original if no format matches
        
    except Exception:
        return str(date_str)


def extract_merchant_keywords(description: str) -> List[str]:
    """
    Extract meaningful keywords from transaction description.
    
    Args:
        description: Transaction description
        
    Returns:
        List of extracted keywords
    """
    # Clean description
    cleaned = re.sub(r'[^\w\s]', ' ', str(description).upper())
    words = cleaned.split()
    
    # Filter out common non-merchant words
    stop_words = {
        'POS', 'PURCHASE', 'DEBIT', 'CARD', 'TRANSACTION', 'PAYMENT',
        'TRANSFER', 'WITHDRAWAL', 'DEPOSIT', 'FEE', 'CHARGE', 'ATM',
        'ONLINE', 'MOBILE', 'TELEPHONE', 'RECURRING', 'AUTOMATIC',
        'CHECK', 'ACH', 'WIRE', 'ELECTRONIC', 'PENDING', 'AUTHORIZED',
        'THE', 'AND', 'OR', 'OF', 'IN', 'AT', 'ON', 'FOR', 'TO', 'FROM'
    }
    
    # Extract meaningful keywords (length > 2, not in stop words)
    keywords = [word for word in words if len(word) > 2 and word not in stop_words]
    
    return keywords[:5]  # Limit to top 5 keywords


def build_category_mapping(transactions: List[Dict]) -> Dict[str, str]:
    """
    Build category mapping based on merchant patterns.
    
    Args:
        transactions: List of transaction dictionaries
        
    Returns:
        Category mapping dictionary
    """
    # Predefined merchant patterns
    category_patterns = {
        'GROCERY': [
            'WALMART', 'TARGET', 'COSTCO', 'SAFEWAY', 'KROGER', 'PUBLIX',
            'TRADER', 'WHOLE', 'MARKET', 'GROCERY', 'SUPERMARKET', 'FOOD'
        ],
        'RESTAURANT': [
            'MCDONALD', 'STARBUCKS', 'SUBWAY', 'PIZZA', 'RESTAURANT',
            'CAFE', 'DINER', 'GRILL', 'BISTRO', 'EATERY', 'BURGER'
        ],
        'GAS': [
            'SHELL', 'EXXON', 'CHEVRON', 'BP', 'MOBIL', 'TEXACO',
            'GAS', 'FUEL', 'STATION', 'PETRO'
        ],
        'SHOPPING': [
            'AMAZON', 'EBAY', 'STORE', 'SHOP', 'RETAIL', 'MALL',
            'OUTLET', 'BOUTIQUE', 'MERCHANDISE'
        ],
        'UTILITIES': [
            'ELECTRIC', 'WATER', 'GAS', 'UTILITY', 'POWER', 'ENERGY',
            'CABLE', 'INTERNET', 'PHONE', 'TELEPHONE'
        ],
        'BANKING': [
            'BANK', 'ATM', 'TRANSFER', 'DEPOSIT', 'WITHDRAWAL',
            'FEE', 'INTEREST', 'OVERDRAFT', 'MAINTENANCE'
        ],
        'ENTERTAINMENT': [
            'NETFLIX', 'SPOTIFY', 'MOVIE', 'THEATER', 'CINEMA',
            'ENTERTAINMENT', 'STREAMING', 'MUSIC', 'GAME'
        ],
        'HEALTHCARE': [
            'PHARMACY', 'MEDICAL', 'DOCTOR', 'HOSPITAL', 'CLINIC',
            'DENTAL', 'HEALTH', 'MEDICINE', 'CVS', 'WALGREENS'
        ],
        'TRANSPORTATION': [
            'UBER', 'LYFT', 'TAXI', 'BUS', 'TRAIN', 'AIRLINE',
            'PARKING', 'TOLL', 'TRANSIT', 'TRANSPORTATION'
        ]
    }
    
    mapping = {}
    merchant_frequency = defaultdict(int)
    
    # Count merchant frequency
    for transaction in transactions:
        description = transaction.get('description', '')
        keywords = extract_merchant_keywords(description)
        
        for keyword in keywords:
            merchant_frequency[keyword] += 1
    
    # Build mapping based on patterns
    for transaction in transactions:
        description = transaction.get('description', '')
        keywords = extract_merchant_keywords(description)
        
        best_category = 'OTHER'
        best_score = 0
        
        for category, patterns in category_patterns.items