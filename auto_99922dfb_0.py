```python
"""
Bank Statement Transaction Categorizer

This module reads CSV bank statements and categorizes transactions based on
keyword matching rules. It processes transaction data into structured categories
like groceries, utilities, entertainment, etc.

Features:
- Reads CSV files with transaction data
- Implements configurable keyword-based categorization
- Handles various CSV formats with flexible column mapping
- Provides transaction summaries by category
- Includes error handling for file operations and data parsing

Usage:
    python script.py
"""

import csv
import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import os


class TransactionCategorizer:
    def __init__(self):
        # Define categorization rules with keywords
        self.category_rules = {
            'groceries': [
                'walmart', 'target', 'kroger', 'safeway', 'whole foods', 'trader joe',
                'costco', 'sam\'s club', 'grocery', 'market', 'food lion', 'publix',
                'aldi', 'stop & shop', 'giant', 'harris teeter', 'meijer'
            ],
            'utilities': [
                'electric', 'gas', 'water', 'sewer', 'internet', 'cable', 'phone',
                'utility', 'power', 'energy', 'verizon', 'at&t', 'comcast', 'xfinity',
                'spectrum', 'cox', 'duke energy', 'pge', 'con edison'
            ],
            'entertainment': [
                'netflix', 'spotify', 'hulu', 'disney', 'amazon prime', 'apple music',
                'movie', 'theater', 'cinema', 'concert', 'game', 'steam', 'xbox',
                'playstation', 'youtube', 'twitch', 'entertainment'
            ],
            'transportation': [
                'gas station', 'shell', 'exxon', 'bp', 'chevron', 'mobil', 'uber',
                'lyft', 'taxi', 'metro', 'bus', 'train', 'parking', 'toll',
                'car wash', 'auto', 'vehicle', 'dmv'
            ],
            'dining': [
                'restaurant', 'mcdonald', 'burger king', 'subway', 'starbucks',
                'pizza', 'cafe', 'bar', 'grill', 'diner', 'bistro', 'kitchen',
                'food delivery', 'doordash', 'grubhub', 'ubereats'
            ],
            'shopping': [
                'amazon', 'ebay', 'store', 'shop', 'retail', 'mall', 'outlet',
                'department', 'clothing', 'shoes', 'electronics', 'best buy',
                'home depot', 'lowes', 'tj maxx', 'marshalls'
            ],
            'healthcare': [
                'hospital', 'doctor', 'medical', 'pharmacy', 'cvs', 'walgreens',
                'clinic', 'dental', 'vision', 'health', 'medicare', 'insurance'
            ],
            'banking': [
                'bank', 'atm', 'fee', 'interest', 'dividend', 'transfer',
                'deposit', 'withdrawal', 'check', 'overdraft', 'maintenance'
            ]
        }
    
    def normalize_description(self, description: str) -> str:
        """Normalize transaction description for better matching."""
        if not description:
            return ""
        
        # Convert to lowercase and remove extra whitespace
        normalized = re.sub(r'\s+', ' ', description.lower().strip())
        
        # Remove common transaction codes and special characters
        normalized = re.sub(r'[#*]+\d+', '', normalized)  # Remove transaction IDs
        normalized = re.sub(r'[^\w\s&\'-]', ' ', normalized)  # Keep only alphanumeric, &, ', -
        
        return normalized
    
    def categorize_transaction(self, description: str) -> str:
        """Categorize a transaction based on its description."""
        normalized_desc = self.normalize_description(description)
        
        if not normalized_desc:
            return 'uncategorized'
        
        # Check each category's keywords
        for category, keywords in self.category_rules.items():
            for keyword in keywords:
                if keyword.lower() in normalized_desc:
                    return category
        
        return 'uncategorized'
    
    def detect_csv_format(self, file_path: str) -> Optional[Dict[str, int]]:
        """Detect CSV format and return column mapping."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # Read first few lines to detect format
                sample = file.read(1024)
                file.seek(0)
                
                # Try different delimiters
                delimiter = ','
                if ';' in sample and sample.count(';') > sample.count(','):
                    delimiter = ';'
                elif '\t' in sample:
                    delimiter = '\t'
                
                reader = csv.reader(file, delimiter=delimiter)
                headers = next(reader, None)
                
                if not headers:
                    return None
                
                # Normalize headers for matching
                headers_lower = [h.lower().strip() for h in headers]
                
                # Common column mappings
                column_mapping = {}
                
                # Look for date columns
                date_patterns = ['date', 'transaction date', 'posted date', 'trans date']
                for i, header in enumerate(headers_lower):
                    if any(pattern in header for pattern in date_patterns):
                        column_mapping['date'] = i
                        break
                
                # Look for description columns
                desc_patterns = ['description', 'memo', 'detail', 'transaction', 'payee']
                for i, header in enumerate(headers_lower):
                    if any(pattern in header for pattern in desc_patterns):
                        column_mapping['description'] = i
                        break
                
                # Look for amount columns
                amount_patterns = ['amount', 'debit', 'credit', 'transaction amount']
                for i, header in enumerate(headers_lower):
                    if any(pattern in header for pattern in amount_patterns):
                        column_mapping['amount'] = i
                        break
                
                # Ensure we have minimum required columns
                if 'description' in column_mapping and 'amount' in column_mapping:
                    return column_mapping
                
                return None
                
        except Exception as e:
            print(f"Error detecting CSV format: {e}")
            return None
    
    def parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float."""
        if not amount_str:
            return 0.0
        
        try:
            # Remove currency symbols, commas, and extra whitespace
            cleaned = re.sub(r'[^\d.-]', '', str(amount_str).strip())
            if not cleaned:
                return 0.0
            
            return float(cleaned)
        except (ValueError, TypeError):
            return 0.0
    
    def process_csv(self, file_path: str) -> List[Dict]:
        """Process CSV file and categorize transactions."""
        transactions = []
        
        try:
            column_mapping = self.detect_csv_format(file_path)
            if not column_mapping:
                raise ValueError("Could not detect CSV format or missing required columns")
            
            with open(file_path, 'r', encoding='utf-8') as file:
                # Detect delimiter again
                sample = file.read(1024)
                file.seek(0)
                delimiter = ',' if sample.count(',') >= sample.count(';') else ';'
                if '\t' in sample:
                    delimiter = '\t'
                
                reader = csv.reader(file, delimiter=delimiter)
                headers = next(reader, None)  # Skip header row
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        if len(row) < max(column_mapping.values()) + 1: