```python
"""
Bank Transaction Categorizer

This module parses CSV bank transaction files and automatically categorizes transactions
based on keyword matching rules. It supports common transaction categories like groceries,
utilities, entertainment, etc.

The script reads a CSV file with transaction data, applies categorization rules based on
transaction descriptions, and outputs the results with category tags.

Usage: python script.py

The script expects a CSV file named 'transactions.csv' in the same directory with columns:
- Date
- Description 
- Amount
- (optional) Category

If no CSV file exists, it creates a sample one for demonstration.
"""

import csv
import os
import sys
from typing import List, Dict, Any
from datetime import datetime


class TransactionCategorizer:
    """Categorizes bank transactions based on keyword matching rules."""
    
    def __init__(self):
        """Initialize categorizer with predefined category rules."""
        self.category_rules = {
            'groceries': [
                'grocery', 'supermarket', 'walmart', 'target', 'kroger', 'safeway',
                'whole foods', 'trader joe', 'costco', 'sams club', 'food lion',
                'publix', 'wegmans', 'giant', 'stop shop', 'market', 'fresh'
            ],
            'utilities': [
                'electric', 'gas', 'water', 'sewer', 'internet', 'cable', 'phone',
                'utility', 'power', 'energy', 'verizon', 'comcast', 'att', 'sprint'
            ],
            'entertainment': [
                'netflix', 'spotify', 'amazon prime', 'hulu', 'disney', 'movie',
                'theater', 'cinema', 'concert', 'show', 'game', 'entertainment'
            ],
            'restaurants': [
                'restaurant', 'cafe', 'pizza', 'burger', 'mcdonalds', 'subway',
                'starbucks', 'dunkin', 'kfc', 'taco bell', 'wendys', 'dining'
            ],
            'gas': [
                'shell', 'exxon', 'bp', 'chevron', 'mobil', 'gas station',
                'fuel', 'gasoline', 'petrol'
            ],
            'healthcare': [
                'pharmacy', 'cvs', 'walgreens', 'hospital', 'medical', 'doctor',
                'dental', 'health', 'clinic'
            ],
            'shopping': [
                'amazon', 'ebay', 'best buy', 'home depot', 'lowes', 'macy',
                'nordstrom', 'gap', 'old navy', 'shopping'
            ],
            'transportation': [
                'uber', 'lyft', 'taxi', 'bus', 'train', 'airline', 'parking',
                'metro', 'transit'
            ],
            'banking': [
                'bank', 'atm', 'fee', 'transfer', 'deposit', 'withdrawal',
                'interest', 'overdraft'
            ]
        }
    
    def categorize_transaction(self, description: str) -> str:
        """
        Categorize a transaction based on its description.
        
        Args:
            description: Transaction description text
            
        Returns:
            Category name or 'other' if no match found
        """
        description_lower = description.lower()
        
        for category, keywords in self.category_rules.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'other'
    
    def parse_csv_file(self, filename: str) -> List[Dict[str, Any]]:
        """
        Parse CSV file and return list of transaction dictionaries.
        
        Args:
            filename: Path to CSV file
            
        Returns:
            List of transaction dictionaries
            
        Raises:
            FileNotFoundError: If CSV file doesn't exist
            ValueError: If CSV format is invalid
        """
        transactions = []
        
        try:
            with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
                # Try to detect delimiter
                sample = csvfile.read(1024)
                csvfile.seek(0)
                
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                
                # Validate required columns
                required_columns = {'date', 'description', 'amount'}
                if not required_columns.issubset(col.lower() for col in reader.fieldnames):
                    raise ValueError(f"CSV must contain columns: {required_columns}")
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        # Normalize column names to lowercase
                        normalized_row = {k.lower(): v for k, v in row.items()}
                        
                        # Validate required fields
                        if not all(normalized_row.get(col) for col in required_columns):
                            print(f"Warning: Skipping row {row_num} - missing required data")
                            continue
                        
                        # Parse amount
                        amount_str = normalized_row['amount'].replace('$', '').replace(',', '')
                        amount = float(amount_str)
                        
                        transaction = {
                            'date': normalized_row['date'],
                            'description': normalized_row['description'],
                            'amount': amount,
                            'original_category': normalized_row.get('category', '')
                        }
                        
                        transactions.append(transaction)
                        
                    except (ValueError, KeyError) as e:
                        print(f"Warning: Error parsing row {row_num}: {e}")
                        continue
                        
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file '{filename}' not found")
        except Exception as e:
            raise ValueError(f"Error reading CSV file: {e}")
        
        return transactions
    
    def create_sample_csv(self, filename: str):
        """Create a sample CSV file for demonstration."""
        sample_data = [
            ['Date', 'Description', 'Amount', 'Category'],
            ['2024-01-15', 'WALMART SUPERCENTER #1234', '-89.45', ''],
            ['2024-01-16', 'STARBUCKS COFFEE #567', '-5.75', ''],
            ['2024-01-17', 'ELECTRIC COMPANY PAYMENT', '-125.50', ''],
            ['2024-01-18', 'NETFLIX MONTHLY SUBSCRIPTION', '-15.99', ''],
            ['2024-01-19', 'SHELL GAS STATION', '-45.20', ''],
            ['2024-01-20', 'CVS PHARMACY #890', '-32.18', ''],
            ['2024-01-21', 'AMAZON.COM PURCHASE', '-67.89', ''],
            ['2024-01-22', 'UBER RIDE', '-18.50', ''],
            ['2024-01-23', 'MCDONALDS #1122', '-12.35', ''],
            ['2024-01-24', 'BANK ATM FEE', '-3.00', '']
        ]
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(sample_data)
            print(f"Created sample CSV file: {filename}")
        except Exception as e:
            print(f"Error creating sample CSV: {e}")
    
    def process_transactions(self, filename: str = 'transactions.csv'):
        """
        Main processing function that categorizes transactions and prints results.
        
        Args:
            filename: Path to CSV file (default: 'transactions.csv')
        """
        try:
            # Check if CSV file exists, create sample if not
            if not os.path.exists(filename):
                print(f"CSV file '{filename}' not found. Creating sample file...")
                self.create_sample_csv(filename)
                print()
            
            # Parse