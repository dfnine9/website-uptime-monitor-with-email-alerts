```python
#!/usr/bin/env python3
"""
Bank Transaction Parser and Categorizer

This module parses CSV files from multiple bank formats, validates transaction data,
and categorizes expenses using predefined keyword dictionaries. It supports various
CSV formats commonly used by banks and financial institutions.

Features:
- Multi-format CSV parsing with auto-detection
- Transaction data validation (amount, date, description)
- Automated expense categorization using keyword matching
- Comprehensive error handling and reporting
- Self-contained with minimal dependencies

Usage:
    python script.py
"""

import csv
import re
import os
import sys
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from decimal import Decimal, InvalidOperation


class BankTransactionParser:
    """Parses and categorizes bank transactions from various CSV formats."""
    
    # Predefined category keywords
    CATEGORY_KEYWORDS = {
        'groceries': [
            'grocery', 'supermarket', 'walmart', 'target', 'safeway', 'kroger',
            'whole foods', 'trader joe', 'costco', 'food', 'market', 'deli'
        ],
        'utilities': [
            'electric', 'gas', 'water', 'internet', 'phone', 'cable', 'utility',
            'power', 'energy', 'telecom', 'verizon', 'att', 'comcast'
        ],
        'entertainment': [
            'netflix', 'spotify', 'hulu', 'disney', 'movie', 'theater', 'cinema',
            'concert', 'music', 'gaming', 'entertainment', 'streaming'
        ],
        'transportation': [
            'gas station', 'fuel', 'uber', 'lyft', 'taxi', 'metro', 'bus',
            'train', 'parking', 'toll', 'car', 'automotive'
        ],
        'dining': [
            'restaurant', 'cafe', 'pizza', 'mcdonald', 'starbucks', 'burger',
            'dining', 'takeout', 'delivery', 'doordash', 'grubhub'
        ],
        'shopping': [
            'amazon', 'ebay', 'store', 'retail', 'clothing', 'fashion',
            'electronics', 'home depot', 'lowes', 'best buy'
        ],
        'healthcare': [
            'pharmacy', 'doctor', 'medical', 'hospital', 'clinic', 'dental',
            'health', 'cvs', 'walgreens', 'prescription'
        ],
        'finance': [
            'bank', 'fee', 'interest', 'loan', 'credit', 'investment',
            'insurance', 'transfer', 'atm'
        ]
    }
    
    # Common CSV field mappings for different bank formats
    FIELD_MAPPINGS = [
        # Chase format
        {'date': 'Transaction Date', 'description': 'Description', 'amount': 'Amount'},
        # Bank of America format
        {'date': 'Date', 'description': 'Description', 'amount': 'Amount'},
        # Wells Fargo format
        {'date': 'Date', 'description': 'Description', 'amount': 'Amount', 'debit': 'Debit', 'credit': 'Credit'},
        # Citi format
        {'date': 'Date', 'description': 'Description', 'amount': 'Credit/Debit'},
        # Generic format
        {'date': 'date', 'description': 'description', 'amount': 'amount'}
    ]
    
    def __init__(self):
        self.transactions = []
        self.errors = []
        self.stats = {
            'total_transactions': 0,
            'valid_transactions': 0,
            'categorized_transactions': 0,
            'categories': {}
        }
    
    def detect_csv_format(self, headers: List[str]) -> Optional[Dict[str, str]]:
        """Detect CSV format based on headers."""
        headers_lower = [h.lower().strip() for h in headers]
        
        for mapping in self.FIELD_MAPPINGS:
            mapping_lower = {k: v.lower() for k, v in mapping.items()}
            
            # Check if all required fields are present
            required_fields = ['date', 'description']
            if all(mapping_lower[field] in headers_lower for field in required_fields):
                # Create reverse mapping from header to field type
                reverse_mapping = {}
                for field, header in mapping.items():
                    header_lower = header.lower()
                    if header_lower in headers_lower:
                        actual_header = headers[headers_lower.index(header_lower)]
                        reverse_mapping[field] = actual_header
                return reverse_mapping
        
        return None
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string in various formats."""
        date_formats = [
            '%m/%d/%Y', '%m/%d/%y', '%Y-%m-%d', '%d/%m/%Y',
            '%Y/%m/%d', '%m-%d-%Y', '%d-%m-%Y'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        return None
    
    def parse_amount(self, amount_str: str) -> Optional[Decimal]:
        """Parse amount string, handling various formats."""
        if not amount_str or amount_str.strip() == '':
            return None
        
        try:
            # Clean the amount string
            cleaned = re.sub(r'[^\d.-]', '', amount_str.strip())
            if not cleaned:
                return None
            
            return Decimal(cleaned)
        except (InvalidOperation, ValueError):
            return None
    
    def categorize_transaction(self, description: str) -> str:
        """Categorize transaction based on description keywords."""
        description_lower = description.lower()
        
        # Score each category
        category_scores = {}
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in description_lower)
            if score > 0:
                category_scores[category] = score
        
        if category_scores:
            # Return category with highest score
            return max(category_scores.items(), key=lambda x: x[1])[0]
        
        return 'other'
    
    def validate_transaction(self, transaction: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate transaction data."""
        errors = []
        
        if not transaction.get('date'):
            errors.append("Missing date")
        
        if not transaction.get('description'):
            errors.append("Missing description")
        elif len(transaction['description'].strip()) < 2:
            errors.append("Description too short")
        
        if transaction.get('amount') is None:
            errors.append("Invalid amount")
        
        return len(errors) == 0, "; ".join(errors)
    
    def parse_csv_file(self, filepath: str) -> bool:
        """Parse a CSV file and extract transactions."""
        try:
            with open(filepath, 'r', encoding='utf-8-sig', newline='') as file:
                # Detect delimiter
                sample = file.read(1024)
                file.seek(0)
                
                delimiter = ','
                if sample.count(';') > sample.count(','):
                    delimiter = ';'
                elif sample.count('\t') > sample.count(','):
                    delimiter = '\t'
                
                reader = csv.DictReader(file, delimiter=delimiter)
                headers = reader.fieldnames
                
                if not headers:
                    self.errors.append(f"No headers found in {filepath}")
                    return False
                
                # Detect format
                field_mapping = self.detect_csv_format(headers)
                if not field_mapping:
                    self.errors.append(f"Unknown CSV format in {filepath}")
                    return False
                
                print(f"Processing {filepath} with format: