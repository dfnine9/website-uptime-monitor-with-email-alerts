```python
#!/usr/bin/env python3
"""
Bank Transaction Categorizer

This module reads CSV files from common bank formats and automatically categorizes
transactions using keyword matching on merchant names and descriptions.

Supports common bank CSV formats and provides flexible categorization rules
based on merchant names, transaction descriptions, and amounts.

Usage: python script.py

The script will look for CSV files in the current directory and process them
for transaction categorization.
"""

import csv
import os
import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Transaction:
    """Represents a bank transaction."""
    date: str
    description: str
    amount: float
    original_category: str = ""
    predicted_category: str = ""


class TransactionCategorizer:
    """Categorizes bank transactions using keyword matching."""
    
    def __init__(self):
        self.category_rules = {
            'Groceries': [
                'walmart', 'target', 'kroger', 'safeway', 'whole foods', 'trader joe',
                'grocery', 'market', 'food', 'supermarket', 'costco', 'sams club'
            ],
            'Gas': [
                'shell', 'chevron', 'exxon', 'bp', 'mobil', 'gas station', 'fuel',
                'petro', 'marathon', 'valero', 'citgo'
            ],
            'Restaurants': [
                'restaurant', 'cafe', 'diner', 'pizza', 'burger', 'taco bell',
                'mcdonalds', 'subway', 'starbucks', 'dunkin', 'kfc', 'wendys',
                'chipotle', 'panera'
            ],
            'Shopping': [
                'amazon', 'ebay', 'shop', 'store', 'mall', 'retail', 'clothing',
                'nordstrom', 'macys', 'best buy', 'home depot', 'lowes'
            ],
            'Utilities': [
                'electric', 'gas bill', 'water', 'internet', 'cable', 'phone',
                'utility', 'power', 'energy', 'telecom', 'verizon', 'att'
            ],
            'Transportation': [
                'uber', 'lyft', 'taxi', 'bus', 'train', 'airline', 'airport',
                'parking', 'toll', 'metro', 'transit'
            ],
            'Healthcare': [
                'pharmacy', 'doctor', 'medical', 'hospital', 'clinic', 'cvs',
                'walgreens', 'dentist', 'health'
            ],
            'Entertainment': [
                'movie', 'theater', 'netflix', 'spotify', 'gaming', 'concert',
                'ticket', 'entertainment', 'gym', 'fitness'
            ],
            'Banking': [
                'fee', 'interest', 'transfer', 'atm', 'overdraft', 'maintenance',
                'service charge'
            ],
            'Income': [
                'salary', 'payroll', 'deposit', 'refund', 'dividend', 'bonus'
            ]
        }
    
    def categorize_transaction(self, description: str, amount: float) -> str:
        """Categorize a transaction based on description and amount."""
        description_lower = description.lower()
        
        # Handle income (positive amounts in some formats)
        if amount > 0 and any(keyword in description_lower for keyword in self.category_rules['Income']):
            return 'Income'
        
        # Check each category for keyword matches
        for category, keywords in self.category_rules.items():
            if category == 'Income':  # Already handled above
                continue
                
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'Other'


class BankCSVReader:
    """Reads and parses CSV files from common bank formats."""
    
    def __init__(self):
        self.common_date_columns = ['date', 'transaction date', 'posted date', 'trans date']
        self.common_description_columns = ['description', 'merchant', 'payee', 'memo', 'details']
        self.common_amount_columns = ['amount', 'transaction amount', 'debit', 'credit']
    
    def detect_csv_format(self, filepath: str) -> Optional[Dict[str, str]]:
        """Detect the CSV format and return column mappings."""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                # Try to detect delimiter
                sample = file.read(1024)
                file.seek(0)
                
                delimiter = ','
                if sample.count(';') > sample.count(','):
                    delimiter = ';'
                elif sample.count('\t') > sample.count(','):
                    delimiter = '\t'
                
                reader = csv.DictReader(file, delimiter=delimiter)
                headers = [h.lower().strip() if h else '' for h in reader.fieldnames or []]
                
                # Find column mappings
                mapping = {}
                
                # Find date column
                for col in headers:
                    if any(date_col in col for date_col in self.common_date_columns):
                        mapping['date'] = col
                        break
                
                # Find description column
                for col in headers:
                    if any(desc_col in col for desc_col in self.common_description_columns):
                        mapping['description'] = col
                        break
                
                # Find amount column(s)
                amount_cols = []
                for col in headers:
                    if any(amt_col in col for amt_col in self.common_amount_columns):
                        amount_cols.append(col)
                
                if amount_cols:
                    mapping['amount'] = amount_cols[0]  # Use first found amount column
                
                # Check if we found the essential columns
                if 'date' in mapping and 'description' in mapping and 'amount' in mapping:
                    mapping['delimiter'] = delimiter
                    return mapping
                
                return None
                
        except Exception as e:
            print(f"Error detecting CSV format for {filepath}: {e}")
            return None
    
    def parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float, handling various formats."""
        if not amount_str:
            return 0.0
        
        # Remove currency symbols and extra whitespace
        amount_str = re.sub(r'[$€£¥,\s]', '', str(amount_str))
        
        # Handle parentheses as negative (accounting format)
        if amount_str.startswith('(') and amount_str.endswith(')'):
            amount_str = '-' + amount_str[1:-1]
        
        try:
            return float(amount_str)
        except ValueError:
            return 0.0
    
    def read_csv_file(self, filepath: str) -> List[Transaction]:
        """Read and parse a CSV file into Transaction objects."""
        format_mapping = self.detect_csv_format(filepath)
        if not format_mapping:
            print(f"Could not detect format for {filepath}")
            return []
        
        transactions = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file, delimiter=format_mapping['delimiter'])
                
                for row in reader:
                    try:
                        date = row.get(format_mapping['date'], '').strip()
                        description = row.get(format_mapping['description'], '').strip()
                        amount_str = row.get(format_mapping['amount'], '').strip()
                        amount = self.parse_amount(amount_str)
                        
                        if date and description:  # Only add if we have essential data
                            transaction = Transaction(
                                date=date,
                                description=description,
                                amount=amount
                            )
                            transactions.append(transaction)
                    
                    except Exception as e:
                        print(f"Error parsing row in