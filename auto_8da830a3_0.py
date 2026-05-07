```python
"""
CSV Transaction Parser and Spending Pattern Analyzer

This module parses CSV files containing financial transaction data and categorizes
transactions based on description keywords. It calculates spending patterns by
category including total amounts, transaction counts, and percentages.

Expected CSV format:
- Headers: date, description, amount (or similar variations)
- Date format: YYYY-MM-DD, MM/DD/YYYY, or DD/MM/YYYY
- Amount: positive for income, negative for expenses

Usage: python script.py [csv_file_path]
If no file provided, uses sample data for demonstration.
"""

import csv
import re
import sys
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Any


class TransactionCategorizer:
    """Categorizes financial transactions based on description patterns."""
    
    def __init__(self):
        self.categories = {
            'Food & Dining': [
                'restaurant', 'cafe', 'coffee', 'pizza', 'mcdonalds', 'burger',
                'starbucks', 'food', 'dining', 'lunch', 'dinner', 'breakfast',
                'grocery', 'supermarket', 'walmart', 'target', 'safeway'
            ],
            'Transportation': [
                'gas', 'fuel', 'uber', 'lyft', 'taxi', 'metro', 'bus', 'train',
                'parking', 'toll', 'car', 'automotive', 'shell', 'chevron'
            ],
            'Shopping': [
                'amazon', 'ebay', 'store', 'retail', 'mall', 'shop', 'purchase',
                'clothing', 'electronics', 'pharmacy', 'cvs', 'walgreens'
            ],
            'Entertainment': [
                'movie', 'theater', 'netflix', 'spotify', 'game', 'entertainment',
                'concert', 'show', 'club', 'bar', 'casino', 'sports'
            ],
            'Utilities': [
                'electric', 'gas company', 'water', 'internet', 'phone', 'cable',
                'utility', 'power', 'energy', 'verizon', 'att', 'comcast'
            ],
            'Healthcare': [
                'hospital', 'doctor', 'medical', 'pharmacy', 'health', 'dental',
                'insurance', 'clinic', 'medicine', 'prescription'
            ],
            'Income': [
                'salary', 'payroll', 'deposit', 'income', 'paycheck', 'wage',
                'bonus', 'refund', 'transfer in', 'interest'
            ],
            'Other': []  # Default category
        }
    
    def categorize(self, description: str) -> str:
        """Categorize a transaction based on its description."""
        description_lower = description.lower()
        
        for category, keywords in self.categories.items():
            if category == 'Other':
                continue
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'Other'


class CSVTransactionParser:
    """Parses CSV transaction files and analyzes spending patterns."""
    
    def __init__(self):
        self.categorizer = TransactionCategorizer()
        self.transactions = []
    
    def parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float, handling various formats."""
        try:
            # Remove currency symbols and whitespace
            cleaned = re.sub(r'[$,\s]', '', amount_str.strip())
            # Handle parentheses for negative amounts
            if cleaned.startswith('(') and cleaned.endswith(')'):
                cleaned = '-' + cleaned[1:-1]
            return float(cleaned)
        except (ValueError, AttributeError):
            return 0.0
    
    def parse_date(self, date_str: str) -> str:
        """Parse date string to standardized format."""
        date_formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%m/%d/%y', '%d/%m/%y']
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str.strip(), fmt)
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        return date_str  # Return original if parsing fails
    
    def detect_headers(self, headers: List[str]) -> Dict[str, int]:
        """Detect column indices for date, description, and amount."""
        header_map = {}
        headers_lower = [h.lower().strip() for h in headers]
        
        # Date column detection
        for i, header in enumerate(headers_lower):
            if any(word in header for word in ['date', 'time', 'timestamp']):
                header_map['date'] = i
                break
        
        # Description column detection
        for i, header in enumerate(headers_lower):
            if any(word in header for word in ['description', 'desc', 'memo', 'detail', 'payee']):
                header_map['description'] = i
                break
        
        # Amount column detection
        for i, header in enumerate(headers_lower):
            if any(word in header for word in ['amount', 'value', 'total', 'sum', 'debit', 'credit']):
                header_map['amount'] = i
                break
        
        return header_map
    
    def parse_csv(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse CSV file and return list of transaction dictionaries."""
        transactions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # Detect delimiter
                sample = file.read(1024)
                file.seek(0)
                delimiter = ',' if sample.count(',') > sample.count(';') else ';'
                
                reader = csv.reader(file, delimiter=delimiter)
                headers = next(reader)
                header_map = self.detect_headers(headers)
                
                if len(header_map) < 3:
                    raise ValueError("Could not detect required columns (date, description, amount)")
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        if len(row) <= max(header_map.values()):
                            continue
                        
                        transaction = {
                            'date': self.parse_date(row[header_map['date']]),
                            'description': row[header_map['description']].strip(),
                            'amount': self.parse_amount(row[header_map['amount']]),
                            'category': ''
                        }
                        
                        # Skip if amount is 0 or description is empty
                        if transaction['amount'] == 0 or not transaction['description']:
                            continue
                        
                        transaction['category'] = self.categorizer.categorize(transaction['description'])
                        transactions.append(transaction)
                        
                    except (IndexError, ValueError) as e:
                        print(f"Warning: Skipping row {row_num} due to parsing error: {e}")
                        continue
        
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file not found: {file_path}")
        except Exception as e:
            raise Exception(f"Error parsing CSV file: {e}")
        
        return transactions
    
    def calculate_spending_patterns(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate spending patterns by category."""
        patterns = defaultdict(lambda: {'total': 0.0, 'count': 0, 'transactions': []})
        total_amount = 0.0
        
        for transaction in transactions:
            category = transaction['category']
            amount = transaction['amount']
            
            patterns[category]['total'] += amount
            patterns[category]['count'] += 1
            patterns[category]['transactions'].append(transaction)
            total_amount += abs(amount)
        
        # Calculate percentages
        for category_data in patterns.values():
            if total_amount > 0:
                category_data['percentage