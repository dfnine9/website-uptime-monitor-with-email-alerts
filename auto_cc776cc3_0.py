```python
#!/usr/bin/env python3
"""
Bank Statement Categorizer

A self-contained Python script that reads CSV bank statements and automatically
categorizes transactions using regex patterns and keyword matching. Categories
include food, transport, utilities, entertainment, and others.

Features:
- Reads CSV files with transaction data
- Uses regex and keyword matching for intelligent categorization
- Generates summary statistics by category
- Handles various CSV formats and missing data
- Provides detailed transaction breakdown

Usage: python script.py

The script will look for CSV files in the current directory or prompt for a file path.
Expected CSV columns: Date, Description, Amount (flexible column names supported)
"""

import csv
import re
import os
import sys
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class TransactionCategorizer:
    """Main class for categorizing bank transactions."""
    
    def __init__(self):
        """Initialize the categorizer with predefined categories and patterns."""
        self.categories = {
            'food': {
                'keywords': ['restaurant', 'cafe', 'coffee', 'pizza', 'burger', 'deli', 
                           'grocery', 'supermarket', 'food', 'dining', 'bakery', 'bar',
                           'mcdonald', 'subway', 'starbucks', 'dominos', 'kfc', 'taco'],
                'patterns': [
                    r'\b(restaurant|cafe|coffee|pizza|burger|deli|grocery|supermarket)\b',
                    r'\b(dining|bakery|bar|grill|bistro|eatery)\b',
                    r'\b(mcdonald|subway|starbucks|dominos|kfc|taco|wendys)\b'
                ]
            },
            'transport': {
                'keywords': ['gas', 'fuel', 'shell', 'exxon', 'bp', 'chevron', 'uber', 
                           'lyft', 'taxi', 'metro', 'bus', 'train', 'parking', 'toll'],
                'patterns': [
                    r'\b(gas|fuel|gasoline|petrol)\b',
                    r'\b(shell|exxon|bp|chevron|mobil|citgo)\b',
                    r'\b(uber|lyft|taxi|metro|bus|train|parking|toll)\b'
                ]
            },
            'utilities': {
                'keywords': ['electric', 'electricity', 'gas', 'water', 'sewer', 'internet',
                           'phone', 'mobile', 'cable', 'internet', 'power', 'energy'],
                'patterns': [
                    r'\b(electric|electricity|power|energy)\b',
                    r'\b(gas|water|sewer|utility)\b',
                    r'\b(internet|phone|mobile|cable|telecom)\b'
                ]
            },
            'entertainment': {
                'keywords': ['movie', 'cinema', 'theater', 'netflix', 'spotify', 'amazon',
                           'gaming', 'game', 'entertainment', 'music', 'streaming'],
                'patterns': [
                    r'\b(movie|cinema|theater|theatre)\b',
                    r'\b(netflix|spotify|amazon|hulu|disney)\b',
                    r'\b(gaming|game|entertainment|music|streaming)\b'
                ]
            },
            'shopping': {
                'keywords': ['amazon', 'walmart', 'target', 'costco', 'mall', 'store',
                           'shopping', 'retail', 'online', 'ebay'],
                'patterns': [
                    r'\b(amazon|walmart|target|costco|mall|store)\b',
                    r'\b(shopping|retail|online|ebay|etsy)\b'
                ]
            },
            'healthcare': {
                'keywords': ['doctor', 'medical', 'pharmacy', 'hospital', 'clinic',
                           'dental', 'health', 'insurance', 'cvs', 'walgreens'],
                'patterns': [
                    r'\b(doctor|medical|pharmacy|hospital|clinic)\b',
                    r'\b(dental|health|insurance|cvs|walgreens)\b'
                ]
            },
            'banking': {
                'keywords': ['fee', 'charge', 'interest', 'atm', 'bank', 'transfer',
                           'overdraft', 'maintenance'],
                'patterns': [
                    r'\b(fee|charge|interest|atm|bank)\b',
                    r'\b(transfer|overdraft|maintenance)\b'
                ]
            }
        }
    
    def categorize_transaction(self, description: str, amount: float) -> str:
        """
        Categorize a transaction based on its description.
        
        Args:
            description: Transaction description
            amount: Transaction amount
            
        Returns:
            Category name or 'other' if no match found
        """
        if not description:
            return 'other'
        
        description_lower = description.lower().strip()
        
        # Check each category
        for category, rules in self.categories.items():
            # Check keywords
            for keyword in rules['keywords']:
                if keyword.lower() in description_lower:
                    return category
            
            # Check regex patterns
            for pattern in rules['patterns']:
                if re.search(pattern, description_lower, re.IGNORECASE):
                    return category
        
        # Special handling for income (positive amounts with certain keywords)
        if amount > 0:
            income_keywords = ['salary', 'payroll', 'deposit', 'income', 'refund', 'credit']
            if any(keyword in description_lower for keyword in income_keywords):
                return 'income'
        
        return 'other'

class CSVProcessor:
    """Handles CSV file reading and processing."""
    
    @staticmethod
    def find_csv_files() -> List[str]:
        """Find CSV files in the current directory."""
        try:
            csv_files = [f for f in os.listdir('.') if f.lower().endswith('.csv')]
            return csv_files
        except Exception as e:
            print(f"Error scanning directory: {e}")
            return []
    
    @staticmethod
    def detect_columns(header: List[str]) -> Tuple[Optional[int], Optional[int], Optional[int]]:
        """
        Detect which columns contain date, description, and amount data.
        
        Args:
            header: List of column names
            
        Returns:
            Tuple of (date_col, description_col, amount_col) indices
        """
        date_col = description_col = amount_col = None
        
        for i, col in enumerate(header):
            col_lower = col.lower().strip()
            
            if date_col is None and any(word in col_lower for word in ['date', 'time']):
                date_col = i
            elif description_col is None and any(word in col_lower for word in 
                ['description', 'memo', 'detail', 'merchant', 'payee']):
                description_col = i
            elif amount_col is None and any(word in col_lower for word in 
                ['amount', 'value', 'total', 'debit', 'credit']):
                amount_col = i
        
        return date_col, description_col, amount_col
    
    @staticmethod
    def parse_amount(amount_str: str) -> float:
        """
        Parse amount string to float, handling various formats.
        
        Args:
            amount_str: String representation of amount
            
        Returns:
            Parsed amount as float
        """
        if not amount_str:
            return 0.0
        
        try:
            # Remove currency symbols and whitespace
            cleaned = re.sub(r'[$£€¥,\s]', '', str(amount_str).strip())
            
            # Handle parentheses as negative (accounting format)
            if cleaned.startswith('(') and cleaned.endswith(')'):
                cleaned = '-' + cleaned[1:-1]
            
            return float(cleaned)
        except (ValueError, TypeError):
            print(f"Warning: Could not parse amount '{amount_str}', using