```python
#!/usr/bin/env python3
"""
Bank Statement Transaction Categorizer

This module reads CSV bank statement files, categorizes transactions based on keywords,
and outputs the categorized data in JSON format. It supports flexible CSV formats and
provides detailed transaction categorization for personal finance tracking.

Features:
- Flexible CSV parsing with auto-detection of common bank statement formats
- Keyword-based transaction categorization across multiple categories
- JSON output with transaction summaries and category totals
- Comprehensive error handling for file operations and data parsing
- Support for both positive and negative transaction amounts

Usage:
    python script.py [csv_file_path]
    
If no file path is provided, it will look for 'bank_statement.csv' in the current directory.
"""

import csv
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from decimal import Decimal, InvalidOperation


class TransactionCategorizer:
    """Categorizes bank transactions based on keyword matching."""
    
    CATEGORIES = {
        'groceries': [
            'walmart', 'target', 'kroger', 'safeway', 'whole foods', 'costco',
            'grocery', 'market', 'food', 'supermarket', 'fresh', 'organic'
        ],
        'utilities': [
            'electric', 'gas', 'water', 'sewer', 'internet', 'cable', 'phone',
            'utility', 'power', 'energy', 'telecom', 'verizon', 'att', 'comcast'
        ],
        'entertainment': [
            'netflix', 'spotify', 'movie', 'theater', 'cinema', 'gaming',
            'entertainment', 'music', 'streaming', 'subscription', 'disney',
            'hulu', 'amazon prime', 'youtube'
        ],
        'dining': [
            'restaurant', 'cafe', 'coffee', 'starbucks', 'mcdonalds', 'pizza',
            'dining', 'bar', 'pub', 'bistro', 'grill', 'kitchen', 'diner'
        ],
        'transportation': [
            'gas station', 'fuel', 'uber', 'lyft', 'taxi', 'bus', 'train',
            'parking', 'toll', 'auto', 'car', 'vehicle', 'transport'
        ],
        'healthcare': [
            'pharmacy', 'doctor', 'medical', 'hospital', 'clinic', 'dental',
            'health', 'cvs', 'walgreens', 'insurance', 'copay'
        ],
        'shopping': [
            'amazon', 'ebay', 'store', 'retail', 'shop', 'mall', 'outlet',
            'clothing', 'apparel', 'department', 'best buy', 'home depot'
        ],
        'bills': [
            'payment', 'loan', 'mortgage', 'rent', 'credit card', 'insurance',
            'bill', 'monthly', 'autopay', 'recurring'
        ]
    }
    
    def __init__(self):
        self.transactions = []
        self.category_totals = {}
        self.uncategorized_total = Decimal('0')
    
    def categorize_transaction(self, description: str) -> str:
        """Categorize a transaction based on its description."""
        description_lower = description.lower()
        
        for category, keywords in self.CATEGORIES.items():
            if any(keyword in description_lower for keyword in keywords):
                return category
        
        return 'uncategorized'
    
    def parse_amount(self, amount_str: str) -> Decimal:
        """Parse amount string to Decimal, handling various formats."""
        try:
            # Remove common currency symbols and whitespace
            cleaned = amount_str.strip().replace('$', '').replace(',', '')
            
            # Handle parentheses for negative amounts (accounting format)
            if cleaned.startswith('(') and cleaned.endswith(')'):
                cleaned = '-' + cleaned[1:-1]
            
            return Decimal(cleaned)
        except (InvalidOperation, ValueError):
            return Decimal('0')
    
    def detect_csv_format(self, filepath: str) -> Optional[Dict[str, int]]:
        """Detect CSV format and return column mappings."""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                # Read first few lines to detect format
                sample_lines = [file.readline() for _ in range(3)]
                file.seek(0)
                
                # Try to detect delimiter
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(''.join(sample_lines)).delimiter
                
                # Read header
                reader = csv.DictReader(file, delimiter=delimiter)
                fieldnames = reader.fieldnames
                
                if not fieldnames:
                    return None
                
                # Map common column names to our standard format
                column_mapping = {}
                fieldnames_lower = [name.lower() for name in fieldnames]
                
                # Find date column
                for i, name in enumerate(fieldnames_lower):
                    if any(keyword in name for keyword in ['date', 'transaction', 'posted']):
                        column_mapping['date'] = i
                        break
                
                # Find description column
                for i, name in enumerate(fieldnames_lower):
                    if any(keyword in name for keyword in ['description', 'memo', 'detail', 'merchant']):
                        column_mapping['description'] = i
                        break
                
                # Find amount column
                for i, name in enumerate(fieldnames_lower):
                    if any(keyword in name for keyword in ['amount', 'transaction', 'debit', 'credit']):
                        column_mapping['amount'] = i
                        break
                
                return {
                    'mapping': column_mapping,
                    'fieldnames': fieldnames,
                    'delimiter': delimiter
                }
                
        except Exception as e:
            print(f"Error detecting CSV format: {e}", file=sys.stderr)
            return None
    
    def process_csv(self, filepath: str) -> bool:
        """Process CSV file and categorize transactions."""
        try:
            if not os.path.exists(filepath):
                print(f"Error: File '{filepath}' not found", file=sys.stderr)
                return False
            
            format_info = self.detect_csv_format(filepath)
            if not format_info:
                print("Error: Could not detect CSV format", file=sys.stderr)
                return False
            
            with open(filepath, 'r', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=format_info['delimiter'])
                rows = list(reader)
                
                if len(rows) < 2:
                    print("Error: CSV file appears to be empty or has no data rows", file=sys.stderr)
                    return False
                
                # Skip header row
                data_rows = rows[1:]
                mapping = format_info['mapping']
                
                for row_num, row in enumerate(data_rows, start=2):
                    try:
                        if len(row) <= max(mapping.values()):
                            continue
                        
                        # Extract data using column mapping
                        date_str = row[mapping.get('date', 0)] if 'date' in mapping else ''
                        description = row[mapping.get('description', 1)] if 'description' in mapping else ''
                        amount_str = row[mapping.get('amount', 2)] if 'amount' in mapping else '0'
                        
                        if not description.strip():
                            continue
                        
                        amount = self.parse_amount(amount_str)
                        category = self.categorize_transaction(description)
                        
                        transaction = {
                            'date': date_str,
                            'description': description.strip(),
                            'amount': float(amount),
                            'category': category
                        }
                        
                        self.transactions.append(transaction)
                        
                        # Update category totals
                        if category not in self.category_totals:
                            self.category_totals[category] = Decimal