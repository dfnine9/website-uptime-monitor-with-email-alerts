```python
#!/usr/bin/env python3
"""
Transaction Categorizer

A self-contained Python script that parses CSV files containing financial transactions
and categorizes them using keyword matching and pattern recognition. The script identifies
transaction types such as groceries, utilities, entertainment, transportation, etc.

Features:
- Reads CSV files with transaction data
- Uses keyword matching for category assignment
- Applies pattern recognition for amounts and descriptions
- Handles various CSV formats automatically
- Provides detailed categorization statistics
- Exports categorized results

Usage:
    python script.py

The script will look for CSV files in the current directory or create sample data
if no CSV files are found.
"""

import csv
import re
import os
import sys
from datetime import datetime
from collections import defaultdict, Counter
from typing import List, Dict, Tuple, Optional


class TransactionCategorizer:
    """Categorizes financial transactions using keyword matching and pattern recognition."""
    
    def __init__(self):
        self.categories = {
            'groceries': [
                'walmart', 'target', 'kroger', 'safeway', 'whole foods', 'trader joe',
                'costco', 'sam\'s club', 'grocery', 'supermarket', 'food mart',
                'aldi', 'publix', 'wegmans', 'harris teeter'
            ],
            'restaurants': [
                'mcdonald', 'burger king', 'taco bell', 'subway', 'starbucks',
                'pizza', 'restaurant', 'cafe', 'diner', 'grill', 'bistro',
                'kitchen', 'eatery', 'takeout', 'delivery'
            ],
            'gas_transportation': [
                'shell', 'exxon', 'bp', 'chevron', 'mobil', 'gas station',
                'uber', 'lyft', 'taxi', 'bus fare', 'metro', 'parking',
                'toll', 'airline', 'airport'
            ],
            'utilities': [
                'electric', 'electricity', 'gas bill', 'water', 'sewer',
                'internet', 'cable', 'phone', 'wireless', 'verizon',
                'at&t', 'comcast', 'utility'
            ],
            'entertainment': [
                'netflix', 'spotify', 'amazon prime', 'hulu', 'disney',
                'movie', 'theater', 'cinema', 'concert', 'game',
                'entertainment', 'streaming'
            ],
            'shopping': [
                'amazon', 'ebay', 'mall', 'department store', 'clothing',
                'shoes', 'electronics', 'best buy', 'home depot',
                'lowes', 'bed bath', 'tjmaxx'
            ],
            'healthcare': [
                'pharmacy', 'cvs', 'walgreens', 'doctor', 'hospital',
                'medical', 'dental', 'clinic', 'health', 'prescription'
            ],
            'banking_fees': [
                'atm fee', 'overdraft', 'monthly fee', 'service charge',
                'interest charge', 'late fee', 'bank fee'
            ]
        }
        
        self.amount_patterns = {
            'small_purchase': (0, 50),
            'medium_purchase': (50, 200),
            'large_purchase': (200, 1000),
            'major_purchase': (1000, float('inf'))
        }
    
    def detect_csv_format(self, filepath: str) -> Optional[Dict[str, int]]:
        """Detect CSV format and return column mapping."""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                # Try to detect delimiter
                sample = file.read(1024)
                file.seek(0)
                
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.reader(file, delimiter=delimiter)
                headers = next(reader)
                
                # Normalize headers
                headers_lower = [h.lower().strip() for h in headers]
                
                column_mapping = {}
                
                # Map common column names
                for i, header in enumerate(headers_lower):
                    if any(keyword in header for keyword in ['date', 'time']):
                        column_mapping['date'] = i
                    elif any(keyword in header for keyword in ['desc', 'description', 'memo', 'detail']):
                        column_mapping['description'] = i
                    elif any(keyword in header for keyword in ['amount', 'value', 'sum', 'total']):
                        column_mapping['amount'] = i
                    elif any(keyword in header for keyword in ['type', 'category', 'class']):
                        column_mapping['type'] = i
                
                return column_mapping
                
        except Exception as e:
            print(f"Error detecting CSV format: {e}")
            return None
    
    def clean_amount(self, amount_str: str) -> float:
        """Clean and convert amount string to float."""
        try:
            # Remove currency symbols, commas, and whitespace
            cleaned = re.sub(r'[$,\s]', '', str(amount_str))
            # Handle negative amounts in parentheses
            if cleaned.startswith('(') and cleaned.endswith(')'):
                cleaned = '-' + cleaned[1:-1]
            return abs(float(cleaned))
        except (ValueError, TypeError):
            return 0.0
    
    def categorize_by_keywords(self, description: str) -> str:
        """Categorize transaction based on description keywords."""
        description_lower = description.lower()
        
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'other'
    
    def categorize_by_amount(self, amount: float) -> str:
        """Categorize transaction based on amount patterns."""
        for pattern, (min_amt, max_amt) in self.amount_patterns.items():
            if min_amt <= amount < max_amt:
                return pattern
        return 'unknown_amount'
    
    def analyze_patterns(self, transactions: List[Dict]) -> Dict:
        """Analyze transaction patterns and generate insights."""
        patterns = {
            'category_totals': defaultdict(float),
            'category_counts': defaultdict(int),
            'amount_distribution': defaultdict(int),
            'monthly_spending': defaultdict(float),
            'frequent_merchants': Counter()
        }
        
        for transaction in transactions:
            category = transaction['category']
            amount = transaction['amount']
            description = transaction['description']
            
            patterns['category_totals'][category] += amount
            patterns['category_counts'][category] += 1
            patterns['amount_distribution'][self.categorize_by_amount(amount)] += 1
            
            # Extract potential merchant names (first few words)
            merchant = ' '.join(description.split()[:3]).strip()
            patterns['frequent_merchants'][merchant] += 1
            
            # Monthly analysis if date is available
            if 'date' in transaction and transaction['date']:
                try:
                    date_obj = datetime.strptime(transaction['date'], '%Y-%m-%d')
                    month_key = f"{date_obj.year}-{date_obj.month:02d}"
                    patterns['monthly_spending'][month_key] += amount
                except:
                    pass
        
        return patterns
    
    def process_csv(self, filepath: str) -> Tuple[List[Dict], Dict]:
        """Process CSV file and categorize transactions."""
        column_mapping = self.detect_csv_format(filepath)
        if not column_mapping:
            raise ValueError("Could not detect CSV format")
        
        transactions = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                headers = next(reader)  # Skip header row
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        transaction = {}
                        
                        # Extract data based on column mapping