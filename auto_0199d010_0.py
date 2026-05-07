```python
"""
Bank Statement Transaction Categorizer

This module reads CSV bank statement files and categorizes transactions based on keywords.
It parses transaction data (date, description, amount) and automatically categorizes
expenses into predefined categories like groceries, utilities, entertainment, and transportation.

Usage: python script.py
"""

import csv
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import os


class TransactionCategorizer:
    def __init__(self):
        self.categories = {
            'groceries': ['grocery', 'supermarket', 'food', 'walmart', 'target', 'costco', 
                         'safeway', 'kroger', 'whole foods', 'trader joe', 'market'],
            'utilities': ['electric', 'gas', 'water', 'internet', 'phone', 'cable', 
                         'utility', 'power', 'energy', 'telecom', 'verizon', 'at&t'],
            'entertainment': ['movie', 'theater', 'netflix', 'spotify', 'amazon prime', 
                            'entertainment', 'game', 'concert', 'bar', 'restaurant'],
            'transportation': ['gas station', 'fuel', 'uber', 'lyft', 'taxi', 'metro', 
                             'bus', 'train', 'parking', 'auto', 'car', 'transport'],
            'dining': ['restaurant', 'cafe', 'pizza', 'mcdonald', 'burger', 'starbucks',
                      'coffee', 'food delivery', 'doordash', 'grubhub'],
            'shopping': ['amazon', 'ebay', 'mall', 'store', 'retail', 'shop', 'purchase'],
            'healthcare': ['pharmacy', 'hospital', 'medical', 'doctor', 'health', 'cvs', 'walgreens'],
            'banking': ['fee', 'interest', 'transfer', 'atm', 'bank', 'withdrawal']
        }
    
    def categorize_transaction(self, description: str) -> str:
        """Categorize a transaction based on its description."""
        description_lower = description.lower()
        
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'other'
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string with multiple format support."""
        formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d', '%m-%d-%Y']
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        return None
    
    def parse_amount(self, amount_str: str) -> float:
        """Parse amount string, handling negative values and currency symbols."""
        amount_str = amount_str.strip()
        # Remove currency symbols and commas
        amount_str = re.sub(r'[$,]', '', amount_str)
        
        # Handle parentheses as negative
        if amount_str.startswith('(') and amount_str.endswith(')'):
            amount_str = '-' + amount_str[1:-1]
        
        try:
            return float(amount_str)
        except ValueError:
            return 0.0
    
    def detect_csv_format(self, filepath: str) -> Optional[Dict[str, int]]:
        """Auto-detect CSV column mapping."""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                header = next(reader)
                
                column_map = {}
                header_lower = [col.lower().strip() for col in header]
                
                # Map common column names
                for i, col in enumerate(header_lower):
                    if any(word in col for word in ['date', 'transaction date', 'posted date']):
                        column_map['date'] = i
                    elif any(word in col for word in ['description', 'memo', 'payee', 'merchant']):
                        column_map['description'] = i
                    elif any(word in col for word in ['amount', 'debit', 'credit', 'transaction amount']):
                        column_map['amount'] = i
                
                return column_map if len(column_map) >= 3 else None
                
        except Exception as e:
            print(f"Error detecting CSV format: {e}")
            return None
    
    def read_csv_file(self, filepath: str) -> List[Tuple[datetime, str, float, str]]:
        """Read and parse CSV bank statement file."""
        transactions = []
        
        try:
            # Auto-detect column mapping
            column_map = self.detect_csv_format(filepath)
            if not column_map:
                print(f"Could not auto-detect CSV format for {filepath}")
                return transactions
            
            with open(filepath, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                header = next(reader)  # Skip header
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        if len(row) <= max(column_map.values()):
                            continue
                        
                        date_str = row[column_map['date']]
                        description = row[column_map['description']]
                        amount_str = row[column_map['amount']]
                        
                        # Parse components
                        date_obj = self.parse_date(date_str)
                        if not date_obj:
                            print(f"Warning: Could not parse date '{date_str}' in row {row_num}")
                            continue
                        
                        amount = self.parse_amount(amount_str)
                        category = self.categorize_transaction(description)
                        
                        transactions.append((date_obj, description, amount, category))
                        
                    except Exception as e:
                        print(f"Error parsing row {row_num}: {e}")
                        continue
                        
        except FileNotFoundError:
            print(f"Error: File '{filepath}' not found")
        except Exception as e:
            print(f"Error reading CSV file: {e}")
        
        return transactions
    
    def generate_summary(self, transactions: List[Tuple[datetime, str, float, str]]) -> Dict:
        """Generate summary statistics."""
        if not transactions:
            return {}
        
        summary = {
            'total_transactions': len(transactions),
            'date_range': {
                'start': min(t[0] for t in transactions),
                'end': max(t[0] for t in transactions)
            },
            'category_totals': {},
            'category_counts': {},
            'total_expenses': 0,
            'total_income': 0
        }
        
        for date, description, amount, category in transactions:
            if category not in summary['category_totals']:
                summary['category_totals'][category] = 0
                summary['category_counts'][category] = 0
            
            summary['category_totals'][category] += amount
            summary['category_counts'][category] += 1
            
            if amount < 0:
                summary['total_expenses'] += abs(amount)
            else:
                summary['total_income'] += amount
        
        return summary


def create_sample_csv():
    """Create a sample CSV file for testing."""
    sample_data = [
        ['Date', 'Description', 'Amount'],
        ['2024-01-15', 'Walmart Grocery Store', '-125.50'],
        ['2024-01-16', 'Electric Company Payment', '-89.25'],
        ['2024-01-17', 'Netflix Subscription', '-15.99'],
        ['2024-01-18', 'Shell Gas Station', '-45.00'],
        ['2024-01-19', 'Starbucks Coffee', '-6.75'],
        ['2024-01-20', 'Salary Deposit', '2500.00'],
        ['2024-01