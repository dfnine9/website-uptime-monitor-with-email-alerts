```python
"""
Bank Statement CSV Parser

A self-contained Python script that parses CSV bank statement files from various banks,
automatically detects common CSV formats, and extracts transaction data into a
standardized data structure.

Supports multiple bank formats by detecting column patterns and data structures.
Outputs standardized transaction data with date, description, amount, and balance fields.

Usage: python script.py [csv_file_path]
If no file path provided, uses sample data for demonstration.
"""

import csv
import re
import sys
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation


@dataclass
class Transaction:
    """Standardized transaction data structure"""
    date: str
    description: str
    amount: float
    balance: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'date': self.date,
            'description': self.description,
            'amount': self.amount,
            'balance': self.balance
        }


class BankStatementParser:
    """Parser for bank statement CSV files with automatic format detection"""
    
    def __init__(self):
        self.date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{4}',
            r'\d{4}-\d{2}-\d{2}',
            r'\d{1,2}-\d{1,2}-\d{4}',
            r'\d{2}/\d{2}/\d{4}',
            r'\d{1,2}/\d{1,2}/\d{2}'
        ]
        
        self.amount_patterns = [
            r'-?\$?[\d,]+\.?\d*',
            r'-?[\d,]+\.?\d*'
        ]
    
    def detect_format(self, rows: List[List[str]]) -> Dict[str, int]:
        """
        Detect CSV format by analyzing column headers and data patterns
        Returns mapping of field names to column indices
        """
        if not rows:
            raise ValueError("No data rows found")
        
        headers = rows[0] if rows else []
        sample_rows = rows[1:6] if len(rows) > 1 else []
        
        format_map = {}
        
        # Try to detect columns by header names
        for i, header in enumerate(headers):
            header_lower = header.lower().strip()
            
            if any(keyword in header_lower for keyword in ['date', 'transaction date', 'posted date']):
                format_map['date'] = i
            elif any(keyword in header_lower for keyword in ['description', 'memo', 'reference', 'details']):
                format_map['description'] = i
            elif any(keyword in header_lower for keyword in ['amount', 'debit', 'credit']):
                if 'amount' not in format_map:
                    format_map['amount'] = i
            elif any(keyword in header_lower for keyword in ['balance', 'running balance']):
                format_map['balance'] = i
        
        # If header detection failed, try pattern matching on sample data
        if 'date' not in format_map and sample_rows:
            for col_idx in range(len(headers)):
                if self._is_date_column(sample_rows, col_idx):
                    format_map['date'] = col_idx
                    break
        
        if 'amount' not in format_map and sample_rows:
            for col_idx in range(len(headers)):
                if self._is_amount_column(sample_rows, col_idx):
                    format_map['amount'] = col_idx
                    break
        
        # Try to find description column (usually longest text)
        if 'description' not in format_map and sample_rows:
            desc_col = self._find_description_column(sample_rows, format_map)
            if desc_col is not None:
                format_map['description'] = desc_col
        
        return format_map
    
    def _is_date_column(self, sample_rows: List[List[str]], col_idx: int) -> bool:
        """Check if a column contains date values"""
        date_matches = 0
        for row in sample_rows:
            if col_idx < len(row):
                cell = row[col_idx].strip()
                if any(re.match(pattern, cell) for pattern in self.date_patterns):
                    date_matches += 1
        
        return date_matches >= len(sample_rows) * 0.6
    
    def _is_amount_column(self, sample_rows: List[List[str]], col_idx: int) -> bool:
        """Check if a column contains amount values"""
        amount_matches = 0
        for row in sample_rows:
            if col_idx < len(row):
                cell = row[col_idx].strip()
                try:
                    float(cell.replace('$', '').replace(',', ''))
                    amount_matches += 1
                except ValueError:
                    continue
        
        return amount_matches >= len(sample_rows) * 0.6
    
    def _find_description_column(self, sample_rows: List[List[str]], existing_map: Dict[str, int]) -> Optional[int]:
        """Find the column most likely to contain descriptions"""
        used_columns = set(existing_map.values())
        
        best_col = None
        max_avg_length = 0
        
        for col_idx in range(len(sample_rows[0]) if sample_rows else 0):
            if col_idx in used_columns:
                continue
            
            total_length = 0
            valid_entries = 0
            
            for row in sample_rows:
                if col_idx < len(row):
                    cell = row[col_idx].strip()
                    if cell and not self._looks_like_number(cell):
                        total_length += len(cell)
                        valid_entries += 1
            
            if valid_entries > 0:
                avg_length = total_length / valid_entries
                if avg_length > max_avg_length:
                    max_avg_length = avg_length
                    best_col = col_idx
        
        return best_col
    
    def _looks_like_number(self, text: str) -> bool:
        """Check if text looks like a number"""
        try:
            float(text.replace('$', '').replace(',', ''))
            return True
        except ValueError:
            return False
    
    def parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float"""
        try:
            # Remove currency symbols and whitespace
            cleaned = amount_str.replace('$', '').replace(',', '').strip()
            
            # Handle parentheses as negative
            if cleaned.startswith('(') and cleaned.endswith(')'):
                cleaned = '-' + cleaned[1:-1]
            
            return float(cleaned)
        except (ValueError, AttributeError):
            return 0.0
    
    def parse_date(self, date_str: str) -> str:
        """Parse date string to standardized format"""
        try:
            date_str = date_str.strip()
            
            # Try common date formats
            formats = ['%m/%d/%Y', '%Y-%m-%d', '%m-%d-%Y', '%m/%d/%y']
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            
            return date_str  # Return original if parsing fails
        except (ValueError, AttributeError):
            return date_str
    
    def parse_csv(self, file_path: str) -> List[Transaction]:
        """
        Parse CSV file and return list of Transaction objects
        """
        transactions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', newline='') as file:
                # Try to detect delimiter
                sample = file.read(1024)
                file.seek(0)
                
                sniffer = csv.Sniffer()
                try