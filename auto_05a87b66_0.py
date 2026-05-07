```python
"""
Transaction CSV Parser and Expense Categorizer

This module reads CSV transaction files and automatically categorizes expenses
based on keyword matching. It processes transaction data including date, description,
and amount, then assigns categories like groceries, utilities, entertainment, etc.

Usage:
    python script.py

Features:
- Reads CSV files with transaction data
- Keyword-based expense categorization
- Error handling for file operations and data parsing
- Summary statistics and categorized output
- Self-contained with only standard library dependencies
"""

import csv
import sys
import os
from datetime import datetime
from collections import defaultdict
import re


class TransactionCategorizer:
    """Categorizes transactions based on keywords in descriptions."""
    
    def __init__(self):
        # Define category keywords (case-insensitive matching)
        self.categories = {
            'groceries': [
                'walmart', 'target', 'kroger', 'safeway', 'whole foods', 'trader joe',
                'grocery', 'supermarket', 'food', 'market', 'fresh', 'organic'
            ],
            'utilities': [
                'electric', 'gas', 'water', 'power', 'utility', 'energy',
                'internet', 'phone', 'mobile', 'cable', 'telecom'
            ],
            'entertainment': [
                'netflix', 'spotify', 'movie', 'theater', 'cinema', 'concert',
                'game', 'entertainment', 'music', 'streaming', 'youtube'
            ],
            'transportation': [
                'gas station', 'fuel', 'uber', 'lyft', 'taxi', 'metro', 'bus',
                'parking', 'toll', 'car', 'auto', 'vehicle'
            ],
            'restaurants': [
                'restaurant', 'cafe', 'coffee', 'starbucks', 'mcdonald', 'pizza',
                'burger', 'diner', 'bistro', 'bar', 'pub', 'food truck'
            ],
            'shopping': [
                'amazon', 'ebay', 'store', 'shop', 'retail', 'mall',
                'clothing', 'fashion', 'shoes', 'electronics'
            ],
            'healthcare': [
                'hospital', 'doctor', 'medical', 'pharmacy', 'health',
                'dental', 'clinic', 'medicine', 'prescription'
            ],
            'finance': [
                'bank', 'atm', 'fee', 'interest', 'loan', 'credit',
                'insurance', 'investment', 'transfer'
            ]
        }
    
    def categorize(self, description):
        """Categorize a transaction based on its description."""
        description_lower = description.lower()
        
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'other'


class CSVTransactionParser:
    """Parses CSV transaction files and categorizes expenses."""
    
    def __init__(self):
        self.categorizer = TransactionCategorizer()
        self.transactions = []
        self.category_totals = defaultdict(float)
        self.total_amount = 0.0
    
    def parse_amount(self, amount_str):
        """Parse amount string to float, handling various formats."""
        try:
            # Remove currency symbols and whitespace
            clean_amount = re.sub(r'[$,\s]', '', str(amount_str))
            
            # Handle negative amounts in parentheses
            if clean_amount.startswith('(') and clean_amount.endswith(')'):
                clean_amount = '-' + clean_amount[1:-1]
            
            return float(clean_amount)
        except (ValueError, TypeError):
            return 0.0
    
    def parse_date(self, date_str):
        """Parse date string to datetime object."""
        date_formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']
        
        for fmt in date_formats:
            try:
                return datetime.strptime(str(date_str).strip(), fmt)
            except ValueError:
                continue
        
        return None
    
    def detect_csv_structure(self, file_path):
        """Detect CSV structure and column mapping."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # Read first few lines to detect structure
                sample = file.read(1024)
                file.seek(0)
                
                # Detect delimiter
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.reader(file, delimiter=delimiter)
                headers = next(reader, [])
                
                # Map common column names
                column_map = {}
                for i, header in enumerate(headers):
                    header_lower = header.lower().strip()
                    
                    if any(word in header_lower for word in ['date', 'time']):
                        column_map['date'] = i
                    elif any(word in header_lower for word in ['desc', 'description', 'memo', 'detail']):
                        column_map['description'] = i
                    elif any(word in header_lower for word in ['amount', 'value', 'sum', 'total']):
                        column_map['amount'] = i
                
                return delimiter, column_map, headers
                
        except Exception as e:
            print(f"Error detecting CSV structure: {e}")
            return ',', {}, []
    
    def read_csv(self, file_path):
        """Read and parse CSV transaction file."""
        try:
            delimiter, column_map, headers = self.detect_csv_structure(file_path)
            
            # Check if we have required columns
            if not all(key in column_map for key in ['date', 'description', 'amount']):
                print("Warning: Could not detect all required columns (date, description, amount)")
                print(f"Available headers: {headers}")
                
                # Use default column positions if detection fails
                if not column_map:
                    column_map = {'date': 0, 'description': 1, 'amount': 2}
            
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=delimiter)
                next(reader, None)  # Skip header row
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        if len(row) < max(column_map.values()) + 1:
                            continue
                        
                        date_str = row[column_map.get('date', 0)]
                        description = row[column_map.get('description', 1)]
                        amount_str = row[column_map.get('amount', 2)]
                        
                        # Parse data
                        transaction_date = self.parse_date(date_str)
                        amount = self.parse_amount(amount_str)
                        category = self.categorizer.categorize(description)
                        
                        transaction = {
                            'date': transaction_date,
                            'description': description.strip(),
                            'amount': amount,
                            'category': category
                        }
                        
                        self.transactions.append(transaction)
                        self.category_totals[category] += amount
                        self.total_amount += amount
                        
                    except (IndexError, ValueError) as e:
                        print(f"Warning: Error parsing row {row_num}: {e}")
                        continue
            
            print(f"Successfully parsed {len(self.transactions)} transactions")
            return True
            
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found")
            return False
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return False
    
    def create_sample_csv(self, file_path):
        """Create a sample CSV file for demonstration."""
        sample_data = [
            ['Date', 'Description', 'Amount'],
            ['2024-01-15',