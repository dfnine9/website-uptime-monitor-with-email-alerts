```python
"""
Transaction Categorizer and Spending Pattern Analyzer

This module provides functionality to parse CSV transaction files, categorize transactions
using keyword matching, and calculate spending patterns by category. It processes financial
transaction data to provide insights into spending habits.

Features:
- CSV transaction parsing with flexible column detection
- Keyword-based transaction categorization
- Spending pattern analysis with statistics
- Error handling for file operations and data processing
- Self-contained with minimal dependencies

Usage:
    python script.py

The script will look for a 'transactions.csv' file in the current directory or create
a sample file if none exists.
"""

import csv
import sys
from collections import defaultdict
from datetime import datetime
import os
import re


class TransactionCategorizer:
    """Categorizes financial transactions using keyword matching."""
    
    def __init__(self):
        self.categories = {
            'Groceries': ['grocery', 'supermarket', 'walmart', 'target', 'kroger', 'safeway', 'whole foods'],
            'Restaurants': ['restaurant', 'mcdonald', 'burger', 'pizza', 'starbucks', 'cafe', 'dine'],
            'Gas': ['gas', 'fuel', 'shell', 'chevron', 'exxon', 'bp', 'mobil'],
            'Shopping': ['amazon', 'ebay', 'mall', 'store', 'shop', 'retail', 'clothes'],
            'Utilities': ['electric', 'water', 'gas bill', 'internet', 'phone', 'cable'],
            'Transportation': ['uber', 'lyft', 'taxi', 'bus', 'metro', 'parking'],
            'Healthcare': ['hospital', 'doctor', 'pharmacy', 'medical', 'dental'],
            'Entertainment': ['movie', 'theater', 'netflix', 'spotify', 'game', 'concert'],
            'Banking': ['fee', 'atm', 'bank', 'interest', 'transfer']
        }
    
    def categorize_transaction(self, description, merchant=None):
        """Categorize a transaction based on description and merchant."""
        text = f"{description} {merchant or ''}".lower()
        
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in text:
                    return category
        
        return 'Other'


class SpendingAnalyzer:
    """Analyzes spending patterns from categorized transactions."""
    
    def __init__(self):
        self.transactions = []
        self.categorizer = TransactionCategorizer()
    
    def parse_csv(self, filepath):
        """Parse CSV file and extract transaction data."""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                # Detect delimiter
                sample = file.read(1024)
                file.seek(0)
                
                delimiter = ','
                if sample.count(';') > sample.count(','):
                    delimiter = ';'
                elif sample.count('\t') > sample.count(','):
                    delimiter = '\t'
                
                reader = csv.DictReader(file, delimiter=delimiter)
                
                # Try to detect column names (case-insensitive)
                headers = [h.lower().strip() for h in reader.fieldnames]
                
                date_col = self._find_column(headers, ['date', 'transaction_date', 'posted_date'])
                desc_col = self._find_column(headers, ['description', 'desc', 'transaction', 'memo'])
                amount_col = self._find_column(headers, ['amount', 'debit', 'credit', 'transaction_amount'])
                merchant_col = self._find_column(headers, ['merchant', 'payee', 'vendor'])
                
                if not all([date_col, desc_col, amount_col]):
                    raise ValueError("Required columns (date, description, amount) not found")
                
                for row in reader:
                    try:
                        # Clean and parse amount
                        amount_str = str(row[amount_col]).strip()
                        amount = self._parse_amount(amount_str)
                        
                        # Skip if amount is 0 or positive (assuming we want expenses)
                        if amount >= 0:
                            continue
                        
                        transaction = {
                            'date': self._parse_date(row[date_col]),
                            'description': row[desc_col].strip(),
                            'amount': abs(amount),  # Make positive for expense analysis
                            'merchant': row.get(merchant_col, '').strip() if merchant_col else '',
                            'category': None
                        }
                        
                        # Categorize transaction
                        transaction['category'] = self.categorizer.categorize_transaction(
                            transaction['description'], 
                            transaction['merchant']
                        )
                        
                        self.transactions.append(transaction)
                        
                    except (ValueError, KeyError) as e:
                        print(f"Warning: Skipping invalid transaction row: {e}", file=sys.stderr)
                        continue
                        
        except FileNotFoundError:
            raise FileNotFoundError(f"Transaction file '{filepath}' not found")
        except Exception as e:
            raise Exception(f"Error parsing CSV file: {e}")
    
    def _find_column(self, headers, possible_names):
        """Find column name from possible alternatives."""
        for header in headers:
            for name in possible_names:
                if name in header:
                    return header
        return None
    
    def _parse_amount(self, amount_str):
        """Parse amount string to float."""
        # Remove currency symbols and whitespace
        cleaned = re.sub(r'[^\d.-]', '', amount_str)
        if not cleaned:
            return 0.0
        return float(cleaned)
    
    def _parse_date(self, date_str):
        """Parse date string to datetime object."""
        date_formats = [
            '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', 
            '%Y-%m-%d %H:%M:%S', '%m/%d/%Y %H:%M:%S'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        # If no format matches, return current date
        print(f"Warning: Could not parse date '{date_str}', using current date", file=sys.stderr)
        return datetime.now()
    
    def analyze_spending_patterns(self):
        """Analyze spending patterns by category."""
        if not self.transactions:
            return {}
        
        category_totals = defaultdict(float)
        category_counts = defaultdict(int)
        monthly_spending = defaultdict(lambda: defaultdict(float))
        
        total_spending = 0
        
        for transaction in self.transactions:
            category = transaction['category']
            amount = transaction['amount']
            month_key = transaction['date'].strftime('%Y-%m')
            
            category_totals[category] += amount
            category_counts[category] += 1
            monthly_spending[month_key][category] += amount
            total_spending += amount
        
        # Calculate percentages and averages
        analysis = {}
        for category in category_totals:
            analysis[category] = {
                'total_amount': category_totals[category],
                'percentage': (category_totals[category] / total_spending) * 100 if total_spending > 0 else 0,
                'transaction_count': category_counts[category],
                'average_transaction': category_totals[category] / category_counts[category]
            }
        
        return {
            'by_category': analysis,
            'total_spending': total_spending,
            'total_transactions': len(self.transactions),
            'monthly_breakdown': dict(monthly_spending)
        }


def create_sample_data():
    """Create a sample transactions.csv file for demonstration."""
    sample_data = [
        ['Date', 'Description', 'Amount', 'Merchant'],
        ['2024-01-15', 'Grocery Shopping', '-125.43', 'Walmart'],
        ['2024-01-16',