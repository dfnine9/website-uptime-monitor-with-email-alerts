```python
"""
Bank Statement Transaction Categorizer

This module reads CSV bank statement files and categorizes transactions based on keywords.
It calculates spending totals by category and supports date range filtering.

The script expects CSV files with columns: date, description, amount
Date format should be YYYY-MM-DD or MM/DD/YYYY
Amount should be numeric (negative for expenses, positive for income)

Usage: python script.py
"""

import csv
import re
import sys
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Optional


class TransactionCategorizer:
    def __init__(self):
        self.categories = {
            'groceries': ['grocery', 'supermarket', 'food', 'market', 'kroger', 'walmart', 'target', 'safeway', 'whole foods'],
            'utilities': ['electric', 'gas', 'water', 'internet', 'phone', 'cable', 'utility', 'power', 'energy'],
            'entertainment': ['netflix', 'spotify', 'movie', 'theater', 'gaming', 'steam', 'entertainment', 'music'],
            'transportation': ['gas station', 'fuel', 'uber', 'lyft', 'taxi', 'parking', 'metro', 'bus', 'train'],
            'dining': ['restaurant', 'cafe', 'coffee', 'pizza', 'mcdonald', 'starbucks', 'dining', 'bar', 'pub'],
            'shopping': ['amazon', 'ebay', 'store', 'mall', 'retail', 'clothing', 'shoes', 'electronics'],
            'healthcare': ['pharmacy', 'doctor', 'hospital', 'medical', 'dental', 'health', 'cvs', 'walgreens'],
            'banking': ['fee', 'charge', 'interest', 'bank', 'atm', 'transfer', 'payment'],
            'insurance': ['insurance', 'premium', 'policy', 'coverage'],
            'other': []
        }
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string in various formats"""
        date_formats = ['%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y', '%d/%m/%Y', '%Y/%m/%d']
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        return None
    
    def categorize_transaction(self, description: str) -> str:
        """Categorize transaction based on description keywords"""
        description_lower = description.lower()
        
        for category, keywords in self.categories.items():
            if category == 'other':
                continue
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'other'
    
    def read_csv_file(self, filename: str) -> List[Dict]:
        """Read and parse CSV bank statement file"""
        transactions = []
        
        try:
            with open(filename, 'r', newline='', encoding='utf-8') as file:
                # Try to detect delimiter
                sample = file.read(1024)
                file.seek(0)
                
                delimiter = ',' if ',' in sample else ';' if ';' in sample else '\t'
                reader = csv.reader(file, delimiter=delimiter)
                
                # Read header
                headers = next(reader)
                headers = [h.lower().strip() for h in headers]
                
                # Find column indices
                date_col = self._find_column_index(headers, ['date', 'transaction date', 'posted date'])
                desc_col = self._find_column_index(headers, ['description', 'memo', 'details', 'transaction'])
                amount_col = self._find_column_index(headers, ['amount', 'debit', 'credit', 'transaction amount'])
                
                if date_col == -1 or desc_col == -1 or amount_col == -1:
                    raise ValueError(f"Could not find required columns in {filename}")
                
                # Read transactions
                for row_num, row in enumerate(reader, start=2):
                    if len(row) <= max(date_col, desc_col, amount_col):
                        continue
                    
                    try:
                        date_obj = self.parse_date(row[date_col])
                        if not date_obj:
                            print(f"Warning: Could not parse date '{row[date_col]}' in row {row_num}")
                            continue
                        
                        # Clean and parse amount
                        amount_str = re.sub(r'[,$\s]', '', row[amount_col])
                        amount_str = amount_str.replace('(', '-').replace(')', '')
                        
                        try:
                            amount = float(amount_str)
                        except ValueError:
                            print(f"Warning: Could not parse amount '{row[amount_col]}' in row {row_num}")
                            continue
                        
                        transaction = {
                            'date': date_obj,
                            'description': row[desc_col].strip(),
                            'amount': amount,
                            'category': self.categorize_transaction(row[desc_col])
                        }
                        
                        transactions.append(transaction)
                        
                    except Exception as e:
                        print(f"Warning: Error processing row {row_num}: {e}")
                        continue
                        
        except FileNotFoundError:
            raise FileNotFoundError(f"File '{filename}' not found")
        except Exception as e:
            raise Exception(f"Error reading file '{filename}': {e}")
        
        return transactions
    
    def _find_column_index(self, headers: List[str], possible_names: List[str]) -> int:
        """Find column index by matching possible column names"""
        for i, header in enumerate(headers):
            for name in possible_names:
                if name in header:
                    return i
        return -1
    
    def filter_by_date_range(self, transactions: List[Dict], 
                           start_date: Optional[str] = None, 
                           end_date: Optional[str] = None) -> List[Dict]:
        """Filter transactions by date range"""
        filtered = transactions.copy()
        
        if start_date:
            start_dt = self.parse_date(start_date)
            if start_dt:
                filtered = [t for t in filtered if t['date'] >= start_dt]
            else:
                print(f"Warning: Could not parse start date '{start_date}'")
        
        if end_date:
            end_dt = self.parse_date(end_date)
            if end_dt:
                filtered = [t for t in filtered if t['date'] <= end_dt]
            else:
                print(f"Warning: Could not parse end date '{end_date}'")
        
        return filtered
    
    def calculate_category_totals(self, transactions: List[Dict]) -> Dict[str, float]:
        """Calculate spending totals by category"""
        category_totals = defaultdict(float)
        
        for transaction in transactions:
            amount = transaction['amount']
            category = transaction['category']
            
            # Only count expenses (negative amounts) for spending analysis
            if amount < 0:
                category_totals[category] += abs(amount)
        
        return dict(category_totals)
    
    def print_summary(self, transactions: List[Dict], category_totals: Dict[str, float]):
        """Print transaction summary and category breakdown"""
        print(f"\n{'='*60}")
        print("TRANSACTION ANALYSIS SUMMARY")
        print(f"{'='*60}")
        
        total_transactions = len(transactions)
        total_expenses = sum(abs(t['amount']) for t in transactions if t['amount'] < 0)
        total_income = sum(t['amount'] for t in transactions if t['amount'] > 0)
        net_amount = total_income - total_expenses
        
        print(f"Total Transactions: {total_transactions}")
        print(f"Total Expenses: ${total_expenses:,.2f}")