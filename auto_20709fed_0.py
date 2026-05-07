```python
"""
Bank Statement Transaction Categorizer

This module parses CSV bank statements and automatically categorizes transactions
based on configurable keyword patterns in transaction descriptions. It provides
a flexible rule-based system for financial transaction classification.

Features:
- Parses CSV bank statements with configurable column mapping
- Configurable categorization rules with keyword patterns
- Case-insensitive pattern matching
- Error handling for malformed data
- Summary statistics and detailed transaction listing

Usage:
    python script.py

The script expects a CSV file named 'bank_statement.csv' in the same directory
with columns: Date, Description, Amount, Balance
"""

import csv
import re
import os
from typing import Dict, List, Tuple, Any
from datetime import datetime


class TransactionCategorizer:
    """Categorizes bank transactions based on description patterns."""
    
    def __init__(self):
        """Initialize with default categorization rules."""
        self.rules = {
            'Food & Dining': [
                r'restaurant', r'cafe', r'coffee', r'pizza', r'burger',
                r'mcdonald', r'subway', r'starbucks', r'domino', r'kfc',
                r'grocery', r'supermarket', r'food', r'dining'
            ],
            'Transportation': [
                r'gas station', r'fuel', r'uber', r'lyft', r'taxi',
                r'metro', r'bus', r'train', r'parking', r'toll'
            ],
            'Shopping': [
                r'amazon', r'walmart', r'target', r'mall', r'store',
                r'shopping', r'retail', r'purchase'
            ],
            'Entertainment': [
                r'movie', r'cinema', r'netflix', r'spotify', r'game',
                r'entertainment', r'theater', r'concert'
            ],
            'Bills & Utilities': [
                r'electric', r'water', r'gas bill', r'internet', r'phone',
                r'insurance', r'utility', r'bill payment'
            ],
            'Banking & Finance': [
                r'transfer', r'deposit', r'withdrawal', r'fee', r'interest',
                r'atm', r'bank', r'credit'
            ],
            'Healthcare': [
                r'pharmacy', r'doctor', r'medical', r'hospital', r'clinic',
                r'health', r'dental'
            ],
            'Income': [
                r'salary', r'payroll', r'income', r'wages', r'deposit.*employer'
            ]
        }
    
    def categorize_transaction(self, description: str) -> str:
        """
        Categorize a transaction based on its description.
        
        Args:
            description: Transaction description text
            
        Returns:
            Category name or 'Uncategorized' if no match found
        """
        description_lower = description.lower()
        
        for category, patterns in self.rules.items():
            for pattern in patterns:
                if re.search(pattern, description_lower):
                    return category
        
        return 'Uncategorized'
    
    def add_rule(self, category: str, patterns: List[str]) -> None:
        """Add or update categorization rules."""
        if category in self.rules:
            self.rules[category].extend(patterns)
        else:
            self.rules[category] = patterns
    
    def get_rules(self) -> Dict[str, List[str]]:
        """Get current categorization rules."""
        return self.rules.copy()


class BankStatementParser:
    """Parses CSV bank statements and categorizes transactions."""
    
    def __init__(self, categorizer: TransactionCategorizer):
        """Initialize with a transaction categorizer."""
        self.categorizer = categorizer
        self.transactions = []
        
    def parse_csv(self, filepath: str, 
                  date_col: str = 'Date',
                  description_col: str = 'Description', 
                  amount_col: str = 'Amount',
                  balance_col: str = 'Balance') -> List[Dict[str, Any]]:
        """
        Parse CSV bank statement and categorize transactions.
        
        Args:
            filepath: Path to CSV file
            date_col: Name of date column
            description_col: Name of description column
            amount_col: Name of amount column
            balance_col: Name of balance column
            
        Returns:
            List of categorized transactions
        """
        transactions = []
        
        try:
            with open(filepath, 'r', newline='', encoding='utf-8') as csvfile:
                # Detect delimiter
                sample = csvfile.read(1024)
                csvfile.seek(0)
                
                delimiter = ','
                if '\t' in sample:
                    delimiter = '\t'
                elif ';' in sample:
                    delimiter = ';'
                
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        # Validate required columns exist
                        if not all(col in row for col in [date_col, description_col, amount_col]):
                            print(f"Warning: Row {row_num} missing required columns")
                            continue
                        
                        # Parse date
                        date_str = row[date_col].strip()
                        try:
                            # Try common date formats
                            for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']:
                                try:
                                    parsed_date = datetime.strptime(date_str, fmt)
                                    break
                                except ValueError:
                                    continue
                            else:
                                print(f"Warning: Could not parse date '{date_str}' in row {row_num}")
                                parsed_date = None
                        except Exception:
                            parsed_date = None
                        
                        # Parse amount
                        amount_str = row[amount_col].strip().replace('$', '').replace(',', '')
                        try:
                            amount = float(amount_str)
                        except ValueError:
                            print(f"Warning: Could not parse amount '{amount_str}' in row {row_num}")
                            continue
                        
                        # Parse balance (optional)
                        balance = None
                        if balance_col in row:
                            balance_str = row[balance_col].strip().replace('$', '').replace(',', '')
                            try:
                                balance = float(balance_str)
                            except ValueError:
                                pass
                        
                        # Get description and categorize
                        description = row[description_col].strip()
                        category = self.categorizer.categorize_transaction(description)
                        
                        transaction = {
                            'date': parsed_date,
                            'date_str': date_str,
                            'description': description,
                            'amount': amount,
                            'balance': balance,
                            'category': category
                        }
                        
                        transactions.append(transaction)
                        
                    except Exception as e:
                        print(f"Error processing row {row_num}: {e}")
                        continue
                        
        except FileNotFoundError:
            raise FileNotFoundError(f"Bank statement file '{filepath}' not found")
        except Exception as e:
            raise Exception(f"Error reading CSV file: {e}")
        
        self.transactions = transactions
        return transactions
    
    def get_category_summary(self) -> Dict[str, Dict[str, Any]]:
        """Generate summary statistics by category."""
        summary = {}
        
        for transaction in self.transactions:
            category = transaction['category']
            amount = transaction['amount']
            
            if category not in summary:
                summary[category] = {
                    'count': 0,
                    'total': 0.0,
                    'avg': 0.0,
                    'min': float('inf'),
                    'max': float('-inf')
                }
            
            summary[category]['count'] += 1
            summary[category]['total'] += amount
            summary[category]['min'] = min(summary[category]['min'], amount)
            summary[category]['max'] = max(summary[category]['max'], amount)