```python
#!/usr/bin/env python3
"""
Bank Statement CSV Parser

This module parses CSV bank statement files and extracts transaction data including
date, description, and amount fields. It creates a standardized data structure for
further processing and analysis.

Features:
- Automatic CSV format detection (comma, semicolon, tab delimiters)
- Flexible column mapping for common bank statement formats
- Data validation and type conversion
- Error handling for malformed files and data
- Support for multiple date formats
- Amount parsing with currency symbol removal

Usage:
    python script.py

The script will look for CSV files in the current directory and process them.
Results are printed to stdout in a structured format.
"""

import csv
import os
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Optional, Tuple, Any


class BankStatementParser:
    """Parser for bank statement CSV files with automatic format detection."""
    
    def __init__(self):
        self.date_formats = [
            '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d',
            '%d-%m-%Y', '%m-%d-%Y', '%Y%m%d', '%d.%m.%Y',
            '%m.%d.%Y', '%Y.%m.%d'
        ]
        
        # Common column name variations
        self.column_mappings = {
            'date': ['date', 'transaction date', 'posting date', 'value date', 'trans date'],
            'description': ['description', 'memo', 'details', 'transaction details', 'reference'],
            'amount': ['amount', 'transaction amount', 'debit', 'credit', 'balance change']
        }
    
    def detect_delimiter(self, file_path: str) -> str:
        """Detect the CSV delimiter used in the file."""
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as file:
                sample = file.read(1024)
                
            # Check for common delimiters
            delimiters = [',', ';', '\t', '|']
            delimiter_counts = {}
            
            for delimiter in delimiters:
                delimiter_counts[delimiter] = sample.count(delimiter)
            
            # Return the delimiter with the highest count
            return max(delimiter_counts, key=delimiter_counts.get)
            
        except Exception as e:
            print(f"Error detecting delimiter: {e}")
            return ','  # Default fallback
    
    def normalize_column_name(self, column_name: str) -> Optional[str]:
        """Normalize column names to standard field names."""
        if not column_name:
            return None
            
        normalized = column_name.lower().strip()
        
        for standard_name, variations in self.column_mappings.items():
            if any(variation in normalized for variation in variations):
                return standard_name
        
        return normalized
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string using multiple format attempts."""
        if not date_str or not date_str.strip():
            return None
            
        date_str = date_str.strip()
        
        for date_format in self.date_formats:
            try:
                return datetime.strptime(date_str, date_format)
            except ValueError:
                continue
        
        return None
    
    def parse_amount(self, amount_str: str) -> Optional[Decimal]:
        """Parse amount string, handling currency symbols and formatting."""
        if not amount_str or not amount_str.strip():
            return None
        
        # Clean the amount string
        cleaned = re.sub(r'[^\d.,\-+]', '', amount_str.strip())
        
        if not cleaned:
            return None
        
        # Handle different decimal separators
        if ',' in cleaned and '.' in cleaned:
            # Determine which is the decimal separator based on position
            last_comma = cleaned.rfind(',')
            last_dot = cleaned.rfind('.')
            
            if last_comma > last_dot:
                # Comma is decimal separator
                cleaned = cleaned.replace('.', '').replace(',', '.')
            else:
                # Dot is decimal separator
                cleaned = cleaned.replace(',', '')
        elif ',' in cleaned:
            # Check if comma is likely a decimal separator
            parts = cleaned.split(',')
            if len(parts) == 2 and len(parts[1]) <= 2:
                cleaned = cleaned.replace(',', '.')
            else:
                cleaned = cleaned.replace(',', '')
        
        try:
            return Decimal(cleaned)
        except (InvalidOperation, ValueError):
            return None
    
    def map_columns(self, headers: List[str]) -> Dict[str, int]:
        """Map CSV headers to standard column indices."""
        column_map = {}
        normalized_headers = [self.normalize_column_name(h) for h in headers]
        
        for i, normalized_header in enumerate(normalized_headers):
            if normalized_header in ['date', 'description', 'amount']:
                column_map[normalized_header] = i
        
        return column_map
    
    def parse_csv_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse a CSV bank statement file and return structured transaction data."""
        transactions = []
        
        try:
            delimiter = self.detect_delimiter(file_path)
            
            with open(file_path, 'r', encoding='utf-8-sig') as file:
                # Try to detect if file has headers
                sample_lines = []
                for _ in range(3):
                    line = file.readline()
                    if line:
                        sample_lines.append(line)
                
                file.seek(0)  # Reset file pointer
                
                reader = csv.reader(file, delimiter=delimiter)
                headers = next(reader, None)
                
                if not headers:
                    raise ValueError("No headers found in CSV file")
                
                column_map = self.map_columns(headers)
                
                if not column_map:
                    print(f"Warning: Could not map columns in {file_path}")
                    print(f"Available headers: {headers}")
                    return []
                
                for row_num, row in enumerate(reader, start=2):
                    if len(row) < len(headers):
                        continue  # Skip incomplete rows
                    
                    transaction = {}
                    
                    # Extract date
                    if 'date' in column_map:
                        date_obj = self.parse_date(row[column_map['date']])
                        transaction['date'] = date_obj.isoformat() if date_obj else None
                        transaction['date_raw'] = row[column_map['date']]
                    
                    # Extract description
                    if 'description' in column_map:
                        transaction['description'] = row[column_map['description']].strip()
                    
                    # Extract amount
                    if 'amount' in column_map:
                        amount_obj = self.parse_amount(row[column_map['amount']])
                        transaction['amount'] = float(amount_obj) if amount_obj else None
                        transaction['amount_raw'] = row[column_map['amount']]
                    
                    # Add metadata
                    transaction['source_file'] = os.path.basename(file_path)
                    transaction['row_number'] = row_num
                    
                    # Only add transaction if we have at least one valid field
                    if any(transaction.get(field) is not None for field in ['date', 'description', 'amount']):
                        transactions.append(transaction)
                
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return []
        
        return transactions


def main():
    """Main function to process CSV files in current directory."""
    parser = BankStatementParser()
    
    # Find CSV files in current directory
    csv_files = [f for f in os.listdir('.') if f.lower().endswith('.csv')]
    
    if not csv_files:
        print("No CSV files found in current directory.")
        return
    
    all_transactions = []