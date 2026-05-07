```python
#!/usr/bin/env python3
"""
Bank Transaction CSV Parser and Standardizer

This module parses CSV files from multiple bank formats (Chase, Bank of America, Wells Fargo)
and standardizes the transaction data into a common schema with fields:
- date: Transaction date in YYYY-MM-DD format
- amount: Transaction amount as float (negative for debits, positive for credits)
- description: Transaction description/memo
- category: Basic transaction category (debit/credit/transfer)

Supported bank formats:
- Chase: Date, Description, Amount, Type, Balance, Check or Slip #
- Bank of America: Date, Description, Amount, Running Bal.
- Wells Fargo: Date, Amount, *, *, Description
"""

import csv
import sys
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import re


class BankTransactionParser:
    """Parser for standardizing bank CSV transaction formats."""
    
    def __init__(self):
        self.standardized_transactions = []
    
    def parse_date(self, date_str: str) -> str:
        """Parse various date formats and return YYYY-MM-DD format."""
        date_formats = [
            "%m/%d/%Y",    # MM/DD/YYYY
            "%m/%d/%y",    # MM/DD/YY
            "%Y-%m-%d",    # YYYY-MM-DD
            "%d/%m/%Y",    # DD/MM/YYYY
            "%m-%d-%Y",    # MM-DD-YYYY
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str.strip(), fmt)
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        # If no format matches, return original string
        return date_str.strip()
    
    def parse_amount(self, amount_str: str) -> float:
        """Parse amount string and return float."""
        try:
            # Remove currency symbols, commas, and extra spaces
            cleaned = re.sub(r'[\$,\s]', '', amount_str.strip())
            
            # Handle parentheses as negative (common in banking)
            if cleaned.startswith('(') and cleaned.endswith(')'):
                cleaned = '-' + cleaned[1:-1]
            
            return float(cleaned)
        except (ValueError, TypeError):
            return 0.0
    
    def categorize_transaction(self, description: str, amount: float) -> str:
        """Basic categorization of transactions."""
        description_lower = description.lower()
        
        if amount > 0:
            return "credit"
        elif "transfer" in description_lower or "xfer" in description_lower:
            return "transfer"
        else:
            return "debit"
    
    def parse_chase_csv(self, filepath: str) -> List[Dict[str, Any]]:
        """Parse Chase bank CSV format."""
        transactions = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    try:
                        # Chase format: Date, Description, Amount, Type, Balance, Check or Slip #
                        date = self.parse_date(row.get('Date', ''))
                        description = row.get('Description', '').strip()
                        amount = self.parse_amount(row.get('Amount', '0'))
                        category = self.categorize_transaction(description, amount)
                        
                        transaction = {
                            'date': date,
                            'amount': amount,
                            'description': description,
                            'category': category,
                            'bank': 'Chase'
                        }
                        transactions.append(transaction)
                        
                    except Exception as e:
                        print(f"Error parsing Chase row: {e}", file=sys.stderr)
                        continue
                        
        except FileNotFoundError:
            print(f"Chase CSV file not found: {filepath}", file=sys.stderr)
        except Exception as e:
            print(f"Error reading Chase CSV: {e}", file=sys.stderr)
            
        return transactions
    
    def parse_boa_csv(self, filepath: str) -> List[Dict[str, Any]]:
        """Parse Bank of America CSV format."""
        transactions = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    try:
                        # BofA format: Date, Description, Amount, Running Bal.
                        date = self.parse_date(row.get('Date', ''))
                        description = row.get('Description', '').strip()
                        amount = self.parse_amount(row.get('Amount', '0'))
                        category = self.categorize_transaction(description, amount)
                        
                        transaction = {
                            'date': date,
                            'amount': amount,
                            'description': description,
                            'category': category,
                            'bank': 'Bank of America'
                        }
                        transactions.append(transaction)
                        
                    except Exception as e:
                        print(f"Error parsing BofA row: {e}", file=sys.stderr)
                        continue
                        
        except FileNotFoundError:
            print(f"Bank of America CSV file not found: {filepath}", file=sys.stderr)
        except Exception as e:
            print(f"Error reading Bank of America CSV: {e}", file=sys.stderr)
            
        return transactions
    
    def parse_wells_fargo_csv(self, filepath: str) -> List[Dict[str, Any]]:
        """Parse Wells Fargo CSV format."""
        transactions = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                
                # Skip header if present
                header = next(reader, None)
                
                for row in reader:
                    try:
                        # Wells Fargo format: Date, Amount, *, *, Description
                        if len(row) >= 5:
                            date = self.parse_date(row[0])
                            amount = self.parse_amount(row[1])
                            description = row[4].strip()
                            category = self.categorize_transaction(description, amount)
                            
                            transaction = {
                                'date': date,
                                'amount': amount,
                                'description': description,
                                'category': category,
                                'bank': 'Wells Fargo'
                            }
                            transactions.append(transaction)
                            
                    except Exception as e:
                        print(f"Error parsing Wells Fargo row: {e}", file=sys.stderr)
                        continue
                        
        except FileNotFoundError:
            print(f"Wells Fargo CSV file not found: {filepath}", file=sys.stderr)
        except Exception as e:
            print(f"Error reading Wells Fargo CSV: {e}", file=sys.stderr)
            
        return transactions
    
    def process_files(self, file_paths: List[str]) -> None:
        """Process multiple CSV files and standardize transactions."""
        all_transactions = []
        
        for filepath in file_paths:
            if not os.path.exists(filepath):
                print(f"File not found: {filepath}", file=sys.stderr)
                continue
                
            filename_lower = os.path.basename(filepath).lower()
            
            try:
                if 'chase' in filename_lower:
                    transactions = self.parse_chase_csv(filepath)
                elif 'bofa' in filename_lower or 'bankofamerica' in filename_lower:
                    transactions = self.parse_boa_csv(filepath)
                elif 'wells' in filename_lower or 'wf' in filename_lower:
                    transactions = self.parse_wells_fargo_csv(filepath)
                else:
                    # Try to detect format by examining first few rows
                    transactions = self.auto_detect_format(filepath)
                    
                all_transactions.extend(transactions)
                print(f"