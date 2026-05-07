```python
#!/usr/bin/env python3
"""
Bank Transaction Categorizer

A self-contained Python script that reads bank CSV files and categorizes transactions
based on configurable keyword rules. Supports multiple CSV formats and provides
detailed expense categorization for personal finance tracking.

Features:
- Automatic CSV format detection
- Configurable keyword-based categorization rules
- Robust error handling and data validation
- Summary statistics and reporting
- Support for multiple date formats

Usage: python script.py [csv_file_path]
If no file is provided, uses 'transactions.csv' in current directory.
"""

import csv
import re
import sys
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import os


class TransactionCategorizer:
    """Categorizes bank transactions based on configurable keyword rules."""
    
    def __init__(self):
        self.category_rules = {
            'food': [
                'restaurant', 'cafe', 'coffee', 'pizza', 'burger', 'food', 'grocery',
                'supermarket', 'bakery', 'deli', 'mcdonalds', 'subway', 'starbucks',
                'dominos', 'uber eats', 'doordash', 'grubhub', 'takeaway', 'dining'
            ],
            'transport': [
                'gas', 'fuel', 'uber', 'lyft', 'taxi', 'bus', 'train', 'metro',
                'parking', 'toll', 'car', 'vehicle', 'auto', 'transportation',
                'airline', 'flight', 'airport', 'rental car'
            ],
            'utilities': [
                'electric', 'electricity', 'gas bill', 'water', 'internet', 'phone',
                'mobile', 'cable', 'utility', 'energy', 'power', 'sewage',
                'trash', 'garbage', 'heating', 'cooling'
            ],
            'entertainment': [
                'movie', 'cinema', 'theater', 'concert', 'music', 'streaming',
                'netflix', 'spotify', 'gaming', 'game', 'entertainment',
                'club', 'bar', 'pub', 'recreation', 'hobby'
            ],
            'shopping': [
                'amazon', 'walmart', 'target', 'costco', 'store', 'retail',
                'purchase', 'buy', 'shopping', 'mall', 'outlet', 'clothes',
                'clothing', 'shoes', 'electronics'
            ],
            'healthcare': [
                'medical', 'doctor', 'hospital', 'pharmacy', 'health', 'dental',
                'vision', 'prescription', 'clinic', 'insurance', 'medicare'
            ],
            'housing': [
                'rent', 'mortgage', 'property', 'real estate', 'housing',
                'apartment', 'maintenance', 'repair', 'home improvement'
            ],
            'finance': [
                'bank', 'atm', 'fee', 'interest', 'loan', 'credit', 'investment',
                'transfer', 'payment', 'finance', 'tax', 'irs'
            ]
        }
    
    def detect_csv_format(self, file_path: str) -> Optional[Dict[str, int]]:
        """Detect CSV format by analyzing headers."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # Try to detect delimiter
                sample = file.read(1024)
                file.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.reader(file, delimiter=delimiter)
                headers = next(reader)
                
                # Normalize headers for matching
                headers_lower = [h.lower().strip() for h in headers]
                
                format_map = {}
                
                # Look for date column
                for i, header in enumerate(headers_lower):
                    if any(keyword in header for keyword in ['date', 'transaction date', 'posted date']):
                        format_map['date'] = i
                        break
                
                # Look for amount column
                for i, header in enumerate(headers_lower):
                    if any(keyword in header for keyword in ['amount', 'debit', 'credit', 'transaction amount']):
                        format_map['amount'] = i
                        break
                
                # Look for description column
                for i, header in enumerate(headers_lower):
                    if any(keyword in header for keyword in ['description', 'memo', 'details', 'transaction details']):
                        format_map['description'] = i
                        break
                
                if len(format_map) == 3:
                    return format_map
                else:
                    print(f"Warning: Could not detect all required columns. Found: {format_map}")
                    return None
                    
        except Exception as e:
            print(f"Error detecting CSV format: {e}")
            return None
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string with multiple format support."""
        date_formats = [
            '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%m-%d-%Y',
            '%Y/%m/%d', '%d-%m-%Y', '%m/%d/%y', '%d/%m/%y'
        ]
        
        date_str = date_str.strip()
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        print(f"Warning: Could not parse date: {date_str}")
        return None
    
    def parse_amount(self, amount_str: str) -> float:
        """Parse amount string, handling various formats."""
        try:
            # Remove currency symbols, commas, and whitespace
            cleaned = re.sub(r'[^\d.-]', '', amount_str.strip())
            
            # Handle negative amounts in parentheses
            if amount_str.strip().startswith('(') and amount_str.strip().endswith(')'):
                cleaned = '-' + cleaned
            
            return float(cleaned)
        except ValueError:
            print(f"Warning: Could not parse amount: {amount_str}")
            return 0.0
    
    def categorize_transaction(self, description: str) -> str:
        """Categorize transaction based on description keywords."""
        description_lower = description.lower()
        
        for category, keywords in self.category_rules.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'other'
    
    def read_transactions(self, file_path: str) -> List[Dict]:
        """Read and parse transactions from CSV file."""
        transactions = []
        
        format_map = self.detect_csv_format(file_path)
        if not format_map:
            print("Error: Could not detect CSV format")
            return transactions
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # Detect delimiter again for reading
                sample = file.read(1024)
                file.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.reader(file, delimiter=delimiter)
                next(reader)  # Skip header
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        if len(row) <= max(format_map.values()):
                            continue
                        
                        date_str = row[format_map['date']]
                        amount_str = row[format_map['amount']]
                        description = row[format_map['description']]
                        
                        parsed_date = self.parse_date(date_str)
                        if not parsed_date:
                            continue
                        
                        amount = self.parse_amount(amount_str)
                        category = self.categorize_transaction(description)
                        
                        transactions.append({
                            'date':