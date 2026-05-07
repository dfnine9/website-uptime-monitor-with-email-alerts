```python
#!/usr/bin/env python3
"""
Bank Transaction CSV Parser and Categorizer

This module parses CSV files exported from bank accounts and categorizes transactions
based on configurable keyword mappings. It extracts transaction data including date,
amount, description, and merchant information, then applies keyword-based rules to
assign categories like 'grocery', 'gas', 'restaurant', etc.

The script uses only standard library modules and can handle various CSV formats
commonly used by banks. Categories are configurable and can be easily modified
to match personal spending patterns.

Usage: python script.py
"""

import csv
import re
import sys
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from pathlib import Path


class TransactionCategorizer:
    """Categorizes bank transactions based on configurable keyword rules."""
    
    def __init__(self):
        """Initialize with default category mappings."""
        self.category_mappings = {
            'grocery': [
                'walmart', 'target', 'kroger', 'safeway', 'whole foods', 'trader joe',
                'costco', 'sam\'s club', 'publix', 'food lion', 'harris teeter',
                'giant', 'wegmans', 'stop & shop', 'king soopers', 'fred meyer'
            ],
            'gas': [
                'shell', 'exxon', 'bp', 'chevron', 'mobil', 'texaco', 'sunoco',
                'gulf', 'citgo', 'marathon', 'valero', 'speedway', 'wawa',
                'gas station', 'fuel'
            ],
            'restaurant': [
                'mcdonald', 'burger king', 'subway', 'taco bell', 'kfc', 'pizza',
                'starbucks', 'dunkin', 'chipotle', 'panera', 'olive garden',
                'applebee', 'chili\'s', 'restaurant', 'bistro', 'cafe', 'diner',
                'grill', 'kitchen', 'bar & grill'
            ],
            'entertainment': [
                'netflix', 'spotify', 'amazon prime', 'disney', 'hulu', 'youtube',
                'theater', 'cinema', 'movie', 'game', 'xbox', 'playstation',
                'steam', 'entertainment', 'concert', 'tickets'
            ],
            'shopping': [
                'amazon', 'ebay', 'best buy', 'home depot', 'lowe\'s', 'macy\'s',
                'nordstrom', 'tj maxx', 'marshall', 'ross', 'department store',
                'outlet', 'mall'
            ],
            'utilities': [
                'electric', 'electricity', 'gas company', 'water', 'sewer',
                'internet', 'cable', 'phone', 'wireless', 'utility', 'power'
            ],
            'healthcare': [
                'pharmacy', 'cvs', 'walgreens', 'rite aid', 'hospital', 'medical',
                'doctor', 'dentist', 'clinic', 'health', 'prescription'
            ],
            'transport': [
                'uber', 'lyft', 'taxi', 'bus', 'metro', 'subway', 'train',
                'parking', 'toll', 'airport'
            ],
            'banking': [
                'atm fee', 'bank fee', 'overdraft', 'interest', 'transfer',
                'deposit', 'withdrawal'
            ]
        }
    
    def categorize_transaction(self, description: str, merchant: str = '') -> str:
        """
        Categorize a transaction based on description and merchant.
        
        Args:
            description: Transaction description
            merchant: Merchant name (optional)
            
        Returns:
            Category name or 'other' if no match found
        """
        text_to_search = f"{description} {merchant}".lower()
        
        for category, keywords in self.category_mappings.items():
            for keyword in keywords:
                if keyword in text_to_search:
                    return category
        
        return 'other'


class BankCSVParser:
    """Parses CSV files from various bank export formats."""
    
    def __init__(self):
        """Initialize the parser."""
        self.categorizer = TransactionCategorizer()
    
    def detect_csv_format(self, file_path: str) -> Dict[str, int]:
        """
        Detect the CSV format by examining headers.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            Dictionary mapping field names to column indices
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # Try to detect delimiter
                sample = file.read(1024)
                file.seek(0)
                
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.reader(file, delimiter=delimiter)
                headers = next(reader)
                
                # Normalize headers to lowercase for easier matching
                headers = [h.lower().strip() for h in headers]
                
                # Map common header variations to standard fields
                field_mapping = {}
                
                for i, header in enumerate(headers):
                    if any(date_word in header for date_word in ['date', 'transaction date', 'posted date']):
                        field_mapping['date'] = i
                    elif any(amount_word in header for amount_word in ['amount', 'transaction amount', 'debit', 'credit']):
                        field_mapping['amount'] = i
                    elif any(desc_word in header for desc_word in ['description', 'transaction description', 'memo', 'details']):
                        field_mapping['description'] = i
                    elif any(merchant_word in header for merchant_word in ['merchant', 'payee', 'vendor', 'business']):
                        field_mapping['merchant'] = i
                
                return field_mapping
                
        except Exception as e:
            print(f"Error detecting CSV format: {e}", file=sys.stderr)
            return {}
    
    def parse_amount(self, amount_str: str) -> float:
        """
        Parse amount string to float, handling various formats.
        
        Args:
            amount_str: Amount as string
            
        Returns:
            Amount as float
        """
        if not amount_str:
            return 0.0
        
        # Remove currency symbols, commas, and extra spaces
        cleaned = re.sub(r'[$,\s]', '', str(amount_str))
        
        # Handle parentheses for negative amounts
        if cleaned.startswith('(') and cleaned.endswith(')'):
            cleaned = '-' + cleaned[1:-1]
        
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse date string to datetime object.
        
        Args:
            date_str: Date as string
            
        Returns:
            Datetime object or None if parsing fails
        """
        if not date_str:
            return None
        
        # Common date formats
        date_formats = [
            '%m/%d/%Y', '%m-%d-%Y', '%Y-%m-%d', '%m/%d/%y', '%m-%d-%y',
            '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d', '%d/%m/%y', '%d-%m-%y',
            '%B %d, %Y', '%b %d, %Y', '%d %B %Y', '%d %b %Y'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        return None
    
    def parse_csv_file(self, file_path: str) -> List[Dict]:
        """
        Parse CSV file and extract transaction data.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            List of transaction dictionaries