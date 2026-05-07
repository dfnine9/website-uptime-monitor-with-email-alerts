```python
"""
CSV Transaction Categorizer

This module reads CSV transaction files and automatically categorizes expenses using
regex pattern matching. It supports common expense categories including food, transport,
utilities, entertainment, and others.

The script processes transaction data from CSV files, applies intelligent pattern matching
to transaction descriptions, and outputs categorized results with summary statistics.

Usage: python script.py
"""

import csv
import re
import sys
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import os

class TransactionCategorizer:
    """Handles categorization of financial transactions using regex patterns."""
    
    def __init__(self):
        """Initialize categorizer with predefined category patterns."""
        self.category_patterns = {
            'food': [
                r'\b(restaurant|cafe|coffee|pizza|burger|mcdonald|kfc|subway|starbucks)\b',
                r'\b(grocery|supermarket|walmart|target|costco|food|dining)\b',
                r'\b(breakfast|lunch|dinner|meal|eat|restaurant)\b',
                r'\b(bakery|deli|butcher|market)\b'
            ],
            'transport': [
                r'\b(gas|fuel|shell|exxon|bp|chevron|mobil)\b',
                r'\b(uber|lyft|taxi|cab|bus|train|metro|subway)\b',
                r'\b(parking|toll|bridge|highway)\b',
                r'\b(airline|flight|airport|car rental|hertz|avis)\b'
            ],
            'utilities': [
                r'\b(electric|electricity|gas company|water|sewer|trash)\b',
                r'\b(internet|cable|phone|cell|mobile|verizon|att|comcast)\b',
                r'\b(utility|utilities|power|energy)\b'
            ],
            'entertainment': [
                r'\b(movie|cinema|theater|netflix|spotify|hulu|amazon prime)\b',
                r'\b(concert|show|event|ticket|entertainment)\b',
                r'\b(game|gaming|steam|playstation|xbox)\b',
                r'\b(bar|pub|nightclub|drinks)\b'
            ],
            'shopping': [
                r'\b(amazon|ebay|store|shop|mall|retail)\b',
                r'\b(clothing|clothes|apparel|fashion)\b',
                r'\b(electronics|best buy|apple store)\b'
            ],
            'healthcare': [
                r'\b(doctor|hospital|pharmacy|medical|health|dentist)\b',
                r'\b(insurance|copay|prescription|medicine)\b'
            ],
            'banking': [
                r'\b(bank|atm|fee|interest|transfer|deposit)\b',
                r'\b(credit card|payment|finance charge)\b'
            ]
        }
    
    def categorize_transaction(self, description: str, amount: float) -> str:
        """
        Categorize a transaction based on its description.
        
        Args:
            description: Transaction description text
            amount: Transaction amount (positive for income, negative for expense)
            
        Returns:
            Category name as string
        """
        if not description:
            return 'uncategorized'
            
        description_lower = description.lower()
        
        # Check for income patterns first
        if amount > 0:
            income_patterns = [
                r'\b(salary|wage|payroll|income|deposit|refund)\b',
                r'\b(bonus|commission|dividend|interest)\b'
            ]
            for pattern in income_patterns:
                if re.search(pattern, description_lower):
                    return 'income'
        
        # Check expense categories
        for category, patterns in self.category_patterns.items():
            for pattern in patterns:
                if re.search(pattern, description_lower, re.IGNORECASE):
                    return category
        
        return 'uncategorized'

class CSVTransactionProcessor:
    """Processes CSV transaction files and generates categorized reports."""
    
    def __init__(self):
        """Initialize processor with categorizer."""
        self.categorizer = TransactionCategorizer()
        self.transactions = []
    
    def parse_csv_file(self, filepath: str) -> List[Dict]:
        """
        Parse CSV file and extract transaction data.
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            List of transaction dictionaries
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If CSV format is invalid
        """
        transactions = []
        
        try:
            with open(filepath, 'r', newline='', encoding='utf-8') as csvfile:
                # Try to detect delimiter
                sample = csvfile.read(1024)
                csvfile.seek(0)
                
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                
                for row_num, row in enumerate(reader, 1):
                    try:
                        transaction = self._parse_transaction_row(row)
                        if transaction:
                            transactions.append(transaction)
                    except Exception as e:
                        print(f"Warning: Skipping row {row_num} due to error: {e}")
                        continue
                        
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file not found: {filepath}")
        except Exception as e:
            raise ValueError(f"Error reading CSV file: {e}")
            
        return transactions
    
    def _parse_transaction_row(self, row: Dict) -> Optional[Dict]:
        """
        Parse individual transaction row from CSV.
        
        Args:
            row: Dictionary representing CSV row
            
        Returns:
            Parsed transaction dictionary or None if invalid
        """
        # Common CSV column name variations
        description_fields = ['description', 'desc', 'memo', 'details', 'transaction_description']
        amount_fields = ['amount', 'value', 'transaction_amount', 'debit', 'credit']
        date_fields = ['date', 'transaction_date', 'posting_date']
        
        # Extract description
        description = None
        for field in description_fields:
            if field in row and row[field]:
                description = row[field].strip()
                break
        
        # Extract amount
        amount = None
        for field in amount_fields:
            if field in row and row[field]:
                try:
                    amount_str = str(row[field]).replace('$', '').replace(',', '').strip()
                    amount = float(amount_str)
                    break
                except ValueError:
                    continue
        
        # Extract date
        date = None
        for field in date_fields:
            if field in row and row[field]:
                date = row[field].strip()
                break
        
        if description is None or amount is None:
            return None
            
        return {
            'description': description,
            'amount': amount,
            'date': date or 'Unknown',
            'raw_row': row
        }
    
    def process_transactions(self, transactions: List[Dict]) -> Dict:
        """
        Process and categorize all transactions.
        
        Args:
            transactions: List of transaction dictionaries
            
        Returns:
            Dictionary with categorized results and statistics
        """
        categorized_transactions = []
        category_totals = defaultdict(float)
        category_counts = defaultdict(int)
        
        for transaction in transactions:
            category = self.categorizer.categorize_transaction(
                transaction['description'], 
                transaction['amount']
            )
            
            categorized_transaction = {
                **transaction,
                'category': category
            }
            categorized_transactions.append(categorized_transaction)
            
            category_totals[category] += abs(transaction['amount'])
            category_counts[category] += 1
        
        return {
            'transactions': categorized_transactions,
            'category_totals': dict(category_totals),
            'category_counts': dict(category_counts),
            'total_transactions': len(categorized_transactions),
            'total_amount': sum(abs(t['amount']) for t in categorized_transactions)
        }