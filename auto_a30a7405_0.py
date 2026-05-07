```python
#!/usr/bin/env python3
"""
Transaction Categorization Script

This script parses CSV files containing financial transaction data and automatically
categorizes expenses based on predefined keywords. It supports common expense
categories like groceries, utilities, entertainment, and more.

Features:
- Reads CSV files with transaction data
- Categorizes transactions using keyword matching
- Handles multiple CSV formats automatically
- Provides detailed categorization statistics
- Includes comprehensive error handling

Usage: python script.py
"""

import csv
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class TransactionCategorizer:
    """Categorizes financial transactions based on predefined keyword patterns."""
    
    def __init__(self):
        """Initialize the categorizer with predefined category keywords."""
        self.categories = {
            'groceries': [
                'walmart', 'kroger', 'safeway', 'whole foods', 'trader joe',
                'publix', 'target', 'costco', 'sams club', 'grocery', 'food',
                'supermarket', 'market', 'fresh', 'organic', 'produce'
            ],
            'utilities': [
                'electric', 'electricity', 'gas', 'water', 'sewer', 'trash',
                'internet', 'cable', 'phone', 'wireless', 'verizon', 'att',
                'comcast', 'xfinity', 'utility', 'power', 'energy'
            ],
            'entertainment': [
                'netflix', 'spotify', 'disney', 'hulu', 'amazon prime',
                'movie', 'theater', 'cinema', 'concert', 'music', 'game',
                'entertainment', 'streaming', 'subscription', 'amusement'
            ],
            'restaurants': [
                'restaurant', 'cafe', 'coffee', 'starbucks', 'dunkin',
                'mcdonald', 'burger', 'pizza', 'subway', 'taco bell',
                'dining', 'bar', 'grill', 'bistro', 'diner'
            ],
            'transportation': [
                'gas station', 'shell', 'exxon', 'chevron', 'bp', 'uber',
                'lyft', 'taxi', 'metro', 'bus', 'train', 'parking',
                'toll', 'auto', 'car', 'vehicle', 'transportation'
            ],
            'shopping': [
                'amazon', 'ebay', 'store', 'shop', 'retail', 'mall',
                'clothing', 'apparel', 'shoes', 'electronics', 'best buy',
                'home depot', 'lowes', 'department store'
            ],
            'healthcare': [
                'hospital', 'doctor', 'medical', 'pharmacy', 'cvs',
                'walgreens', 'health', 'dental', 'vision', 'clinic',
                'urgent care', 'medicine', 'prescription'
            ],
            'banking': [
                'bank', 'atm', 'fee', 'charge', 'interest', 'loan',
                'credit', 'debit', 'transfer', 'withdrawal', 'deposit'
            ]
        }
    
    def categorize_transaction(self, description: str, amount: float = None) -> str:
        """
        Categorize a single transaction based on its description.
        
        Args:
            description: Transaction description text
            amount: Transaction amount (optional, for future enhancement)
            
        Returns:
            Category name or 'other' if no match found
        """
        if not description:
            return 'other'
        
        description_lower = description.lower()
        
        # Check each category for keyword matches
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'other'


class CSVTransactionParser:
    """Parses CSV files containing transaction data with flexible column detection."""
    
    def __init__(self, categorizer: TransactionCategorizer):
        """Initialize parser with a transaction categorizer."""
        self.categorizer = categorizer
        self.common_description_columns = [
            'description', 'desc', 'transaction_description', 'memo',
            'merchant', 'payee', 'reference', 'details', 'note'
        ]
        self.common_amount_columns = [
            'amount', 'transaction_amount', 'value', 'sum', 'total',
            'debit', 'credit', 'charge', 'payment'
        ]
    
    def detect_columns(self, headers: List[str]) -> Tuple[Optional[str], Optional[str]]:
        """
        Auto-detect description and amount columns from headers.
        
        Args:
            headers: List of column headers
            
        Returns:
            Tuple of (description_column, amount_column) or (None, None) if not found
        """
        headers_lower = [h.lower().strip() for h in headers]
        
        # Find description column
        description_col = None
        for desc_name in self.common_description_columns:
            if desc_name in headers_lower:
                description_col = headers[headers_lower.index(desc_name)]
                break
        
        # Find amount column
        amount_col = None
        for amt_name in self.common_amount_columns:
            if amt_name in headers_lower:
                amount_col = headers[headers_lower.index(amt_name)]
                break
        
        return description_col, amount_col
    
    def parse_amount(self, amount_str: str) -> Optional[float]:
        """
        Parse amount string to float, handling various formats.
        
        Args:
            amount_str: String representation of amount
            
        Returns:
            Float value or None if parsing fails
        """
        if not amount_str:
            return None
        
        try:
            # Remove currency symbols and commas
            cleaned = re.sub(r'[$,]', '', str(amount_str).strip())
            # Handle parentheses for negative amounts
            if cleaned.startswith('(') and cleaned.endswith(')'):
                cleaned = '-' + cleaned[1:-1]
            return float(cleaned)
        except (ValueError, TypeError):
            return None
    
    def parse_csv_file(self, file_path: str) -> List[Dict]:
        """
        Parse a CSV file and categorize transactions.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            List of transaction dictionaries with categories
        """
        transactions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', newline='') as file:
                # Detect delimiter
                sample = file.read(1024)
                file.seek(0)
                
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(file, delimiter=delimiter)
                headers = reader.fieldnames
                
                if not headers:
                    print(f"Error: No headers found in {file_path}")
                    return []
                
                # Auto-detect columns
                desc_col, amt_col = self.detect_columns(headers)
                
                if not desc_col:
                    print(f"Warning: Could not detect description column in {file_path}")
                    print(f"Available columns: {', '.join(headers)}")
                    return []
                
                print(f"Using description column: '{desc_col}'")
                if amt_col:
                    print(f"Using amount column: '{amt_col}'")
                
                # Process transactions
                for row_num, row in enumerate(reader, start=2):
                    try:
                        description = row.get(desc_col, '').strip()
                        amount_str = row.get(amt_col, '') if amt_col else ''
                        amount = self.parse_amount(amount_str)
                        
                        if description:  # Only process rows with descriptions
                            category = self.categorizer.categorize_transaction(description, amount)
                            transactions.