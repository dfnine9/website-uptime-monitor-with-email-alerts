```python
#!/usr/bin/env python3
"""
Transaction Categorizer Script

This script reads CSV files containing transaction data and categorizes transactions
based on merchant names and amounts using regex patterns. It's designed to help
analyze financial data by automatically grouping transactions into meaningful categories.

Features:
- Reads transaction data from CSV files
- Uses regex patterns to match merchant names
- Categorizes transactions by amount ranges
- Handles errors gracefully
- Outputs categorized results to stdout

Usage: python script.py

Dependencies: Only standard library modules (csv, re, os, sys)
"""

import csv
import re
import os
import sys
from typing import Dict, List, Tuple, Any
from collections import defaultdict


class TransactionCategorizer:
    """Categorizes transactions based on merchant names and amounts."""
    
    def __init__(self):
        # Define merchant category patterns
        self.merchant_patterns = {
            'Grocery': [
                r'.*walmart.*', r'.*kroger.*', r'.*safeway.*', r'.*whole foods.*',
                r'.*trader joe.*', r'.*costco.*', r'.*target.*', r'.*grocery.*'
            ],
            'Restaurant': [
                r'.*mcdonalds.*', r'.*starbucks.*', r'.*subway.*', r'.*pizza.*',
                r'.*restaurant.*', r'.*cafe.*', r'.*bistro.*', r'.*diner.*'
            ],
            'Gas Station': [
                r'.*shell.*', r'.*exxon.*', r'.*chevron.*', r'.*bp.*',
                r'.*texaco.*', r'.*gas.*', r'.*fuel.*'
            ],
            'Online Shopping': [
                r'.*amazon.*', r'.*ebay.*', r'.*paypal.*', r'.*etsy.*',
                r'.*shopify.*', r'.*stripe.*'
            ],
            'Utilities': [
                r'.*electric.*', r'.*water.*', r'.*gas company.*', r'.*utility.*',
                r'.*power.*', r'.*energy.*'
            ],
            'Entertainment': [
                r'.*netflix.*', r'.*spotify.*', r'.*cinema.*', r'.*theater.*',
                r'.*movie.*', r'.*gaming.*', r'.*steam.*'
            ]
        }
        
        # Amount categories
        self.amount_categories = {
            'Micro': (0, 10),
            'Small': (10.01, 50),
            'Medium': (50.01, 200),
            'Large': (200.01, 1000),
            'Extra Large': (1000.01, float('inf'))
        }
    
    def categorize_merchant(self, merchant_name: str) -> str:
        """Categorize merchant based on name patterns."""
        if not merchant_name:
            return 'Unknown'
        
        merchant_lower = merchant_name.lower()
        
        for category, patterns in self.merchant_patterns.items():
            for pattern in patterns:
                if re.search(pattern, merchant_lower, re.IGNORECASE):
                    return category
        
        return 'Other'
    
    def categorize_amount(self, amount: float) -> str:
        """Categorize transaction based on amount."""
        amount = abs(amount)  # Use absolute value
        
        for category, (min_val, max_val) in self.amount_categories.items():
            if min_val <= amount <= max_val:
                return category
        
        return 'Unknown'
    
    def parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float, handling various formats."""
        try:
            # Remove currency symbols and whitespace
            cleaned = re.sub(r'[$,\s]', '', str(amount_str))
            # Handle negative amounts in parentheses
            if cleaned.startswith('(') and cleaned.endswith(')'):
                cleaned = '-' + cleaned[1:-1]
            return float(cleaned)
        except (ValueError, TypeError):
            return 0.0
    
    def read_csv_file(self, filepath: str) -> List[Dict[str, Any]]:
        """Read and parse CSV file."""
        transactions = []
        
        try:
            with open(filepath, 'r', newline='', encoding='utf-8') as file:
                # Try to detect delimiter
                sample = file.read(1024)
                file.seek(0)
                
                delimiter = ','
                if sample.count(';') > sample.count(','):
                    delimiter = ';'
                elif sample.count('\t') > sample.count(','):
                    delimiter = '\t'
                
                reader = csv.DictReader(file, delimiter=delimiter)
                
                for row_num, row in enumerate(reader, 1):
                    try:
                        # Try common column names for merchant and amount
                        merchant = (row.get('merchant') or row.get('Merchant') or 
                                  row.get('description') or row.get('Description') or 
                                  row.get('payee') or row.get('Payee') or '').strip()
                        
                        amount_str = (row.get('amount') or row.get('Amount') or 
                                    row.get('value') or row.get('Value') or '0')
                        
                        amount = self.parse_amount(amount_str)
                        
                        transaction = {
                            'row': row_num,
                            'merchant': merchant,
                            'amount': amount,
                            'raw_data': row
                        }
                        
                        transactions.append(transaction)
                        
                    except Exception as e:
                        print(f"Warning: Error processing row {row_num}: {e}", file=sys.stderr)
                        continue
                        
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file not found: {filepath}")
        except Exception as e:
            raise Exception(f"Error reading CSV file {filepath}: {e}")
        
        return transactions
    
    def categorize_transactions(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Categorize all transactions and return summary."""
        categorized = defaultdict(lambda: defaultdict(list))
        merchant_stats = defaultdict(int)
        amount_stats = defaultdict(int)
        
        for transaction in transactions:
            merchant_category = self.categorize_merchant(transaction['merchant'])
            amount_category = self.categorize_amount(transaction['amount'])
            
            # Store in categorized structure
            categorized[merchant_category][amount_category].append(transaction)
            
            # Update statistics
            merchant_stats[merchant_category] += 1
            amount_stats[amount_category] += 1
        
        return {
            'categorized': dict(categorized),
            'merchant_stats': dict(merchant_stats),
            'amount_stats': dict(amount_stats),
            'total_transactions': len(transactions)
        }
    
    def print_results(self, results: Dict[str, Any]):
        """Print categorized results to stdout."""
        print("=" * 60)
        print("TRANSACTION CATEGORIZATION RESULTS")
        print("=" * 60)
        
        print(f"\nTotal Transactions Processed: {results['total_transactions']}")
        
        # Print merchant category statistics
        print("\nMERCHANT CATEGORY BREAKDOWN:")
        print("-" * 30)
        for category, count in sorted(results['merchant_stats'].items(), 
                                    key=lambda x: x[1], reverse=True):
            percentage = (count / results['total_transactions']) * 100
            print(f"{category:.<20} {count:>5} ({percentage:>5.1f}%)")
        
        # Print amount category statistics
        print("\nAMOUNT CATEGORY BREAKDOWN:")
        print("-" * 30)
        for category, count in sorted(results['amount_stats'].items(), 
                                    key=lambda x: x[1], reverse=True):
            percentage = (count / results['total_transactions']) * 100
            print(f"{category:.<20} {count:>5} ({percentage:>5.1f}%)")