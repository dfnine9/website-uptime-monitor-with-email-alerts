```python
"""
Bank Statement Parser and Expense Categorizer

This module provides functionality to parse CSV bank statements with configurable
column mapping, validate data integrity, and automatically categorize expenses
using regex-based pattern matching for common merchant types and transaction
descriptions.

Features:
- Configurable CSV column mapping
- Data validation and integrity checks
- Automatic expense categorization using regex patterns
- Support for common merchant types (groceries, restaurants, gas stations, etc.)
- Error handling and reporting
- Self-contained implementation using only standard library

Usage:
    python script.py

The script will process a sample bank statement and demonstrate the categorization
functionality.
"""

import csv
import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from io import StringIO


class BankStatementParser:
    """Parses and categorizes bank statement transactions."""
    
    def __init__(self):
        self.column_mapping = {
            'date': 'Date',
            'description': 'Description', 
            'amount': 'Amount',
            'balance': 'Balance'
        }
        
        # Predefined categorization patterns
        self.category_patterns = {
            'Groceries': [
                r'.*WALMART.*',
                r'.*KROGER.*',
                r'.*SAFEWAY.*',
                r'.*WHOLE FOODS.*',
                r'.*TRADER JOE.*',
                r'.*COSTCO.*',
                r'.*TARGET.*GROCERY.*'
            ],
            'Restaurants': [
                r'.*MCDONALD.*',
                r'.*STARBUCKS.*',
                r'.*SUBWAY.*',
                r'.*PIZZA.*',
                r'.*RESTAURANT.*',
                r'.*CAFE.*',
                r'.*BISTRO.*',
                r'.*DINER.*'
            ],
            'Gas/Fuel': [
                r'.*SHELL.*',
                r'.*EXXON.*',
                r'.*BP.*',
                r'.*CHEVRON.*',
                r'.*MOBIL.*',
                r'.*GAS STATION.*',
                r'.*FUEL.*'
            ],
            'Shopping': [
                r'.*AMAZON.*',
                r'.*EBAY.*',
                r'.*TARGET.*',
                r'.*BEST BUY.*',
                r'.*MACY.*',
                r'.*NORDSTROM.*'
            ],
            'Banking/Finance': [
                r'.*ATM.*',
                r'.*BANK.*FEE.*',
                r'.*INTEREST.*',
                r'.*TRANSFER.*',
                r'.*DEPOSIT.*',
                r'.*WITHDRAWAL.*'
            ],
            'Utilities': [
                r'.*ELECTRIC.*',
                r'.*WATER.*SEWER.*',
                r'.*GAS.*COMPANY.*',
                r'.*PHONE.*BILL.*',
                r'.*INTERNET.*'
            ],
            'Healthcare': [
                r'.*PHARMACY.*',
                r'.*MEDICAL.*',
                r'.*DOCTOR.*',
                r'.*HOSPITAL.*',
                r'.*CLINIC.*',
                r'.*CVS.*',
                r'.*WALGREENS.*'
            ],
            'Transportation': [
                r'.*UBER.*',
                r'.*LYFT.*',
                r'.*TAXI.*',
                r'.*BUS.*FARE.*',
                r'.*METRO.*',
                r'.*PARKING.*'
            ]
        }
    
    def configure_columns(self, mapping: Dict[str, str]) -> None:
        """Configure column mapping for CSV parsing."""
        self.column_mapping.update(mapping)
    
    def validate_row_data(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Validate and convert row data types."""
        validated_row = {}
        errors = []
        
        try:
            # Validate date
            date_str = row.get(self.column_mapping['date'], '').strip()
            if date_str:
                try:
                    validated_row['date'] = datetime.strptime(date_str, '%Y-%m-%d').date()
                except ValueError:
                    try:
                        validated_row['date'] = datetime.strptime(date_str, '%m/%d/%Y').date()
                    except ValueError:
                        errors.append(f"Invalid date format: {date_str}")
                        validated_row['date'] = None
            else:
                errors.append("Missing date")
                validated_row['date'] = None
            
            # Validate description
            description = row.get(self.column_mapping['description'], '').strip()
            if description:
                validated_row['description'] = description.upper()
            else:
                errors.append("Missing description")
                validated_row['description'] = ''
            
            # Validate amount
            amount_str = row.get(self.column_mapping['amount'], '').strip()
            if amount_str:
                try:
                    # Remove currency symbols and commas
                    clean_amount = re.sub(r'[$,]', '', amount_str)
                    validated_row['amount'] = float(clean_amount)
                except ValueError:
                    errors.append(f"Invalid amount format: {amount_str}")
                    validated_row['amount'] = 0.0
            else:
                errors.append("Missing amount")
                validated_row['amount'] = 0.0
            
            # Validate balance (optional)
            balance_str = row.get(self.column_mapping['balance'], '').strip()
            if balance_str:
                try:
                    clean_balance = re.sub(r'[$,]', '', balance_str)
                    validated_row['balance'] = float(clean_balance)
                except ValueError:
                    errors.append(f"Invalid balance format: {balance_str}")
                    validated_row['balance'] = None
            else:
                validated_row['balance'] = None
            
            validated_row['validation_errors'] = errors
            return validated_row
            
        except Exception as e:
            return {
                'date': None,
                'description': '',
                'amount': 0.0,
                'balance': None,
                'validation_errors': [f"Row validation failed: {str(e)}"]
            }
    
    def categorize_transaction(self, description: str) -> str:
        """Categorize transaction based on description using regex patterns."""
        description = description.upper().strip()
        
        for category, patterns in self.category_patterns.items():
            for pattern in patterns:
                if re.match(pattern, description, re.IGNORECASE):
                    return category
        
        return 'Other'
    
    def parse_csv_content(self, csv_content: str) -> List[Dict[str, Any]]:
        """Parse CSV content and return list of processed transactions."""
        transactions = []
        
        try:
            csv_reader = csv.DictReader(StringIO(csv_content))
            
            for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 for header
                try:
                    validated_row = self.validate_row_data(row)
                    
                    # Add category
                    validated_row['category'] = self.categorize_transaction(
                        validated_row['description']
                    )
                    
                    # Add row number for reference
                    validated_row['row_number'] = row_num
                    
                    transactions.append(validated_row)
                    
                except Exception as e:
                    print(f"Error processing row {row_num}: {str(e)}")
                    continue
        
        except Exception as e:
            print(f"Error parsing CSV: {str(e)}")
            raise
        
        return transactions
    
    def generate_summary_report(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary report of transactions."""
        total_transactions = len(transactions)
        total_amount = sum(t['amount'] for t in transactions)
        
        # Category breakdown
        category_summary = {}
        for transaction in transactions:
            category = transaction['category']