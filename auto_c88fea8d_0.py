```python
"""
Bank Transaction CSV Parser and Categorizer

This module provides functionality to parse bank transaction CSV files and automatically
categorize transactions based on predefined keyword dictionaries. It reads transaction
data from CSV files and applies rule-based categorization to classify expenses into
common categories like groceries, gas, dining, etc.

Features:
- CSV parsing with flexible column detection
- Rule-based transaction categorization using keyword matching
- Error handling for file operations and data processing
- Self-contained implementation using only standard library
- Configurable category rules and keywords

Usage:
    python script.py

The script expects a CSV file with transaction data including at least:
- Description/merchant name
- Amount (positive for credits, negative for debits)
- Date (various formats supported)
"""

import csv
import re
import sys
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class TransactionCategorizer:
    """Handles rule-based categorization of bank transactions."""
    
    def __init__(self):
        """Initialize with predefined category keywords."""
        self.category_rules = {
            'Groceries': [
                'walmart', 'target', 'kroger', 'safeway', 'whole foods', 'trader joe',
                'costco', 'sams club', 'grocery', 'supermarket', 'food lion',
                'giant', 'stop shop', 'wegmans', 'publix', 'aldi'
            ],
            'Gas & Fuel': [
                'shell', 'exxon', 'bp', 'chevron', 'mobil', 'texaco', 'sunoco',
                'marathon', 'valero', 'citgo', 'gas station', 'fuel', 'petro'
            ],
            'Dining & Restaurants': [
                'restaurant', 'mcdonald', 'burger king', 'subway', 'pizza',
                'starbucks', 'dunkin', 'taco bell', 'kfc', 'wendys', 'chipotle',
                'panera', 'cafe', 'diner', 'bistro', 'grill', 'bar'
            ],
            'Shopping': [
                'amazon', 'ebay', 'best buy', 'home depot', 'lowes', 'macys',
                'nordstrom', 'tj maxx', 'marshalls', 'kohls', 'jcpenney',
                'old navy', 'gap', 'victoria secret', 'bath body works'
            ],
            'Transportation': [
                'uber', 'lyft', 'taxi', 'metro', 'bus', 'train', 'parking',
                'toll', 'subway', 'transit', 'transport', 'airline', 'flight'
            ],
            'Healthcare': [
                'pharmacy', 'cvs', 'walgreens', 'rite aid', 'hospital',
                'medical', 'doctor', 'dental', 'clinic', 'health', 'prescription'
            ],
            'Utilities': [
                'electric', 'gas company', 'water', 'sewer', 'internet',
                'cable', 'phone', 'wireless', 'verizon', 'att', 'comcast',
                'spectrum', 'utility'
            ],
            'Banking & Finance': [
                'bank', 'atm', 'fee', 'interest', 'transfer', 'payment',
                'credit card', 'loan', 'mortgage', 'insurance'
            ],
            'Entertainment': [
                'movie', 'theater', 'netflix', 'spotify', 'hulu', 'disney',
                'xbox', 'playstation', 'steam', 'ticket', 'concert', 'game'
            ]
        }
    
    def categorize_transaction(self, description: str, amount: float) -> str:
        """
        Categorize a transaction based on its description and amount.
        
        Args:
            description: Transaction description/merchant name
            amount: Transaction amount (negative for expenses)
            
        Returns:
            Category name or 'Other' if no match found
        """
        if not description:
            return 'Other'
        
        description_lower = description.lower()
        
        # Check each category's keywords
        for category, keywords in self.category_rules.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        # Special cases based on amount patterns
        if amount > 0:
            return 'Income/Credit'
        elif amount < -500:
            return 'Large Expense'
        
        return 'Other'


class CSVTransactionParser:
    """Parses CSV files containing bank transaction data."""
    
    def __init__(self, categorizer: TransactionCategorizer):
        """Initialize with a transaction categorizer."""
        self.categorizer = categorizer
        self.supported_date_formats = [
            '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%m-%d-%Y',
            '%Y/%m/%d', '%d-%m-%Y', '%m/%d/%y', '%d/%m/%y'
        ]
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string using various common formats."""
        if not date_str:
            return None
        
        for fmt in self.supported_date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        return None
    
    def parse_amount(self, amount_str: str) -> float:
        """Parse amount string, handling currency symbols and formatting."""
        if not amount_str:
            return 0.0
        
        # Remove currency symbols and spaces
        cleaned = re.sub(r'[$,\s]', '', amount_str.strip())
        
        # Handle parentheses for negative amounts
        if cleaned.startswith('(') and cleaned.endswith(')'):
            cleaned = '-' + cleaned[1:-1]
        
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
    
    def detect_columns(self, headers: List[str]) -> Dict[str, int]:
        """
        Auto-detect column indices based on common header names.
        
        Args:
            headers: List of column headers from CSV
            
        Returns:
            Dictionary mapping column types to indices
        """
        column_map = {}
        headers_lower = [h.lower().strip() for h in headers]
        
        # Date column detection
        date_keywords = ['date', 'transaction date', 'posted date', 'trans date']
        for i, header in enumerate(headers_lower):
            if any(keyword in header for keyword in date_keywords):
                column_map['date'] = i
                break
        
        # Description column detection
        desc_keywords = ['description', 'merchant', 'payee', 'details', 'memo']
        for i, header in enumerate(headers_lower):
            if any(keyword in header for keyword in desc_keywords):
                column_map['description'] = i
                break
        
        # Amount column detection
        amount_keywords = ['amount', 'debit', 'credit', 'transaction amount']
        for i, header in enumerate(headers_lower):
            if any(keyword in header for keyword in amount_keywords):
                column_map['amount'] = i
                break
        
        return column_map
    
    def parse_csv(self, filepath: str) -> List[Dict]:
        """
        Parse CSV file and return list of categorized transactions.
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            List of transaction dictionaries with categories
        """
        transactions = []
        
        try:
            with open(filepath, 'r', newline='', encoding='utf-8') as file:
                # Try to detect delimiter
                sample = file.read(1024)
                file.seek(0)
                
                sniffer = csv.Sniffer()
                try:
                    delimiter = sniffer.sniff(sample).delimiter
                except csv.Error:
                    delimiter = ','
                
                reader = csv.reader(file, delimiter=delimiter)
                headers = next(reader, [])
                
                if not headers: