```python
#!/usr/bin/env python3
"""
Bank Statement Transaction Categorizer

This module reads CSV bank statements and automatically categorizes transactions
based on keyword matching logic. It parses transaction data including dates,
descriptions, and amounts, then assigns spending categories like groceries,
gas, dining, utilities, etc.

The script is self-contained and uses only standard library modules.
Run with: python script.py

Expected CSV format: date,description,amount
Example: 2024-01-15,WALMART SUPERCENTER,-45.67
"""

import csv
import re
import sys
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Optional


class TransactionCategorizer:
    """Categorizes bank transactions based on description keyword matching."""
    
    def __init__(self):
        """Initialize with predefined spending categories and keywords."""
        self.categories = {
            'groceries': [
                'walmart', 'kroger', 'safeway', 'whole foods', 'trader joe',
                'grocery', 'supermarket', 'food lion', 'publix', 'harris teeter',
                'costco', 'sams club', 'target', 'aldi', 'wegmans'
            ],
            'gas': [
                'shell', 'bp', 'exxon', 'mobil', 'chevron', 'texaco',
                'citgo', 'sunoco', 'speedway', 'wawa', 'gas station',
                'fuel', 'pump', '76', 'marathon'
            ],
            'dining': [
                'restaurant', 'mcdonalds', 'burger king', 'subway', 'starbucks',
                'pizza', 'taco bell', 'kfc', 'wendys', 'chipotle', 'panera',
                'dominos', 'papa johns', 'dunkin', 'cafe', 'bistro', 'grill',
                'bar', 'pub', 'diner', 'food truck'
            ],
            'utilities': [
                'electric', 'gas company', 'water', 'sewer', 'internet',
                'cable', 'phone', 'verizon', 'att', 'comcast', 'spectrum',
                'duke energy', 'pge', 'utility', 'power', 'energy'
            ],
            'entertainment': [
                'netflix', 'hulu', 'spotify', 'apple music', 'amazon prime',
                'disney', 'hbo', 'movie', 'theater', 'cinema', 'concert',
                'ticket', 'gaming', 'steam', 'xbox', 'playstation'
            ],
            'shopping': [
                'amazon', 'ebay', 'best buy', 'home depot', 'lowes',
                'macys', 'nordstrom', 'kohls', 'jcpenney', 'tj maxx',
                'marshall', 'clothing', 'apparel', 'shoes'
            ],
            'healthcare': [
                'pharmacy', 'cvs', 'walgreens', 'rite aid', 'doctor',
                'medical', 'hospital', 'clinic', 'dentist', 'health',
                'prescription', 'medicine'
            ],
            'transportation': [
                'uber', 'lyft', 'taxi', 'bus', 'train', 'metro', 'parking',
                'toll', 'car wash', 'auto', 'mechanic', 'tire', 'oil change'
            ],
            'banking': [
                'bank', 'atm', 'fee', 'interest', 'transfer', 'deposit',
                'withdrawal', 'overdraft', 'maintenance'
            ]
        }
    
    def categorize_transaction(self, description: str) -> str:
        """
        Categorize a transaction based on its description.
        
        Args:
            description: Transaction description string
            
        Returns:
            Category name or 'other' if no match found
        """
        description_lower = description.lower()
        
        # Remove common non-descriptive words
        cleaned_desc = re.sub(r'\b(inc|llc|corp|ltd|co|#\d+|\d{2}/\d{2})\b', '', description_lower)
        
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in cleaned_desc:
                    return category
        
        return 'other'
    
    def parse_amount(self, amount_str: str) -> float:
        """
        Parse amount string to float, handling various formats.
        
        Args:
            amount_str: Amount as string (may include currency symbols, commas)
            
        Returns:
            Amount as float
        """
        # Remove currency symbols and commas
        cleaned = re.sub(r'[$,]', '', amount_str.strip())
        
        # Handle parentheses as negative (accounting format)
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
            date_str: Date string in various formats
            
        Returns:
            datetime object or None if parsing fails
        """
        date_formats = [
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%m/%d/%y',
            '%d/%m/%Y',
            '%Y/%m/%d'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        return None
    
    def process_csv(self, filename: str) -> List[Dict]:
        """
        Process CSV file and categorize transactions.
        
        Args:
            filename: Path to CSV file
            
        Returns:
            List of processed transaction dictionaries
        """
        transactions = []
        
        try:
            with open(filename, 'r', newline='', encoding='utf-8') as file:
                # Try to detect delimiter
                sample = file.read(1024)
                file.seek(0)
                
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.reader(file, delimiter=delimiter)
                
                # Skip header if present
                first_row = next(reader, None)
                if first_row and any(header in first_row[0].lower() for header in ['date', 'description', 'amount']):
                    pass  # Header row, continue with next row
                else:
                    # First row is data, process it
                    file.seek(0)
                    reader = csv.reader(file, delimiter=delimiter)
                
                for row_num, row in enumerate(reader, 1):
                    if len(row) < 3:
                        print(f"Warning: Row {row_num} has insufficient columns: {row}")
                        continue
                    
                    try:
                        date_str, description, amount_str = row[0], row[1], row[2]
                        
                        parsed_date = self.parse_date(date_str)
                        amount = self.parse_amount(amount_str)
                        category = self.categorize_transaction(description)
                        
                        transaction = {
                            'row': row_num,
                            'date': parsed_date,
                            'date_str': date_str,
                            'description': description.strip(),
                            'amount': amount,
                            'amount_str': amount_str,
                            'category': category
                        }
                        
                        transactions.append(transaction)
                        
                    except Exception as e:
                        print(f"Error processing row {row_num}: {row} - {e}")
                        continue
        
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
            return []
        except Exception as e:
            print(f"Error reading file '{filename}':