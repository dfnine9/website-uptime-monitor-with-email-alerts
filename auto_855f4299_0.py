```python
"""
Bank Transaction Analyzer

This module reads bank CSV files, parses transaction data (date, description, amount),
and implements keyword-based categorization for spending analysis. It categorizes
transactions into groups like groceries, utilities, entertainment, etc., and calculates
total spending by category.

Features:
- Reads CSV files with transaction data
- Parses dates, descriptions, and amounts
- Keyword-based transaction categorization
- Spending calculations by category
- Error handling for malformed data
- Self-contained with minimal dependencies

Usage:
    python script.py
"""

import csv
import re
from datetime import datetime
from collections import defaultdict
import os


class TransactionAnalyzer:
    def __init__(self):
        # Define category keywords (case-insensitive matching)
        self.categories = {
            'groceries': ['grocery', 'supermarket', 'walmart', 'target', 'kroger', 'safeway', 
                         'whole foods', 'trader joe', 'costco', 'food', 'market'],
            'utilities': ['electric', 'gas', 'water', 'internet', 'phone', 'cable', 'utility',
                         'comcast', 'verizon', 'att', 'spectrum', 'pge', 'edison'],
            'entertainment': ['netflix', 'spotify', 'movie', 'theater', 'concert', 'game',
                            'entertainment', 'streaming', 'youtube', 'hulu', 'disney'],
            'restaurants': ['restaurant', 'cafe', 'coffee', 'starbucks', 'mcdonald', 'pizza',
                           'burger', 'taco', 'subway', 'dining', 'bar', 'pub'],
            'transportation': ['gas station', 'shell', 'chevron', 'uber', 'lyft', 'taxi',
                             'parking', 'metro', 'bus', 'train', 'airline'],
            'shopping': ['amazon', 'ebay', 'store', 'mall', 'clothing', 'shoes', 'fashion',
                        'department', 'online', 'purchase'],
            'healthcare': ['doctor', 'hospital', 'pharmacy', 'medical', 'dental', 'clinic',
                          'health', 'cvs', 'walgreens', 'prescription'],
            'bills': ['payment', 'bill', 'invoice', 'loan', 'mortgage', 'rent', 'insurance',
                     'credit card', 'bank fee']
        }
    
    def categorize_transaction(self, description):
        """Categorize a transaction based on its description."""
        description_lower = description.lower()
        
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'other'
    
    def parse_amount(self, amount_str):
        """Parse amount string to float, handling various formats."""
        try:
            # Remove currency symbols, commas, and whitespace
            cleaned = re.sub(r'[$,\s]', '', str(amount_str))
            
            # Handle parentheses for negative amounts
            if '(' in cleaned and ')' in cleaned:
                cleaned = '-' + cleaned.replace('(', '').replace(')', '')
            
            return float(cleaned)
        except (ValueError, AttributeError):
            return 0.0
    
    def parse_date(self, date_str):
        """Parse date string to datetime object."""
        date_formats = [
            '%m/%d/%Y', '%m-%d-%Y', '%Y-%m-%d', '%d/%m/%Y',
            '%m/%d/%y', '%m-%d-%y', '%y-%m-%d', '%d/%m/%y'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(str(date_str).strip(), fmt)
            except ValueError:
                continue
        
        return None
    
    def read_csv_file(self, filename):
        """Read and parse CSV file containing transaction data."""
        transactions = []
        
        try:
            with open(filename, 'r', newline='', encoding='utf-8') as file:
                # Try to detect if first row is header
                sample = file.read(1024)
                file.seek(0)
                
                sniffer = csv.Sniffer()
                has_header = sniffer.has_header(sample)
                
                reader = csv.reader(file)
                
                if has_header:
                    headers = next(reader)
                    print(f"Detected headers: {headers}")
                
                for row_num, row in enumerate(reader, start=2 if has_header else 1):
                    if len(row) < 3:
                        print(f"Warning: Row {row_num} has insufficient columns: {row}")
                        continue
                    
                    try:
                        # Assume format: date, description, amount (adjust indices as needed)
                        date_str = row[0]
                        description = row[1] if len(row) > 1 else "Unknown"
                        amount_str = row[2] if len(row) > 2 else "0"
                        
                        parsed_date = self.parse_date(date_str)
                        amount = self.parse_amount(amount_str)
                        category = self.categorize_transaction(description)
                        
                        transaction = {
                            'date': parsed_date,
                            'description': description.strip(),
                            'amount': amount,
                            'category': category,
                            'raw_row': row
                        }
                        
                        transactions.append(transaction)
                        
                    except Exception as e:
                        print(f"Error processing row {row_num}: {row} - {e}")
                        continue
                        
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
            return []
        except Exception as e:
            print(f"Error reading file '{filename}': {e}")
            return []
        
        return transactions
    
    def analyze_spending(self, transactions):
        """Analyze spending by category."""
        category_totals = defaultdict(float)
        monthly_totals = defaultdict(lambda: defaultdict(float))
        
        for transaction in transactions:
            if transaction['date'] and transaction['amount'] < 0:  # Only count expenses (negative amounts)
                amount = abs(transaction['amount'])
                category = transaction['category']
                
                category_totals[category] += amount
                
                # Group by month-year
                month_key = transaction['date'].strftime('%Y-%m')
                monthly_totals[month_key][category] += amount
        
        return dict(category_totals), dict(monthly_totals)
    
    def print_analysis(self, transactions, category_totals, monthly_totals):
        """Print spending analysis results."""
        print("\n" + "="*60)
        print("BANK TRANSACTION ANALYSIS REPORT")
        print("="*60)
        
        print(f"\nTotal transactions processed: {len(transactions)}")
        
        if not transactions:
            print("No valid transactions found.")
            return
        
        # Date range
        dates = [t['date'] for t in transactions if t['date']]
        if dates:
            print(f"Date range: {min(dates).strftime('%Y-%m-%d')} to {max(dates).strftime('%Y-%m-%d')}")
        
        # Category spending
        print(f"\n{'SPENDING BY CATEGORY':<25} {'AMOUNT':>15}")
        print("-" * 42)
        
        total_spending = 0
        for category, amount in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
            print(f"{category.title():<25} ${amount:>12,.2f}")
            total_spending += amount
        
        print("-" * 42)
        print(f"{'TOTAL SPENDING':<25} ${total_spending:>12,.2f}")
        
        # Monthly breakdown (show last 6 months if available)
        if monthly_totals:
            print(f"\n{'MONTHLY BREAKDOWN (