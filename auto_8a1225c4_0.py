```python
#!/usr/bin/env python3
"""
Bank Transaction Categorizer

This module reads CSV bank export files and automatically categorizes transactions
using regex patterns. It extracts transaction data (date, amount, description, merchant)
and classifies them into predefined categories like groceries, dining, transportation,
utilities, and entertainment.

Usage: python script.py

The script will look for CSV files in the current directory with common bank export
column names and process them automatically.
"""

import csv
import re
import os
import sys
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class TransactionCategorizer:
    def __init__(self):
        # Define category patterns using regex
        self.category_patterns = {
            'groceries': [
                r'\b(walmart|kroger|safeway|whole foods|trader joe|costco|sam\'s club)\b',
                r'\b(grocery|supermarket|market|food mart)\b',
                r'\b(aldi|publix|wegmans|harris teeter|giant eagle)\b'
            ],
            'dining': [
                r'\b(restaurant|cafe|bistro|grill|pizza|burger)\b',
                r'\b(mcdonald|burger king|subway|starbucks|dunkin)\b',
                r'\b(dining|takeout|delivery|doordash|uber eats|grubhub)\b',
                r'\b(bar|pub|tavern|brewery)\b'
            ],
            'transportation': [
                r'\b(gas|gasoline|fuel|exxon|shell|bp|chevron|mobil)\b',
                r'\b(uber|lyft|taxi|cab)\b',
                r'\b(parking|metro|transit|bus|train|airline)\b',
                r'\b(car wash|auto|mechanic|repair)\b'
            ],
            'utilities': [
                r'\b(electric|electricity|power|energy)\b',
                r'\b(water|sewer|waste|garbage)\b',
                r'\b(phone|mobile|cellular|internet|cable|wifi)\b',
                r'\b(utility|utilities|bill payment)\b'
            ],
            'entertainment': [
                r'\b(movie|cinema|theater|netflix|spotify|hulu)\b',
                r'\b(game|gaming|steam|xbox|playstation)\b',
                r'\b(concert|show|event|ticket)\b',
                r'\b(gym|fitness|sports|recreation)\b'
            ],
            'healthcare': [
                r'\b(doctor|medical|hospital|pharmacy|cvs|walgreens)\b',
                r'\b(dental|dentist|health|clinic)\b',
                r'\b(prescription|medicine|drug)\b'
            ],
            'shopping': [
                r'\b(amazon|target|best buy|home depot|lowes)\b',
                r'\b(clothing|apparel|shoes|fashion)\b',
                r'\b(electronics|computer|phone store)\b'
            ],
            'financial': [
                r'\b(bank|atm|fee|interest|transfer)\b',
                r'\b(credit card|loan|mortgage|insurance)\b',
                r'\b(investment|trading|broker)\b'
            ]
        }

    def categorize_transaction(self, description: str, merchant: str = "") -> str:
        """
        Categorize a transaction based on description and merchant name.
        
        Args:
            description: Transaction description
            merchant: Merchant name (optional)
            
        Returns:
            Category name or 'uncategorized' if no match found
        """
        text = f"{description} {merchant}".lower()
        
        for category, patterns in self.category_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return category
        
        return 'uncategorized'

    def detect_csv_format(self, filepath: str) -> Optional[Dict[str, int]]:
        """
        Detect the CSV format and return column mappings.
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            Dictionary mapping field names to column indices, or None if format not recognized
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                # Read first few lines to detect format
                sample = file.read(1024)
                file.seek(0)
                
                # Try to detect dialect
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.reader(file, delimiter=delimiter)
                header = next(reader, None)
                
                if not header:
                    return None
                
                # Convert to lowercase for matching
                header_lower = [col.lower().strip() for col in header]
                
                # Define possible column name variations
                date_cols = ['date', 'transaction date', 'posted date', 'trans date']
                amount_cols = ['amount', 'transaction amount', 'debit', 'credit', 'withdrawal', 'deposit']
                desc_cols = ['description', 'transaction description', 'memo', 'details']
                merchant_cols = ['merchant', 'payee', 'vendor', 'company']
                
                column_map = {}
                
                # Find column indices
                for i, col in enumerate(header_lower):
                    if any(date_col in col for date_col in date_cols):
                        column_map['date'] = i
                    elif any(amt_col in col for amt_col in amount_cols):
                        column_map['amount'] = i
                    elif any(desc_col in col for desc_col in desc_cols):
                        column_map['description'] = i
                    elif any(merch_col in col for merch_col in merchant_cols):
                        column_map['merchant'] = i
                
                # Ensure we have at least date, amount, and description
                if len(column_map) >= 3 and 'date' in column_map and 'amount' in column_map:
                    return column_map
                
                return None
                
        except Exception as e:
            print(f"Error detecting CSV format for {filepath}: {str(e)}")
            return None

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
        
        # Remove currency symbols, commas, and whitespace
        cleaned = re.sub(r'[$,\s]', '', str(amount_str))
        
        # Handle parentheses for negative amounts
        if cleaned.startswith('(') and cleaned.endswith(')'):
            cleaned = '-' + cleaned[1:-1]
        
        try:
            return float(cleaned)
        except ValueError:
            return 0.0

    def parse_date(self, date_str: str) -> str:
        """
        Parse date string to standardized format.
        
        Args:
            date_str: Date as string
            
        Returns:
            Date in YYYY-MM-DD format
        """
        if not date_str:
            return ""
        
        # Common date formats
        date_formats = [
            '%Y-%m-%d', '%m/%d/%Y', '%m-%d-%Y', '%d/%m/%Y', '%d-%m-%Y',
            '%Y/%m/%d', '%m/%d/%y', '%m-%d-%y', '%d/%m/%y', '%d-%m-%y'
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str.strip(), fmt)
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        return date_str  # Return original if parsing fails

    def process_csv_file(self, filepath: str) -> List[Dict]:
        """
        Process a CSV file and extract categorized transactions.
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            List of transaction dictionaries
        """
        column_map = self.detect_csv_format