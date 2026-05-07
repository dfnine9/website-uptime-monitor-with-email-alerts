```python
#!/usr/bin/env python3
"""
Bank Transaction CSV Normalizer and Categorization Engine

This module reads CSV files from various bank formats, normalizes transaction data
(date, description, amount), and categorizes transactions using keyword-based rules.

Supports common bank CSV formats and provides flexible categorization with
predefined expense categories including groceries, utilities, entertainment,
transportation, and more.

Usage: python script.py
"""

import csv
import re
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Transaction:
    """Represents a normalized bank transaction."""
    date: datetime
    description: str
    amount: float
    category: str = "Other"
    raw_data: dict = None


class BankCSVNormalizer:
    """Normalizes CSV data from different bank formats."""
    
    # Common field mappings for different banks
    FIELD_MAPPINGS = {
        'chase': {
            'date': ['Transaction Date', 'Date'],
            'description': ['Description'],
            'amount': ['Amount']
        },
        'bofa': {
            'date': ['Posted Date', 'Date'],
            'description': ['Payee', 'Description'],
            'amount': ['Amount']
        },
        'wells_fargo': {
            'date': ['Date'],
            'description': ['Description'],
            'amount': ['Amount']
        },
        'generic': {
            'date': ['date', 'Date', 'transaction_date', 'posted_date'],
            'description': ['description', 'Description', 'payee', 'Payee', 'memo'],
            'amount': ['amount', 'Amount', 'debit', 'credit']
        }
    }
    
    def detect_bank_format(self, headers: List[str]) -> str:
        """Detect bank format based on CSV headers."""
        headers_lower = [h.lower() for h in headers]
        
        if 'transaction date' in headers_lower:
            return 'chase'
        elif 'posted date' in headers_lower:
            return 'bofa'
        elif any('wells' in h.lower() for h in headers):
            return 'wells_fargo'
        else:
            return 'generic'
    
    def normalize_date(self, date_str: str) -> Optional[datetime]:
        """Normalize various date formats to datetime object."""
        if not date_str or date_str.strip() == '':
            return None
            
        date_str = date_str.strip()
        
        # Common date formats
        date_formats = [
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%m/%d/%y',
            '%m-%d-%Y',
            '%m-%d-%y',
            '%d/%m/%Y',
            '%Y/%m/%d'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
                
        print(f"Warning: Could not parse date '{date_str}'")
        return None
    
    def normalize_amount(self, amount_str: str) -> float:
        """Normalize amount string to float."""
        if not amount_str or amount_str.strip() == '':
            return 0.0
            
        # Remove currency symbols, commas, and extra spaces
        clean_amount = re.sub(r'[^\d.-]', '', amount_str.strip())
        
        try:
            return float(clean_amount)
        except ValueError:
            print(f"Warning: Could not parse amount '{amount_str}'")
            return 0.0
    
    def find_field_value(self, row: dict, field_names: List[str]) -> str:
        """Find field value from row using possible field names."""
        for field_name in field_names:
            if field_name in row and row[field_name]:
                return row[field_name]
        return ""
    
    def normalize_csv(self, csv_path: str) -> List[Transaction]:
        """Normalize CSV file to standard transaction format."""
        transactions = []
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                # Try to detect delimiter
                sample = file.read(1024)
                file.seek(0)
                
                delimiter = ','
                if '\t' in sample:
                    delimiter = '\t'
                elif ';' in sample:
                    delimiter = ';'
                
                reader = csv.DictReader(file, delimiter=delimiter)
                headers = reader.fieldnames
                
                if not headers:
                    print(f"Error: No headers found in {csv_path}")
                    return transactions
                
                bank_format = self.detect_bank_format(headers)
                field_mapping = self.FIELD_MAPPINGS[bank_format]
                
                print(f"Detected format: {bank_format}")
                print(f"Headers: {headers}")
                
                for row in reader:
                    try:
                        # Extract and normalize fields
                        date_str = self.find_field_value(row, field_mapping['date'])
                        description = self.find_field_value(row, field_mapping['description'])
                        amount_str = self.find_field_value(row, field_mapping['amount'])
                        
                        # Normalize values
                        transaction_date = self.normalize_date(date_str)
                        amount = self.normalize_amount(amount_str)
                        
                        if transaction_date and description:
                            transaction = Transaction(
                                date=transaction_date,
                                description=description.strip(),
                                amount=amount,
                                raw_data=dict(row)
                            )
                            transactions.append(transaction)
                        
                    except Exception as e:
                        print(f"Warning: Error processing row {row}: {e}")
                        continue
                        
        except FileNotFoundError:
            print(f"Error: File {csv_path} not found")
        except Exception as e:
            print(f"Error reading {csv_path}: {e}")
            
        return transactions


class TransactionCategorizer:
    """Categorizes transactions based on keyword matching."""
    
    def __init__(self):
        self.categories = {
            'Groceries': [
                'walmart', 'target', 'safeway', 'kroger', 'publix', 'whole foods',
                'trader joe', 'costco', 'sams club', 'grocery', 'supermarket',
                'food lion', 'harris teeter', 'giant', 'wegmans', 'aldi',
                'fresh market', 'market', 'organic'
            ],
            'Utilities': [
                'electric', 'electricity', 'power', 'gas', 'water', 'sewer',
                'internet', 'cable', 'phone', 'wireless', 'verizon', 'att',
                'comcast', 'xfinity', 'spectrum', 'utility', 'energy',
                'trash', 'garbage', 'waste management'
            ],
            'Transportation': [
                'gas station', 'shell', 'exxon', 'chevron', 'bp', 'mobil',
                'uber', 'lyft', 'taxi', 'metro', 'bus', 'train', 'subway',
                'parking', 'toll', 'car wash', 'auto', 'automotive',
                'repair', 'maintenance', 'dmv', 'registration'
            ],
            'Entertainment': [
                'netflix', 'hulu', 'disney', 'amazon prime', 'spotify',
                'apple music', 'movie', 'theater', 'cinema', 'concert',
                'game', 'gaming', 'entertainment', 'recreation', 'fun',
                'bar', 'club', 'brewery', 'casino', 'sports'
            ],
            'Dining': [
                'restaurant', 'mcdonalds', 'burger king', 'subway', 'pizza',
                'starbucks', 'dunkin', 'coffee', 'cafe', 'diner',