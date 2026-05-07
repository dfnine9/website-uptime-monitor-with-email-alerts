```python
#!/usr/bin/env python3
"""
Bank Statement Transaction Categorizer

This module parses CSV bank statements and categorizes transactions based on
common description patterns. It creates a dictionary-based system that maps
transaction descriptions to expense categories like groceries, gas, utilities, etc.

The script reads CSV files with columns: date, description, amount, and optionally balance.
It uses pattern matching to automatically categorize transactions and generates
summary reports showing spending by category.

Usage: python script.py [csv_file_path]
If no file is provided, it will use sample data for demonstration.
"""

import csv
import re
import sys
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Tuple, Optional


class TransactionCategorizer:
    """Categorizes bank transactions based on description patterns."""
    
    def __init__(self):
        # Category mapping with regex patterns
        self.category_patterns = {
            'groceries': [
                r'(?i)\b(walmart|target|safeway|kroger|publix|whole foods|trader joe|costco|sam\'s club)\b',
                r'(?i)\b(grocery|supermarket|market|food)\b',
                r'(?i)\b(aldi|wegmans|harris teeter|giant eagle)\b'
            ],
            'gas': [
                r'(?i)\b(shell|exxon|bp|chevron|mobil|speedway|wawa|sheetz)\b',
                r'(?i)\b(gas|fuel|gasoline|station)\b'
            ],
            'restaurants': [
                r'(?i)\b(mcdonald|burger king|subway|starbucks|dunkin|kfc|taco bell)\b',
                r'(?i)\b(restaurant|cafe|pizza|diner|grill|bar)\b',
                r'(?i)\b(doordash|uber eats|grubhub|postmates)\b'
            ],
            'utilities': [
                r'(?i)\b(electric|electricity|power|pge|duke energy)\b',
                r'(?i)\b(water|sewer|waste|trash|garbage)\b',
                r'(?i)\b(gas company|natural gas)\b',
                r'(?i)\b(utility|utilities)\b'
            ],
            'transportation': [
                r'(?i)\b(uber|lyft|taxi|metro|bus|train|transit)\b',
                r'(?i)\b(parking|toll|bridge)\b'
            ],
            'entertainment': [
                r'(?i)\b(netflix|spotify|hulu|disney|amazon prime|apple music)\b',
                r'(?i)\b(movie|cinema|theater|theatre|concert)\b',
                r'(?i)\b(game|gaming|xbox|playstation|steam)\b'
            ],
            'shopping': [
                r'(?i)\b(amazon|ebay|etsy|best buy|home depot|lowes)\b',
                r'(?i)\b(clothing|apparel|mall|outlet)\b'
            ],
            'healthcare': [
                r'(?i)\b(pharmacy|cvs|walgreens|rite aid|medical|doctor|hospital)\b',
                r'(?i)\b(dentist|dental|vision|health)\b'
            ],
            'banking': [
                r'(?i)\b(atm|fee|charge|interest|overdraft)\b',
                r'(?i)\b(transfer|deposit|withdrawal)\b'
            ],
            'income': [
                r'(?i)\b(salary|payroll|direct deposit|dd|income)\b',
                r'(?i)\b(refund|return|credit)\b'
            ]
        }
        
        self.transactions = []
        self.categorized_transactions = defaultdict(list)
        self.category_totals = defaultdict(Decimal)
    
    def parse_amount(self, amount_str: str) -> Decimal:
        """Parse amount string to Decimal, handling various formats."""
        try:
            # Remove currency symbols, commas, and whitespace
            cleaned = re.sub(r'[$,\s]', '', str(amount_str))
            # Handle parentheses as negative
            if cleaned.startswith('(') and cleaned.endswith(')'):
                cleaned = '-' + cleaned[1:-1]
            return Decimal(cleaned)
        except (InvalidOperation, ValueError):
            return Decimal('0.00')
    
    def categorize_description(self, description: str) -> str:
        """Categorize a transaction description using pattern matching."""
        description_clean = description.strip()
        
        for category, patterns in self.category_patterns.items():
            for pattern in patterns:
                if re.search(pattern, description_clean):
                    return category
        
        return 'other'
    
    def load_csv(self, filepath: str) -> bool:
        """Load transactions from CSV file."""
        try:
            with open(filepath, 'r', newline='', encoding='utf-8') as csvfile:
                # Try to detect delimiter
                sample = csvfile.read(1024)
                csvfile.seek(0)
                
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                
                # Normalize column names (case insensitive)
                fieldnames = [name.lower().strip() for name in reader.fieldnames or []]
                
                for row in reader:
                    # Create normalized row dict
                    norm_row = {k.lower().strip(): v for k, v in row.items()}
                    
                    # Extract required fields with flexible column naming
                    date = self._extract_field(norm_row, ['date', 'transaction date', 'trans date'])
                    description = self._extract_field(norm_row, ['description', 'desc', 'memo', 'transaction'])
                    amount = self._extract_field(norm_row, ['amount', 'debit', 'credit', 'transaction amount'])
                    
                    if date and description and amount:
                        parsed_amount = self.parse_amount(amount)
                        category = self.categorize_description(description)
                        
                        transaction = {
                            'date': date.strip(),
                            'description': description.strip(),
                            'amount': parsed_amount,
                            'category': category
                        }
                        
                        self.transactions.append(transaction)
                        self.categorized_transactions[category].append(transaction)
                        self.category_totals[category] += parsed_amount
                
                return len(self.transactions) > 0
                
        except FileNotFoundError:
            print(f"Error: File '{filepath}' not found.")
            return False
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return False
    
    def _extract_field(self, row_dict: Dict[str, str], possible_names: List[str]) -> Optional[str]:
        """Extract field value from row using possible column names."""
        for name in possible_names:
            if name in row_dict and row_dict[name]:
                return row_dict[name]
        return None
    
    def create_sample_data(self) -> None:
        """Create sample transaction data for demonstration."""
        sample_transactions = [
            ('2024-01-15', 'WALMART SUPERCENTER', '-85.43'),
            ('2024-01-16', 'SHELL FUEL STATION', '-45.20'),
            ('2024-01-17', 'STARBUCKS COFFEE', '-5.75'),
            ('2024-01-18', 'ELECTRIC COMPANY PAYMENT', '-120.00'),
            ('2024-01-19', 'AMAZON PURCHASE', '-67.89'),
            ('2024-01-20', 'SALARY DIRECT DEPOSIT', '2500.00'),
            ('2024-01-21', 'CVS PHARMACY', '-23.45'),
            ('2024-01-22', 'UBER RIDE', '-18.50'),
            ('2024-01-23', 'NETFLIX SUBSCRIPTION', '-15.99'),
            ('2024-01-24', 'TARGET STORE', '-94.32'),