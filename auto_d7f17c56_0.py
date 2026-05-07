```python
"""
Financial Transaction Categorizer

This module parses CSV files containing bank or credit card transaction data,
automatically categorizes transactions using keyword matching and rule-based logic,
and outputs the processed data in a structured JSON format.

Features:
- Supports common CSV formats from major banks
- Automatic transaction categorization using predefined rules
- Configurable category keywords and rules
- Error handling for malformed data
- Self-contained with minimal dependencies

Usage: python script.py
"""

import csv
import json
import re
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


class TransactionCategorizer:
    def __init__(self):
        self.categories = {
            'Food & Dining': [
                'restaurant', 'cafe', 'coffee', 'pizza', 'burger', 'food',
                'dining', 'mcdonalds', 'starbucks', 'subway', 'kfc', 'taco',
                'grocery', 'supermarket', 'walmart', 'target', 'safeway'
            ],
            'Transportation': [
                'gas', 'fuel', 'shell', 'exxon', 'chevron', 'bp', 'uber',
                'lyft', 'taxi', 'bus', 'train', 'airline', 'parking', 'tolls'
            ],
            'Shopping': [
                'amazon', 'ebay', 'store', 'mall', 'retail', 'clothing',
                'electronics', 'best buy', 'costco', 'home depot', 'lowes'
            ],
            'Bills & Utilities': [
                'electric', 'gas bill', 'water', 'internet', 'phone', 'cable',
                'insurance', 'mortgage', 'rent', 'utility', 'verizon', 'att'
            ],
            'Healthcare': [
                'pharmacy', 'doctor', 'medical', 'hospital', 'clinic',
                'dental', 'cvs', 'walgreens', 'health', 'medicare'
            ],
            'Entertainment': [
                'netflix', 'spotify', 'movie', 'theater', 'gym', 'fitness',
                'subscription', 'gaming', 'book', 'music', 'streaming'
            ],
            'Banking': [
                'atm', 'fee', 'interest', 'transfer', 'deposit', 'withdrawal',
                'bank', 'credit', 'payment', 'overdraft'
            ],
            'Income': [
                'salary', 'payroll', 'deposit', 'refund', 'dividend',
                'interest income', 'bonus', 'commission'
            ]
        }
    
    def detect_csv_format(self, file_path: str) -> Optional[Dict[str, str]]:
        """Detect CSV format and return column mapping"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                sample = file.read(1024)
                file.seek(0)
                
                # Try to detect delimiter
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(file, delimiter=delimiter)
                headers = [h.lower().strip() for h in reader.fieldnames or []]
                
                # Common column mappings
                column_mapping = {}
                
                # Date columns
                date_patterns = ['date', 'transaction date', 'trans date', 'posted date']
                for pattern in date_patterns:
                    if pattern in headers:
                        column_mapping['date'] = pattern
                        break
                
                # Description columns
                desc_patterns = ['description', 'merchant', 'payee', 'transaction', 'memo']
                for pattern in desc_patterns:
                    if pattern in headers:
                        column_mapping['description'] = pattern
                        break
                
                # Amount columns
                amount_patterns = ['amount', 'debit', 'credit', 'transaction amount']
                for pattern in amount_patterns:
                    if pattern in headers:
                        column_mapping['amount'] = pattern
                        break
                
                # Check for separate debit/credit columns
                if 'debit' in headers and 'credit' in headers:
                    column_mapping['debit'] = 'debit'
                    column_mapping['credit'] = 'credit'
                
                return column_mapping if column_mapping else None
                
        except Exception as e:
            print(f"Error detecting CSV format: {e}")
            return None
    
    def parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float"""
        if not amount_str or str(amount_str).strip() == '':
            return 0.0
        
        # Remove currency symbols and whitespace
        amount_str = re.sub(r'[$,\s]', '', str(amount_str))
        
        # Handle parentheses as negative
        if amount_str.startswith('(') and amount_str.endswith(')'):
            amount_str = '-' + amount_str[1:-1]
        
        try:
            return float(amount_str)
        except ValueError:
            return 0.0
    
    def parse_date(self, date_str: str) -> Optional[str]:
        """Parse date string to ISO format"""
        if not date_str:
            return None
        
        date_formats = [
            '%m/%d/%Y', '%m/%d/%y', '%Y-%m-%d', '%d/%m/%Y',
            '%m-%d-%Y', '%Y/%m/%d', '%d-%m-%Y', '%b %d, %Y'
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(str(date_str).strip(), fmt)
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        return None
    
    def categorize_transaction(self, description: str, amount: float) -> str:
        """Categorize transaction based on description and amount"""
        description_lower = description.lower()
        
        # Special rules for income (positive amounts with specific keywords)
        if amount > 0:
            income_keywords = ['payroll', 'salary', 'deposit', 'refund', 'dividend']
            if any(keyword in description_lower for keyword in income_keywords):
                return 'Income'
        
        # Check each category
        for category, keywords in self.categories.items():
            if any(keyword in description_lower for keyword in keywords):
                return category
        
        # Default categorization based on amount
        if amount > 0:
            return 'Income'
        elif abs(amount) > 1000:
            return 'Large Expense'
        else:
            return 'Other'
    
    def process_csv_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Process CSV file and return categorized transactions"""
        column_mapping = self.detect_csv_format(file_path)
        if not column_mapping:
            raise ValueError("Could not detect CSV format")
        
        transactions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # Detect delimiter again for actual processing
                sample = file.read(1024)
                file.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(file, delimiter=delimiter)
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        # Extract data based on column mapping
                        date_str = row.get(column_mapping.get('date', ''), '')
                        description = row.get(column_mapping.get('description', ''), '')
                        
                        # Handle amount (either single column or debit/credit)
                        amount = 0.0
                        if 'debit' in column_mapping and 'credit' in column_mapping:
                            debit = self.parse_amount(row.get(column_mapping['debit'], ''))