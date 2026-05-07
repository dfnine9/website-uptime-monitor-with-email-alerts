```python
#!/usr/bin/env python3
"""
Transaction Expense Categorizer

This module parses CSV transaction files, validates data structure, and implements
rule-based expense categorization using keyword matching and merchant name patterns.
Categorizes transactions into common categories like groceries, gas, restaurants,
utilities, and entertainment.

Usage:
    python script.py

The script expects a CSV file named 'transactions.csv' in the same directory with
columns: date, description, amount, merchant (optional)
"""

import csv
import re
import sys
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class TransactionCategorizer:
    def __init__(self):
        """Initialize the categorizer with predefined category rules."""
        self.category_rules = {
            'groceries': {
                'keywords': ['grocery', 'market', 'food', 'supermarket', 'produce'],
                'merchants': ['walmart', 'target', 'kroger', 'safeway', 'publix', 'whole foods',
                             'trader joe', 'costco', 'sams club', 'aldi', 'wegmans']
            },
            'gas': {
                'keywords': ['gas', 'fuel', 'petroleum', 'station'],
                'merchants': ['shell', 'exxon', 'bp', 'chevron', 'mobil', 'texaco',
                             'sunoco', 'citgo', 'marathon', 'speedway', 'wawa']
            },
            'restaurants': {
                'keywords': ['restaurant', 'cafe', 'diner', 'pizza', 'burger', 'grill',
                           'kitchen', 'bistro', 'bar', 'pub', 'food truck'],
                'merchants': ['mcdonalds', 'subway', 'starbucks', 'dunkin', 'kfc',
                             'taco bell', 'pizza hut', 'dominos', 'chipotle', 'panera']
            },
            'utilities': {
                'keywords': ['electric', 'gas company', 'water', 'sewer', 'internet',
                           'cable', 'phone', 'utility', 'power', 'energy'],
                'merchants': ['verizon', 'att', 'comcast', 'xfinity', 'spectrum',
                             'tmobile', 'sprint', 'duke energy', 'pge', 'con edison']
            },
            'entertainment': {
                'keywords': ['movie', 'theater', 'cinema', 'netflix', 'spotify',
                           'gaming', 'streaming', 'concert', 'show', 'entertainment'],
                'merchants': ['netflix', 'spotify', 'hulu', 'disney', 'amazon prime',
                             'xbox', 'playstation', 'steam', 'ticketmaster', 'amc']
            }
        }
    
    def validate_csv_structure(self, filepath: str) -> Tuple[bool, str]:
        """
        Validate CSV file structure and required columns.
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                headers = reader.fieldnames
                
                if not headers:
                    return False, "CSV file is empty or has no headers"
                
                required_columns = ['date', 'description', 'amount']
                missing_columns = [col for col in required_columns if col not in headers]
                
                if missing_columns:
                    return False, f"Missing required columns: {', '.join(missing_columns)}"
                
                # Check if file has at least one data row
                try:
                    next(reader)
                except StopIteration:
                    return False, "CSV file has headers but no data rows"
                
                return True, "CSV structure is valid"
                
        except FileNotFoundError:
            return False, f"File not found: {filepath}"
        except Exception as e:
            return False, f"Error reading CSV file: {str(e)}"
    
    def categorize_transaction(self, description: str, merchant: str = "") -> str:
        """
        Categorize a transaction based on description and merchant.
        
        Args:
            description: Transaction description
            merchant: Merchant name (optional)
            
        Returns:
            Category name or 'other' if no match found
        """
        text_to_analyze = f"{description} {merchant}".lower()
        
        for category, rules in self.category_rules.items():
            # Check keywords
            for keyword in rules['keywords']:
                if keyword in text_to_analyze:
                    return category
            
            # Check merchant patterns
            for merchant_pattern in rules['merchants']:
                if merchant_pattern in text_to_analyze:
                    return category
        
        return 'other'
    
    def parse_amount(self, amount_str: str) -> Optional[float]:
        """
        Parse amount string to float, handling various formats.
        
        Args:
            amount_str: Amount as string
            
        Returns:
            Parsed amount or None if invalid
        """
        try:
            # Remove currency symbols and whitespace
            cleaned = re.sub(r'[$,\s]', '', amount_str.strip())
            
            # Handle negative amounts in parentheses
            if cleaned.startswith('(') and cleaned.endswith(')'):
                cleaned = '-' + cleaned[1:-1]
            
            return float(cleaned)
        except (ValueError, TypeError):
            return None
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse date string to datetime object, trying common formats.
        
        Args:
            date_str: Date as string
            
        Returns:
            Parsed datetime or None if invalid
        """
        date_formats = ['%Y-%m-%d', '%m/%d/%Y', '%m-%d-%Y', '%d/%m/%Y', '%Y/%m/%d']
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        return None
    
    def process_transactions(self, filepath: str) -> List[Dict]:
        """
        Process all transactions from CSV file.
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            List of processed transaction dictionaries
        """
        transactions = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row_num, row in enumerate(reader, start=2):  # Start at 2 for header
                    transaction = {
                        'row_number': row_num,
                        'original_data': row,
                        'errors': []
                    }
                    
                    # Parse date
                    date_obj = self.parse_date(row.get('date', ''))
                    if date_obj:
                        transaction['date'] = date_obj
                    else:
                        transaction['errors'].append(f"Invalid date format: {row.get('date', 'N/A')}")
                    
                    # Parse amount
                    amount = self.parse_amount(row.get('amount', ''))
                    if amount is not None:
                        transaction['amount'] = amount
                    else:
                        transaction['errors'].append(f"Invalid amount format: {row.get('amount', 'N/A')}")
                    
                    # Extract description and merchant
                    transaction['description'] = row.get('description', '').strip()
                    transaction['merchant'] = row.get('merchant', '').strip()
                    
                    # Categorize transaction
                    transaction['category'] = self.categorize_transaction(
                        transaction['description'],
                        transaction['merchant']
                    )
                    
                    transactions.append(transaction)
                    
        except Exception as e:
            print(f"Error processing transactions: {str(e)}", file=sys.stderr)
            return []
        
        return transactions
    
    def generate_report(