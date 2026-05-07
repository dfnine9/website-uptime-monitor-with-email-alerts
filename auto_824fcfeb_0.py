```python
#!/usr/bin/env python3
"""
Bank Statement Transaction Categorizer

This module parses CSV bank statements and automatically categorizes transactions
based on configurable keyword dictionaries. It reads transaction data from a CSV file,
applies category rules based on transaction descriptions, and outputs a new CSV file
with an additional category column.

Features:
- Configurable keyword-based categorization
- Support for multiple CSV formats (auto-detection of common column names)
- Comprehensive error handling
- Detailed transaction categorization reporting
- Self-contained with minimal dependencies

Usage:
    python script.py

The script will look for 'bank_statements.csv' in the current directory and output
'categorized_statements.csv' with added category information.
"""

import csv
import re
import sys
from typing import Dict, List, Tuple, Optional
from pathlib import Path


class TransactionCategorizer:
    """Categorizes bank transactions based on configurable keyword dictionaries."""
    
    def __init__(self):
        """Initialize the categorizer with default category keywords."""
        self.category_keywords = {
            'groceries': [
                'walmart', 'target', 'safeway', 'kroger', 'publix', 'whole foods',
                'trader joes', 'costco', 'sams club', 'aldi', 'food lion',
                'harris teeter', 'giant', 'stop shop', 'wegmans', 'meijer',
                'grocery', 'supermarket', 'market', 'fresh', 'organic'
            ],
            'utilities': [
                'electric', 'electricity', 'gas', 'water', 'sewer', 'trash',
                'internet', 'cable', 'phone', 'utility', 'power', 'energy',
                'comcast', 'verizon', 'att', 'spectrum', 'xfinity'
            ],
            'entertainment': [
                'netflix', 'spotify', 'hulu', 'disney', 'amazon prime', 'youtube',
                'movie', 'theater', 'cinema', 'concert', 'event', 'ticket',
                'entertainment', 'streaming', 'music', 'game', 'gaming'
            ],
            'restaurants': [
                'restaurant', 'cafe', 'coffee', 'starbucks', 'mcdonalds', 'subway',
                'pizza', 'burger', 'taco', 'chinese', 'thai', 'italian',
                'dining', 'food delivery', 'doordash', 'uber eats', 'grubhub'
            ],
            'transportation': [
                'gas station', 'fuel', 'gasoline', 'shell', 'exxon', 'bp', 'chevron',
                'uber', 'lyft', 'taxi', 'bus', 'metro', 'parking', 'toll',
                'car payment', 'insurance', 'auto', 'vehicle'
            ],
            'shopping': [
                'amazon', 'ebay', 'store', 'shop', 'retail', 'clothing',
                'shoes', 'electronics', 'home depot', 'lowes', 'best buy',
                'macys', 'nordstrom', 'department'
            ],
            'healthcare': [
                'medical', 'doctor', 'hospital', 'pharmacy', 'cvs', 'walgreens',
                'health', 'dental', 'vision', 'clinic', 'urgent care'
            ],
            'banking': [
                'atm', 'fee', 'transfer', 'deposit', 'withdrawal', 'interest',
                'bank', 'credit card', 'loan', 'mortgage'
            ]
        }
    
    def add_category(self, category: str, keywords: List[str]) -> None:
        """Add or update a category with new keywords."""
        if category in self.category_keywords:
            self.category_keywords[category].extend(keywords)
        else:
            self.category_keywords[category] = keywords
    
    def categorize_transaction(self, description: str, amount: float = None) -> str:
        """
        Categorize a transaction based on its description.
        
        Args:
            description: Transaction description text
            amount: Transaction amount (optional, for future enhancements)
            
        Returns:
            Category name or 'uncategorized' if no match found
        """
        if not description:
            return 'uncategorized'
        
        description_lower = description.lower()
        
        # Check each category's keywords
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if re.search(r'\b' + re.escape(keyword.lower()) + r'\b', description_lower):
                    return category
        
        return 'uncategorized'


class CSVParser:
    """Handles CSV file parsing and writing operations."""
    
    COMMON_AMOUNT_COLUMNS = ['amount', 'transaction_amount', 'debit', 'credit', 'value']
    COMMON_DESCRIPTION_COLUMNS = ['description', 'memo', 'transaction_description', 'details', 'reference']
    COMMON_DATE_COLUMNS = ['date', 'transaction_date', 'posted_date', 'effective_date']
    
    @staticmethod
    def detect_columns(headers: List[str]) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Auto-detect column names for date, description, and amount.
        
        Returns:
            Tuple of (date_column, description_column, amount_column)
        """
        headers_lower = [h.lower() for h in headers]
        
        date_col = None
        desc_col = None
        amount_col = None
        
        # Find date column
        for col in CSVParser.COMMON_DATE_COLUMNS:
            if col in headers_lower:
                date_col = headers[headers_lower.index(col)]
                break
        
        # Find description column
        for col in CSVParser.COMMON_DESCRIPTION_COLUMNS:
            if col in headers_lower:
                desc_col = headers[headers_lower.index(col)]
                break
        
        # Find amount column
        for col in CSVParser.COMMON_AMOUNT_COLUMNS:
            if col in headers_lower:
                amount_col = headers[headers_lower.index(col)]
                break
        
        return date_col, desc_col, amount_col
    
    @staticmethod
    def parse_amount(amount_str: str) -> float:
        """Parse amount string to float, handling various formats."""
        if not amount_str:
            return 0.0
        
        # Remove currency symbols and whitespace
        cleaned = re.sub(r'[$,\s]', '', str(amount_str))
        
        try:
            return float(cleaned)
        except (ValueError, TypeError):
            return 0.0


def main():
    """Main function to run the transaction categorization process."""
    input_file = 'bank_statements.csv'
    output_file = 'categorized_statements.csv'
    
    print("Bank Statement Transaction Categorizer")
    print("=" * 40)
    
    # Check if input file exists
    if not Path(input_file).exists():
        print(f"Error: Input file '{input_file}' not found.")
        print("Please ensure your bank statement CSV file is named 'bank_statements.csv'")
        print("and is located in the current directory.")
        return 1
    
    categorizer = TransactionCategorizer()
    category_counts = {}
    processed_count = 0
    error_count = 0
    
    try:
        # Read and process the CSV file
        with open(input_file, 'r', newline='', encoding='utf-8') as infile:
            # Detect delimiter
            sample = infile.read(1024)
            infile.seek(0)
            
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
            reader = csv.DictReader(infile, delimiter=delimiter)
            headers = reader.fieldnames
            
            if not headers:
                print("Error: Could not read headers from CSV file.")
                return 1