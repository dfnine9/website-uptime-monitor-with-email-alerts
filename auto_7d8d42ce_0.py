```python
#!/usr/bin/env python3
"""
Bank Statement Transaction Categorizer

This script parses CSV bank statements and automatically categorizes transactions
based on description keywords. It generates spending summaries by category to help
users understand their spending patterns.

Features:
- Parses CSV files with transaction data
- Categorizes transactions using keyword matching
- Generates spending summaries by category
- Handles various CSV formats and encoding issues
- Provides detailed error reporting

Usage: python script.py
"""

import csv
import sys
import os
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import re


class TransactionCategorizer:
    """Categorizes bank transactions based on description keywords."""
    
    def __init__(self):
        """Initialize the categorizer with predefined categories and keywords."""
        self.categories = {
            'Food & Dining': [
                'restaurant', 'cafe', 'coffee', 'pizza', 'burger', 'mcdonald',
                'subway', 'starbucks', 'domino', 'kfc', 'taco', 'food', 'dining',
                'grubhub', 'doordash', 'ubereats', 'postmates'
            ],
            'Groceries': [
                'walmart', 'target', 'kroger', 'safeway', 'grocery', 'market',
                'supermarket', 'costco', 'sams club', 'whole foods', 'trader joe'
            ],
            'Transportation': [
                'gas', 'fuel', 'uber', 'lyft', 'taxi', 'metro', 'bus', 'train',
                'parking', 'toll', 'shell', 'exxon', 'chevron', 'bp'
            ],
            'Entertainment': [
                'netflix', 'spotify', 'amazon prime', 'disney', 'hulu', 'movie',
                'theater', 'cinema', 'concert', 'ticket', 'game', 'steam'
            ],
            'Shopping': [
                'amazon', 'ebay', 'mall', 'store', 'shop', 'retail', 'purchase',
                'order', 'delivery'
            ],
            'Utilities': [
                'electric', 'electricity', 'gas bill', 'water', 'internet',
                'cable', 'phone', 'mobile', 'utility', 'power', 'comcast',
                'verizon', 'att'
            ],
            'Healthcare': [
                'pharmacy', 'doctor', 'medical', 'hospital', 'clinic', 'cvs',
                'walgreens', 'health', 'dental', 'vision'
            ],
            'Finance': [
                'bank', 'atm', 'fee', 'interest', 'loan', 'credit', 'payment',
                'transfer', 'deposit', 'withdrawal'
            ]
        }
    
    def categorize_transaction(self, description: str) -> str:
        """
        Categorize a transaction based on its description.
        
        Args:
            description: The transaction description
            
        Returns:
            The category name or 'Other' if no match found
        """
        description_lower = description.lower()
        
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'Other'


class CSVParser:
    """Handles parsing of CSV bank statement files."""
    
    def __init__(self):
        """Initialize the CSV parser."""
        self.common_headers = {
            'date': ['date', 'transaction date', 'posted date', 'trans date'],
            'description': ['description', 'memo', 'transaction', 'details', 'payee'],
            'amount': ['amount', 'debit', 'credit', 'transaction amount', 'value']
        }
    
    def detect_delimiter(self, file_path: str) -> str:
        """
        Detect the CSV delimiter used in the file.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            The detected delimiter character
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                sample = file.read(1024)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                return delimiter
        except Exception:
            return ','
    
    def find_column_indices(self, headers: List[str]) -> Dict[str, Optional[int]]:
        """
        Find the indices of required columns in the CSV headers.
        
        Args:
            headers: List of column headers from CSV
            
        Returns:
            Dictionary mapping column types to their indices
        """
        headers_lower = [h.lower().strip() for h in headers]
        indices = {}
        
        for col_type, possible_names in self.common_headers.items():
            indices[col_type] = None
            for i, header in enumerate(headers_lower):
                for name in possible_names:
                    if name in header:
                        indices[col_type] = i
                        break
                if indices[col_type] is not None:
                    break
        
        return indices
    
    def parse_amount(self, amount_str: str) -> float:
        """
        Parse amount string to float, handling various formats.
        
        Args:
            amount_str: String representation of amount
            
        Returns:
            Float value of the amount
        """
        if not amount_str:
            return 0.0
        
        # Remove currency symbols and whitespace
        cleaned = re.sub(r'[$€£¥,\s]', '', str(amount_str))
        
        # Handle parentheses for negative amounts
        if '(' in cleaned and ')' in cleaned:
            cleaned = '-' + cleaned.replace('(', '').replace(')', '')
        
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
    
    def parse_csv(self, file_path: str) -> List[Dict[str, str]]:
        """
        Parse CSV file and extract transaction data.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            List of transaction dictionaries
        """
        transactions = []
        delimiter = self.detect_delimiter(file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=delimiter)
                headers = next(reader)
                
                indices = self.find_column_indices(headers)
                
                if not all(idx is not None for idx in indices.values()):
                    raise ValueError(f"Could not find required columns. Found: {indices}")
                
                for row_num, row in enumerate(reader, start=2):
                    if len(row) <= max(indices.values()):
                        continue
                    
                    try:
                        transaction = {
                            'date': row[indices['date']].strip(),
                            'description': row[indices['description']].strip(),
                            'amount': self.parse_amount(row[indices['amount']])
                        }
                        transactions.append(transaction)
                    except (IndexError, ValueError) as e:
                        print(f"Warning: Error parsing row {row_num}: {e}", file=sys.stderr)
                        continue
        
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin1') as file:
                reader = csv.reader(file, delimiter=delimiter)
                headers = next(reader)
                indices = self.find_column_indices(headers)
                
                for row in reader:
                    if len(row) <= max(indices.values()):
                        continue
                    
                    transaction = {
                        'date': row[indices['date']].strip(),
                        'description': row[indices['description']].strip(),
                        'amount': self.parse_amount(row[indices['amount']])
                    }
                    transactions.append(transaction)
        
        return transactions


def generate_sample_csv():
    """Generate a sample