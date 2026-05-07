```python
#!/usr/bin/env python3
"""
Bank Statement Transaction Categorizer

This script parses CSV bank statement files and categorizes transactions based on
keywords in their descriptions. It extracts transaction data (date, description, amount)
and applies predefined spending categories such as groceries, utilities, entertainment, etc.

The script is self-contained using only standard library modules and provides
comprehensive error handling for file operations and data parsing.

Usage: python script.py
"""

import csv
import re
from datetime import datetime
from collections import defaultdict
import os
import sys


class TransactionCategorizer:
    """Categorizes bank transactions based on description keywords."""
    
    def __init__(self):
        self.categories = {
            'groceries': [
                'walmart', 'kroger', 'safeway', 'whole foods', 'trader joe',
                'grocery', 'supermarket', 'food store', 'market', 'costco',
                'target', 'aldi', 'publix', 'harris teeter'
            ],
            'utilities': [
                'electric', 'gas company', 'water', 'internet', 'phone',
                'verizon', 'at&t', 'comcast', 'xfinity', 'utility',
                'power', 'energy', 'cable', 'wifi', 'broadband'
            ],
            'entertainment': [
                'netflix', 'spotify', 'amazon prime', 'hulu', 'disney',
                'movie', 'theater', 'cinema', 'concert', 'tickets',
                'steam', 'playstation', 'xbox', 'entertainment'
            ],
            'restaurants': [
                'restaurant', 'cafe', 'coffee', 'starbucks', 'mcdonald',
                'burger', 'pizza', 'taco', 'subway', 'chipotle',
                'dining', 'food delivery', 'uber eats', 'doordash'
            ],
            'transportation': [
                'gas station', 'fuel', 'uber', 'lyft', 'taxi',
                'metro', 'bus', 'train', 'parking', 'toll',
                'shell', 'exxon', 'bp', 'chevron'
            ],
            'shopping': [
                'amazon', 'ebay', 'store', 'shop', 'retail',
                'mall', 'clothing', 'shoes', 'department store',
                'best buy', 'home depot', 'lowes'
            ],
            'healthcare': [
                'pharmacy', 'cvs', 'walgreens', 'doctor', 'medical',
                'hospital', 'clinic', 'dental', 'prescription',
                'health', 'medicare', 'insurance'
            ],
            'finance': [
                'bank fee', 'interest', 'loan', 'mortgage', 'credit card',
                'investment', 'atm fee', 'service charge', 'overdraft'
            ]
        }
    
    def categorize_transaction(self, description):
        """Categorize a transaction based on its description."""
        description_lower = description.lower()
        
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'other'


def parse_date(date_str):
    """Parse date string in various formats."""
    date_formats = [
        '%m/%d/%Y',
        '%Y-%m-%d',
        '%m-%d-%Y',
        '%d/%m/%Y',
        '%Y/%m/%d',
        '%m/%d/%y',
        '%m-%d-%y'
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    
    raise ValueError(f"Unable to parse date: {date_str}")


def parse_amount(amount_str):
    """Parse amount string and return float value."""
    # Remove currency symbols, commas, and whitespace
    cleaned = re.sub(r'[^\d.-]', '', amount_str.strip())
    
    # Handle parentheses (negative amounts)
    if amount_str.strip().startswith('(') and amount_str.strip().endswith(')'):
        cleaned = '-' + cleaned
    
    try:
        return float(cleaned)
    except ValueError:
        raise ValueError(f"Unable to parse amount: {amount_str}")


def detect_csv_structure(file_path):
    """Detect the structure of the CSV file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # Read first few lines to detect structure
            sample = file.read(1024)
            file.seek(0)
            
            # Try to detect delimiter
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
            reader = csv.reader(file, delimiter=delimiter)
            header = next(reader)
            
            # Common header patterns
            date_cols = ['date', 'transaction date', 'posting date', 'trans date']
            desc_cols = ['description', 'memo', 'transaction', 'payee', 'details']
            amount_cols = ['amount', 'debit', 'credit', 'transaction amount']
            
            date_idx = desc_idx = amount_idx = None
            
            for i, col in enumerate(header):
                col_lower = col.lower().strip()
                if not date_idx and any(dc in col_lower for dc in date_cols):
                    date_idx = i
                elif not desc_idx and any(dc in col_lower for dc in desc_cols):
                    desc_idx = i
                elif not amount_idx and any(ac in col_lower for ac in amount_cols):
                    amount_idx = i
            
            return delimiter, date_idx, desc_idx, amount_idx, header
    
    except Exception as e:
        raise Exception(f"Error detecting CSV structure: {e}")


def parse_csv_file(file_path):
    """Parse CSV file and extract transactions."""
    transactions = []
    
    try:
        delimiter, date_idx, desc_idx, amount_idx, header = detect_csv_structure(file_path)
        
        if date_idx is None or desc_idx is None or amount_idx is None:
            raise ValueError("Could not identify required columns (date, description, amount)")
        
        print(f"Detected columns - Date: {date_idx}, Description: {desc_idx}, Amount: {amount_idx}")
        print(f"Header: {header}")
        
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=delimiter)
            next(reader)  # Skip header
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    if len(row) <= max(date_idx, desc_idx, amount_idx):
                        continue
                    
                    date = parse_date(row[date_idx])
                    description = row[desc_idx].strip()
                    amount = parse_amount(row[amount_idx])
                    
                    transactions.append({
                        'date': date,
                        'description': description,
                        'amount': amount
                    })
                
                except (ValueError, IndexError) as e:
                    print(f"Warning: Skipping row {row_num} due to error: {e}")
                    continue
    
    except Exception as e:
        raise Exception(f"Error parsing CSV file: {e}")
    
    return transactions


def main():
    """Main function to process bank statement and categorize transactions."""
    # Look for CSV files in current directory
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
    
    if not csv_files:
        print("No CSV files found in current directory.")
        print("Please place your bank statement CSV file in the same directory as this script.")
        return
    
    # Use first CSV file found or prompt for specific file
    if len(csv_files) == 1:
        csv_file = csv_files[0]
        print(f"