```python
"""
Bank Statement Transaction Categorizer

This module reads CSV bank statements and categorizes transactions based on merchant names
using regex pattern matching. It supports common CSV formats and includes data validation.

Features:
- Reads CSV files with flexible column detection
- Categorizes transactions using regex patterns for merchant names
- Validates data formats (dates, amounts)
- Handles various CSV structures commonly used by banks
- Provides summary statistics and categorized transaction reports

Usage: python script.py
"""

import csv
import re
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import sys

class TransactionCategorizer:
    def __init__(self):
        self.categories = {
            'groceries': [
                r'walmart|kroger|safeway|whole foods|trader joe|target|costco|sam\'s club',
                r'grocery|supermarket|market|food'
            ],
            'restaurants': [
                r'mcdonald|burger king|kfc|taco bell|subway|pizza|restaurant',
                r'cafe|coffee|starbucks|dunkin|chipotle|domino'
            ],
            'gas': [
                r'shell|bp|exxon|chevron|mobil|texaco|gulf|citgo',
                r'gas station|fuel|petroleum'
            ],
            'retail': [
                r'amazon|ebay|walmart\.com|target\.com|best buy|home depot',
                r'store|shop|retail|mall'
            ],
            'utilities': [
                r'electric|power|gas company|water|sewer|trash|internet|cable',
                r'utility|bill|service'
            ],
            'banking': [
                r'bank|atm|fee|interest|transfer|deposit|withdrawal',
                r'credit card|loan|mortgage'
            ],
            'entertainment': [
                r'netflix|spotify|hulu|disney|movie|theater|cinema',
                r'entertainment|music|streaming'
            ],
            'medical': [
                r'hospital|clinic|doctor|pharmacy|cvs|walgreens|medical',
                r'health|dental|vision|prescription'
            ],
            'transportation': [
                r'uber|lyft|taxi|metro|transit|parking|toll',
                r'transportation|bus|train|airline'
            ]
        }
        
    def categorize_transaction(self, description: str) -> str:
        """Categorize a transaction based on its description using regex patterns."""
        if not description:
            return 'uncategorized'
            
        description_lower = description.lower().strip()
        
        for category, patterns in self.categories.items():
            for pattern in patterns:
                if re.search(pattern, description_lower):
                    return category
                    
        return 'uncategorized'
    
    def validate_amount(self, amount_str: str) -> Optional[float]:
        """Validate and parse amount string to float."""
        try:
            # Remove common currency symbols and whitespace
            cleaned = re.sub(r'[$,\s]', '', amount_str.strip())
            # Handle parentheses for negative amounts
            if cleaned.startswith('(') and cleaned.endswith(')'):
                cleaned = '-' + cleaned[1:-1]
            return float(cleaned)
        except (ValueError, AttributeError):
            return None
    
    def validate_date(self, date_str: str) -> Optional[str]:
        """Validate date string and return standardized format."""
        if not date_str:
            return None
            
        date_formats = [
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%m/%d/%y',
            '%m-%d-%Y',
            '%m-%d-%y',
            '%d/%m/%Y',
            '%d-%m-%Y'
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str.strip(), fmt)
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue
                
        return None
    
    def detect_csv_structure(self, filepath: str) -> Dict:
        """Detect CSV structure and column mappings."""
        try:
            with open(filepath, 'r', newline='', encoding='utf-8') as file:
                # Try to detect dialect
                sample = file.read(1024)
                file.seek(0)
                
                try:
                    dialect = csv.Sniffer().sniff(sample)
                except csv.Error:
                    dialect = csv.excel
                
                reader = csv.reader(file, dialect)
                header = next(reader)
                
                # Common column name patterns
                column_mappings = {
                    'date': ['date', 'transaction date', 'trans date', 'posted date'],
                    'description': ['description', 'merchant', 'payee', 'transaction', 'detail'],
                    'amount': ['amount', 'debit', 'credit', 'transaction amount', 'value'],
                    'balance': ['balance', 'running balance', 'account balance']
                }
                
                detected_columns = {}
                header_lower = [col.lower().strip() for col in header]
                
                for field, patterns in column_mappings.items():
                    for i, col in enumerate(header_lower):
                        if any(pattern in col for pattern in patterns):
                            detected_columns[field] = i
                            break
                
                return {
                    'dialect': dialect,
                    'header': header,
                    'columns': detected_columns
                }
                
        except Exception as e:
            print(f"Error detecting CSV structure: {e}")
            return {}
    
    def process_csv(self, filepath: str) -> List[Dict]:
        """Process CSV file and return categorized transactions."""
        structure = self.detect_csv_structure(filepath)
        if not structure:
            return []
        
        transactions = []
        
        try:
            with open(filepath, 'r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file, structure['dialect'])
                next(reader)  # Skip header
                
                for row_num, row in enumerate(reader, start=2):
                    if len(row) < max(structure['columns'].values(), default=0) + 1:
                        print(f"Warning: Row {row_num} has insufficient columns")
                        continue
                    
                    transaction = {}
                    
                    # Extract date
                    if 'date' in structure['columns']:
                        date_str = row[structure['columns']['date']]
                        validated_date = self.validate_date(date_str)
                        if validated_date:
                            transaction['date'] = validated_date
                        else:
                            print(f"Warning: Invalid date format in row {row_num}: {date_str}")
                            continue
                    
                    # Extract description
                    if 'description' in structure['columns']:
                        transaction['description'] = row[structure['columns']['description']].strip()
                    else:
                        transaction['description'] = ''
                    
                    # Extract amount
                    if 'amount' in structure['columns']:
                        amount_str = row[structure['columns']['amount']]
                        validated_amount = self.validate_amount(amount_str)
                        if validated_amount is not None:
                            transaction['amount'] = validated_amount
                        else:
                            print(f"Warning: Invalid amount format in row {row_num}: {amount_str}")
                            continue
                    
                    # Extract balance if available
                    if 'balance' in structure['columns']:
                        balance_str = row[structure['columns']['balance']]
                        validated_balance = self.validate_amount(balance_str)
                        if validated_balance is not None:
                            transaction['balance'] = validated_balance
                    
                    # Categorize transaction
                    transaction['category'] = self.categorize_transaction(transaction['description'])
                    
                    transactions.append(transaction)
                    
        except Exception as e:
            print(f"Error processing CSV file: {e}")
            return []
        
        return transactions
    
    def generate_report(self, transactions: List[Dict]) -> None:
        """