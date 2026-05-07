```python
"""
Bank CSV Parser and Standardizer

This module parses CSV files from common banks (Chase, Bank of America, Wells Fargo)
and converts them into a standardized transaction format. It automatically detects
the bank format based on CSV headers and outputs unified transaction data.

Standardized format includes:
- date: Transaction date in YYYY-MM-DD format
- amount: Transaction amount as float (negative for debits, positive for credits)
- description: Transaction description/memo
- account: Account identifier (last 4 digits when available)

Usage: python script.py [csv_file_path]
If no file path provided, uses sample data for demonstration.
"""

import csv
import sys
import re
from datetime import datetime
from typing import List, Dict, Optional, Tuple


class BankCSVParser:
    """Parses and standardizes bank CSV formats from major US banks."""
    
    def __init__(self):
        self.parsers = {
            'chase': self._parse_chase,
            'bofa': self._parse_bofa,
            'wells_fargo': self._parse_wells_fargo
        }
    
    def detect_bank_format(self, headers: List[str]) -> Optional[str]:
        """Detect bank format based on CSV headers."""
        headers_lower = [h.lower().strip() for h in headers]
        
        # Chase patterns
        if any('posting date' in h for h in headers_lower) and any('amount' in h for h in headers_lower):
            return 'chase'
        
        # Bank of America patterns
        if any('posted date' in h for h in headers_lower) and any('payee' in h for h in headers_lower):
            return 'bofa'
        
        # Wells Fargo patterns
        if any('date' in h for h in headers_lower) and any('amount' in h for h in headers_lower):
            return 'wells_fargo'
        
        return None
    
    def _normalize_date(self, date_str: str) -> str:
        """Convert various date formats to YYYY-MM-DD."""
        date_str = date_str.strip()
        
        # Common patterns: MM/DD/YYYY, MM-DD-YYYY, YYYY-MM-DD
        patterns = [
            r'(\d{1,2})/(\d{1,2})/(\d{4})',
            r'(\d{1,2})-(\d{1,2})-(\d{4})',
            r'(\d{4})-(\d{1,2})-(\d{1,2})'
        ]
        
        for pattern in patterns:
            match = re.match(pattern, date_str)
            if match:
                if len(match.group(1)) == 4:  # YYYY-MM-DD format
                    return date_str
                else:  # MM/DD/YYYY or MM-DD-YYYY format
                    month, day, year = match.groups()
                    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        return date_str  # Return as-is if no pattern matches
    
    def _normalize_amount(self, amount_str: str) -> float:
        """Convert amount string to float, handling various formats."""
        amount_str = amount_str.strip().replace('$', '').replace(',', '')
        
        # Handle parentheses as negative
        if amount_str.startswith('(') and amount_str.endswith(')'):
            amount_str = '-' + amount_str[1:-1]
        
        try:
            return float(amount_str)
        except ValueError:
            return 0.0
    
    def _parse_chase(self, row: Dict[str, str]) -> Dict[str, str]:
        """Parse Chase bank CSV format."""
        return {
            'date': self._normalize_date(row.get('Posting Date', '')),
            'amount': self._normalize_amount(row.get('Amount', '0')),
            'description': row.get('Description', '').strip(),
            'account': row.get('Account', '')[-4:] if row.get('Account') else ''
        }
    
    def _parse_bofa(self, row: Dict[str, str]) -> Dict[str, str]:
        """Parse Bank of America CSV format."""
        return {
            'date': self._normalize_date(row.get('Posted Date', '')),
            'amount': self._normalize_amount(row.get('Amount', '0')),
            'description': row.get('Payee', '').strip(),
            'account': row.get('Account', '')[-4:] if row.get('Account') else ''
        }
    
    def _parse_wells_fargo(self, row: Dict[str, str]) -> Dict[str, str]:
        """Parse Wells Fargo CSV format."""
        return {
            'date': self._normalize_date(row.get('Date', '')),
            'amount': self._normalize_amount(row.get('Amount', '0')),
            'description': row.get('Description', '').strip(),
            'account': row.get('Account Number', '')[-4:] if row.get('Account Number') else ''
        }
    
    def parse_csv(self, file_path: str) -> List[Dict[str, str]]:
        """Parse CSV file and return standardized transactions."""
        transactions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # Read first line to detect format
                first_line = file.readline().strip()
                file.seek(0)
                
                reader = csv.DictReader(file)
                headers = reader.fieldnames
                
                if not headers:
                    raise ValueError("CSV file has no headers")
                
                bank_format = self.detect_bank_format(headers)
                
                if not bank_format:
                    raise ValueError(f"Unknown bank format. Headers found: {headers}")
                
                parser_func = self.parsers[bank_format]
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        transaction = parser_func(row)
                        transactions.append(transaction)
                    except Exception as e:
                        print(f"Warning: Error parsing row {row_num}: {e}", file=sys.stderr)
                
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except Exception as e:
            raise Exception(f"Error reading CSV file: {e}")
        
        return transactions


def create_sample_data():
    """Create sample CSV data for demonstration."""
    sample_files = {
        'chase_sample.csv': [
            "Posting Date,Description,Amount,Account",
            "01/15/2024,GROCERY STORE PURCHASE,-45.67,****1234",
            "01/16/2024,SALARY DEPOSIT,2500.00,****1234",
            "01/17/2024,ATM WITHDRAWAL,-100.00,****1234"
        ],
        'bofa_sample.csv': [
            "Posted Date,Payee,Amount,Account",
            "01/15/2024,TARGET STORE,($67.89),****5678",
            "01/16/2024,DIRECT DEPOSIT,$3000.00,****5678",
            "01/17/2024,COFFEE SHOP,($4.50),****5678"
        ],
        'wells_fargo_sample.csv': [
            "Date,Description,Amount,Account Number",
            "01/15/2024,GAS STATION,-35.20,****9012",
            "01/16/2024,PAYCHECK DEPOSIT,2800.00,****9012",
            "01/17/2024,RESTAURANT,-25.75,****9012"
        ]
    }
    
    for filename, lines in sample_files.items():
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            print(f"Created sample file: {filename}")
        except Exception as e:
            print(f"Error creating {filename}: {e}", file=sys.stderr)


def main():
    """Main