```python
#!/usr/bin/env python3
"""
Transaction Analysis Module

This module reads CSV files containing financial transactions, categorizes them
using keyword matching, and calculates spending patterns by category.

Features:
- Reads CSV files with transaction data
- Categorizes transactions based on description keywords
- Calculates total spending, average amounts, and transaction counts per category
- Handles various CSV formats and missing data
- Provides detailed spending pattern analysis

Expected CSV format:
- Headers should include: date, description, amount (or similar variations)
- Amount should be numeric (positive for income, negative for expenses)
- Description field used for categorization

Usage:
    python script.py [csv_file_path]

If no file path provided, uses 'transactions.csv' in current directory.
"""

import csv
import sys
import os
import re
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Tuple, Any


class TransactionAnalyzer:
    """Analyzes financial transactions and categorizes spending patterns."""
    
    def __init__(self):
        """Initialize the transaction analyzer with category keywords."""
        self.categories = {
            'groceries': ['grocery', 'supermarket', 'food', 'walmart', 'target', 'costco', 'safeway', 'kroger'],
            'restaurants': ['restaurant', 'cafe', 'coffee', 'pizza', 'mcdonald', 'starbucks', 'dining'],
            'gas': ['gas', 'fuel', 'shell', 'exxon', 'chevron', 'bp', 'mobil'],
            'entertainment': ['movie', 'theater', 'netflix', 'spotify', 'game', 'entertainment', 'cinema'],
            'utilities': ['electric', 'water', 'internet', 'phone', 'utility', 'cable', 'wireless'],
            'shopping': ['amazon', 'ebay', 'store', 'mall', 'shopping', 'retail', 'purchase'],
            'transportation': ['uber', 'lyft', 'taxi', 'bus', 'train', 'metro', 'parking'],
            'healthcare': ['hospital', 'doctor', 'pharmacy', 'medical', 'health', 'clinic', 'cvs', 'walgreens'],
            'insurance': ['insurance', 'premium', 'policy', 'coverage'],
            'banking': ['fee', 'charge', 'interest', 'overdraft', 'atm', 'bank'],
            'income': ['salary', 'payroll', 'deposit', 'refund', 'dividend', 'bonus', 'payment received']
        }
        
        self.transactions = []
        self.categorized_data = defaultdict(list)
        
    def detect_csv_format(self, file_path: str) -> Dict[str, int]:
        """Detect CSV format and return column indices."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                # Read first few lines to detect format
                sample = file.read(1024)
                file.seek(0)
                
                # Try different delimiters
                for delimiter in [',', ';', '\t']:
                    try:
                        reader = csv.reader(file, delimiter=delimiter)
                        headers = [h.lower().strip() for h in next(reader)]
                        file.seek(0)
                        
                        if len(headers) >= 3:  # Minimum columns needed
                            return self._map_columns(headers), delimiter
                    except:
                        file.seek(0)
                        continue
                        
        except Exception as e:
            raise Exception(f"Error detecting CSV format: {e}")
            
        raise Exception("Could not detect valid CSV format")
    
    def _map_columns(self, headers: List[str]) -> Dict[str, int]:
        """Map CSV headers to standard column names."""
        column_map = {}
        
        # Look for date column
        date_keywords = ['date', 'transaction_date', 'trans_date', 'time']
        for i, header in enumerate(headers):
            if any(keyword in header for keyword in date_keywords):
                column_map['date'] = i
                break
        
        # Look for description column
        desc_keywords = ['description', 'memo', 'details', 'reference', 'merchant']
        for i, header in enumerate(headers):
            if any(keyword in header for keyword in desc_keywords):
                column_map['description'] = i
                break
                
        # Look for amount column
        amount_keywords = ['amount', 'value', 'total', 'sum', 'debit', 'credit']
        for i, header in enumerate(headers):
            if any(keyword in header for keyword in amount_keywords):
                column_map['amount'] = i
                break
        
        # Set defaults if not found
        if 'date' not in column_map:
            column_map['date'] = 0
        if 'description' not in column_map:
            column_map['description'] = 1
        if 'amount' not in column_map:
            column_map['amount'] = 2
            
        return column_map
    
    def read_csv(self, file_path: str) -> None:
        """Read and parse CSV file."""
        try:
            column_map, delimiter = self.detect_csv_format(file_path)
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                reader = csv.reader(file, delimiter=delimiter)
                headers = next(reader)  # Skip header row
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        if len(row) <= max(column_map.values()):
                            continue
                            
                        # Extract data
                        date_str = row[column_map['date']].strip()
                        description = row[column_map['description']].strip()
                        amount_str = row[column_map['amount']].strip()
                        
                        # Skip empty rows
                        if not date_str or not description or not amount_str:
                            continue
                        
                        # Parse amount
                        amount = self._parse_amount(amount_str)
                        if amount is None:
                            continue
                        
                        # Parse date (basic parsing)
                        date = self._parse_date(date_str)
                        
                        transaction = {
                            'date': date,
                            'description': description,
                            'amount': amount,
                            'raw_amount': amount_str
                        }
                        
                        self.transactions.append(transaction)
                        
                    except Exception as e:
                        print(f"Warning: Skipping row {row_num} due to error: {e}")
                        continue
                        
        except FileNotFoundError:
            raise Exception(f"File not found: {file_path}")
        except Exception as e:
            raise Exception(f"Error reading CSV file: {e}")
    
    def _parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float."""
        try:
            # Remove common currency symbols and spaces
            cleaned = re.sub(r'[$£€¥,\s]', '', amount_str)
            
            # Handle parentheses (negative amounts)
            if cleaned.startswith('(') and cleaned.endswith(')'):
                cleaned = '-' + cleaned[1:-1]
            
            return float(cleaned)
        except:
            return None
    
    def _parse_date(self, date_str: str) -> str:
        """Basic date parsing - returns original string if can't parse."""
        try:
            # Try common date formats
            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%m-%d-%Y']:
                try:
                    parsed = datetime.strptime(date_str, fmt)
                    return parsed.strftime('%Y-%m-%d')
                except:
                    continue
            return date_str
        except:
            return date_str
    
    def categorize_transactions(self) -> None:
        """Categorize transactions based on description keywords."""
        for transaction in self.transactions:
            description = transaction['description