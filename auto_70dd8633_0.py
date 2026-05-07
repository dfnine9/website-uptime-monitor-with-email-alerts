```python
#!/usr/bin/env python3
"""
Bank Statement Expense Categorizer

This module reads CSV bank statements and automatically categorizes transactions
based on description keyword matching. It processes transaction descriptions
against predefined category mappings to assign appropriate expense categories.

Features:
- Reads CSV files with bank transaction data
- Automatically categorizes expenses using keyword matching
- Supports customizable category definitions
- Handles various CSV formats and missing data
- Provides summary statistics by category

Usage:
    python script.py

The script expects a CSV file named 'bank_statement.csv' in the same directory
with columns: Date, Description, Amount (negative for expenses)
"""

import csv
import re
from typing import Dict, List, Tuple
from datetime import datetime


class ExpenseCategorizer:
    """Categorizes bank transactions based on description keywords."""
    
    def __init__(self):
        """Initialize with predefined category mappings."""
        self.categories = {
            'groceries': [
                'walmart', 'target', 'kroger', 'safeway', 'whole foods', 'trader joe',
                'costco', 'sam\'s club', 'grocery', 'supermarket', 'food mart',
                'aldi', 'publix', 'wegmans', 'harris teeter', 'giant', 'stop shop'
            ],
            'utilities': [
                'electric', 'gas', 'water', 'sewer', 'trash', 'internet', 'cable',
                'phone', 'wireless', 'verizon', 'at&t', 'comcast', 'spectrum',
                'utility', 'power', 'energy'
            ],
            'entertainment': [
                'netflix', 'spotify', 'hulu', 'disney', 'amazon prime', 'movie',
                'theater', 'cinema', 'concert', 'spotify', 'apple music',
                'youtube', 'gaming', 'steam', 'entertainment'
            ],
            'restaurants': [
                'restaurant', 'cafe', 'coffee', 'starbucks', 'mcdonald', 'burger',
                'pizza', 'subway', 'chipotle', 'taco bell', 'kfc', 'wendy',
                'dining', 'food', 'bar', 'grill', 'bistro'
            ],
            'transportation': [
                'gas station', 'shell', 'exxon', 'bp', 'chevron', 'mobil', 'uber',
                'lyft', 'taxi', 'bus', 'train', 'metro', 'parking', 'toll',
                'auto', 'car wash', 'fuel'
            ],
            'shopping': [
                'amazon', 'ebay', 'mall', 'store', 'retail', 'shop', 'clothing',
                'apparel', 'shoes', 'electronics', 'best buy', 'home depot',
                'lowe\'s', 'macy\'s', 'nordstrom'
            ],
            'healthcare': [
                'pharmacy', 'cvs', 'walgreens', 'doctor', 'medical', 'hospital',
                'clinic', 'dentist', 'insurance', 'prescription', 'health'
            ],
            'banking': [
                'atm fee', 'bank fee', 'overdraft', 'transfer', 'wire', 'check',
                'deposit', 'withdrawal', 'interest', 'maintenance'
            ]
        }
    
    def categorize_transaction(self, description: str) -> str:
        """
        Categorize a transaction based on its description.
        
        Args:
            description: Transaction description text
            
        Returns:
            Category name or 'uncategorized' if no match found
        """
        if not description:
            return 'uncategorized'
        
        description_lower = description.lower()
        
        # Check each category for keyword matches
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword.lower() in description_lower:
                    return category
        
        return 'uncategorized'


def read_bank_statement(filename: str) -> List[Dict]:
    """
    Read bank statement CSV file and return list of transactions.
    
    Args:
        filename: Path to CSV file
        
    Returns:
        List of transaction dictionaries
        
    Raises:
        FileNotFoundError: If CSV file doesn't exist
        ValueError: If CSV format is invalid
    """
    transactions = []
    
    try:
        with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
            # Try to detect delimiter
            sample = csvfile.read(1024)
            csvfile.seek(0)
            
            delimiter = ','
            if ';' in sample and sample.count(';') > sample.count(','):
                delimiter = ';'
            
            reader = csv.DictReader(csvfile, delimiter=delimiter)
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    # Handle various column name formats
                    date_col = None
                    desc_col = None
                    amount_col = None
                    
                    # Find appropriate columns (case-insensitive)
                    for col in row.keys():
                        col_lower = col.lower().strip()
                        if 'date' in col_lower:
                            date_col = col
                        elif any(word in col_lower for word in ['description', 'desc', 'memo', 'detail']):
                            desc_col = col
                        elif any(word in col_lower for word in ['amount', 'debit', 'credit', 'transaction']):
                            amount_col = col
                    
                    if not all([date_col, desc_col, amount_col]):
                        raise ValueError(f"Required columns not found. Available: {list(row.keys())}")
                    
                    # Parse transaction data
                    date_str = row[date_col].strip()
                    description = row[desc_col].strip()
                    amount_str = row[amount_col].strip()
                    
                    # Skip empty rows
                    if not any([date_str, description, amount_str]):
                        continue
                    
                    # Parse amount (handle various formats)
                    amount_str = re.sub(r'[,$]', '', amount_str)
                    if amount_str.startswith('(') and amount_str.endswith(')'):
                        amount_str = '-' + amount_str[1:-1]
                    
                    try:
                        amount = float(amount_str)
                    except ValueError:
                        print(f"Warning: Invalid amount '{amount_str}' on row {row_num}, skipping")
                        continue
                    
                    # Parse date
                    try:
                        # Try common date formats
                        for date_format in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%m-%d-%Y']:
                            try:
                                parsed_date = datetime.strptime(date_str, date_format)
                                break
                            except ValueError:
                                continue
                        else:
                            print(f"Warning: Invalid date '{date_str}' on row {row_num}, using raw string")
                            parsed_date = date_str
                    except Exception:
                        parsed_date = date_str
                    
                    transactions.append({
                        'date': parsed_date,
                        'description': description,
                        'amount': amount
                    })
                    
                except Exception as e:
                    print(f"Warning: Error processing row {row_num}: {e}")
                    continue
                    
    except FileNotFoundError:
        raise FileNotFoundError(f"Bank statement file '{filename}' not found")
    except Exception as e:
        raise ValueError(f"Error reading CSV file: {e}")
    
    return transactions


def create_sample_csv():
    """Create a sample bank statement CSV for demonstration."""
    sample_data = [
        ['Date', 'Description', 'Amount'],
        ['2024-01-01', 'WALMART SUPERCENTER', '-85.43'],
        ['2024-01-02', 'ST