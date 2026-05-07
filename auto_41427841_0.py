```python
"""
Bank Statement Parser

A self-contained Python script that parses CSV bank statements from common banks
(Chase, Bank of America, Wells Fargo) and normalizes transaction data into a
standardized format.

The script automatically detects the bank format based on CSV headers and converts
transactions to a uniform structure with fields: date, description, amount, account.

Usage: python script.py
"""

import csv
import re
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple


class BankStatementParser:
    """Parser for common bank statement CSV formats."""
    
    def __init__(self):
        self.bank_formats = {
            'chase': {
                'headers': ['Transaction Date', 'Post Date', 'Description', 'Category', 'Type', 'Amount', 'Memo'],
                'date_field': 'Transaction Date',
                'description_field': 'Description',
                'amount_field': 'Amount',
                'date_format': '%m/%d/%Y'
            },
            'bofa': {
                'headers': ['Date', 'Description', 'Amount', 'Running Bal.'],
                'date_field': 'Date',
                'description_field': 'Description',
                'amount_field': 'Amount',
                'date_format': '%m/%d/%Y'
            },
            'wells_fargo': {
                'headers': ['Date', 'Amount', 'Check Number', 'Description'],
                'date_field': 'Date',
                'description_field': 'Description',
                'amount_field': 'Amount',
                'date_format': '%m/%d/%Y'
            }
        }
    
    def detect_bank_format(self, headers: List[str]) -> Optional[str]:
        """Detect bank format based on CSV headers."""
        try:
            headers_lower = [h.lower().strip() for h in headers]
            
            # Chase detection
            chase_indicators = ['transaction date', 'post date', 'category', 'type']
            if all(indicator in headers_lower for indicator in chase_indicators):
                return 'chase'
            
            # Bank of America detection
            bofa_indicators = ['running bal.', 'date', 'description', 'amount']
            if all(indicator in headers_lower for indicator in bofa_indicators):
                return 'bofa'
            
            # Wells Fargo detection
            wells_indicators = ['check number']
            if any(indicator in headers_lower for indicator in wells_indicators) and 'date' in headers_lower:
                return 'wells_fargo'
            
            return None
        except Exception as e:
            print(f"Error detecting bank format: {e}")
            return None
    
    def normalize_amount(self, amount_str: str) -> float:
        """Normalize amount string to float."""
        try:
            # Remove currency symbols, commas, and extra spaces
            cleaned = re.sub(r'[$,\s]', '', str(amount_str).strip())
            
            # Handle parentheses for negative amounts
            if cleaned.startswith('(') and cleaned.endswith(')'):
                cleaned = '-' + cleaned[1:-1]
            
            return float(cleaned)
        except (ValueError, AttributeError):
            return 0.0
    
    def normalize_date(self, date_str: str, date_format: str) -> str:
        """Normalize date to YYYY-MM-DD format."""
        try:
            parsed_date = datetime.strptime(date_str.strip(), date_format)
            return parsed_date.strftime('%Y-%m-%d')
        except ValueError:
            # Try alternative formats
            alternative_formats = ['%Y-%m-%d', '%m-%d-%Y', '%d/%m/%Y']
            for fmt in alternative_formats:
                try:
                    parsed_date = datetime.strptime(date_str.strip(), fmt)
                    return parsed_date.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            return date_str  # Return original if parsing fails
    
    def parse_csv_file(self, file_path: str) -> Tuple[List[Dict], str]:
        """Parse a single CSV file and return normalized transactions."""
        transactions = []
        detected_bank = None
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                # Try to detect delimiter
                sample = file.read(1024)
                file.seek(0)
                
                delimiter = ','
                if sample.count(';') > sample.count(','):
                    delimiter = ';'
                elif sample.count('\t') > sample.count(','):
                    delimiter = '\t'
                
                reader = csv.DictReader(file, delimiter=delimiter)
                
                # Detect bank format from headers
                headers = reader.fieldnames if reader.fieldnames else []
                detected_bank = self.detect_bank_format(headers)
                
                if not detected_bank:
                    print(f"Warning: Could not detect bank format for {file_path}")
                    print(f"Headers found: {headers}")
                    return transactions, "unknown"
                
                bank_config = self.bank_formats[detected_bank]
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        # Extract and normalize fields
                        date_raw = row.get(bank_config['date_field'], '')
                        description_raw = row.get(bank_config['description_field'], '')
                        amount_raw = row.get(bank_config['amount_field'], '')
                        
                        if not date_raw or not amount_raw:
                            continue  # Skip incomplete rows
                        
                        normalized_transaction = {
                            'date': self.normalize_date(date_raw, bank_config['date_format']),
                            'description': description_raw.strip(),
                            'amount': self.normalize_amount(amount_raw),
                            'account': detected_bank.replace('_', ' ').title(),
                            'source_file': os.path.basename(file_path)
                        }
                        
                        transactions.append(normalized_transaction)
                        
                    except Exception as e:
                        print(f"Error parsing row {row_num} in {file_path}: {e}")
                        continue
                        
        except FileNotFoundError:
            print(f"Error: File not found - {file_path}")
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
        
        return transactions, detected_bank
    
    def find_csv_files(self, directory: str = '.') -> List[str]:
        """Find all CSV files in the given directory."""
        csv_files = []
        try:
            for file in os.listdir(directory):
                if file.lower().endswith('.csv'):
                    csv_files.append(os.path.join(directory, file))
        except OSError as e:
            print(f"Error accessing directory {directory}: {e}")
        
        return csv_files
    
    def process_statements(self, file_paths: List[str] = None) -> List[Dict]:
        """Process bank statements and return normalized transactions."""
        all_transactions = []
        
        if file_paths is None:
            file_paths = self.find_csv_files()
        
        if not file_paths:
            print("No CSV files found in current directory.")
            return all_transactions
        
        for file_path in file_paths:
            print(f"Processing: {file_path}")
            transactions, bank_type = self.parse_csv_file(file_path)
            
            if transactions:
                print(f"  Detected: {bank_type.replace('_', ' ').title()}")
                print(f"  Parsed: {len(transactions)} transactions")
                all_transactions.extend(transactions)
            else:
                print(f"  No transactions found or unsupported format")
        
        # Sort by date
        try:
            all_transactions.sort(key=lambda x: x['date'])
        except Exception as e:
            print(f"Warning: Could not sort transactions by date: {e}")
        
        return all_transactions


def main():