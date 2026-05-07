```python
"""
Transaction Categorizer

This module reads CSV transaction files, categorizes transactions based on
keyword matching rules, and outputs a new CSV file with categorized data.

The script identifies common spending categories like groceries, gas, restaurants,
utilities, etc. based on transaction descriptions using predefined keyword rules.

Usage:
    python script.py

The script will look for 'transactions.csv' in the current directory and output
'categorized_transactions.csv' with an additional 'Category' column.
"""

import csv
import os
import sys
from datetime import datetime
import re


def load_categorization_rules():
    """Define keyword-based categorization rules for transactions."""
    return {
        'Groceries': [
            'grocery', 'supermarket', 'kroger', 'walmart', 'safeway', 'publix',
            'whole foods', 'trader joe', 'costco', 'sams club', 'aldi', 'food lion',
            'harris teeter', 'giant', 'stop shop', 'wegmans', 'heb', 'meijer'
        ],
        'Gas': [
            'shell', 'exxon', 'chevron', 'bp', 'mobil', 'texaco', 'citgo',
            'valero', 'sunoco', 'phillips 66', 'marathon', 'gas station',
            'fuel', 'petrol'
        ],
        'Restaurants': [
            'restaurant', 'mcdonald', 'burger king', 'subway', 'starbucks',
            'pizza', 'cafe', 'bistro', 'diner', 'food truck', 'fast food',
            'takeout', 'delivery', 'dining', 'bar & grill', 'steakhouse'
        ],
        'Utilities': [
            'electric', 'electricity', 'gas company', 'water', 'sewer',
            'internet', 'cable', 'phone', 'utility', 'power company',
            'energy', 'comcast', 'verizon', 'att', 'spectrum'
        ],
        'Transportation': [
            'uber', 'lyft', 'taxi', 'metro', 'bus', 'train', 'subway',
            'parking', 'toll', 'car wash', 'auto repair', 'mechanic',
            'dmv', 'registration'
        ],
        'Healthcare': [
            'hospital', 'doctor', 'pharmacy', 'cvs', 'walgreens', 'rite aid',
            'medical', 'dentist', 'clinic', 'urgent care', 'prescription',
            'health', 'medicare', 'insurance'
        ],
        'Shopping': [
            'amazon', 'target', 'best buy', 'home depot', 'lowes', 'walmart',
            'mall', 'department store', 'retail', 'online', 'shopping',
            'merchandise', 'clothing', 'electronics'
        ],
        'Entertainment': [
            'movie', 'cinema', 'theater', 'netflix', 'spotify', 'gym',
            'fitness', 'entertainment', 'concert', 'sports', 'game',
            'subscription', 'streaming'
        ],
        'Banking': [
            'bank', 'atm', 'fee', 'interest', 'transfer', 'deposit',
            'withdrawal', 'overdraft', 'service charge'
        ],
        'Insurance': [
            'insurance', 'policy', 'premium', 'coverage', 'claim',
            'geico', 'state farm', 'allstate', 'progressive'
        ]
    }


def categorize_transaction(description, rules):
    """
    Categorize a transaction based on its description using keyword matching.
    
    Args:
        description (str): Transaction description
        rules (dict): Dictionary of category rules
    
    Returns:
        str: Category name or 'Other' if no match found
    """
    if not description:
        return 'Other'
    
    description_lower = description.lower()
    
    # Check each category's keywords
    for category, keywords in rules.items():
        for keyword in keywords:
            if keyword.lower() in description_lower:
                return category
    
    return 'Other'


def parse_amount(amount_str):
    """
    Parse amount string to float, handling various formats.
    
    Args:
        amount_str (str): Amount as string
    
    Returns:
        float: Parsed amount
    """
    if not amount_str:
        return 0.0
    
    # Remove currency symbols and whitespace
    cleaned = re.sub(r'[$,\s]', '', str(amount_str))
    
    # Handle parentheses for negative amounts
    if cleaned.startswith('(') and cleaned.endswith(')'):
        cleaned = '-' + cleaned[1:-1]
    
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def validate_date(date_str):
    """
    Validate and parse date string.
    
    Args:
        date_str (str): Date string to validate
    
    Returns:
        str: Original date string if valid, empty string if invalid
    """
    if not date_str:
        return ''
    
    # Try common date formats
    date_formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']
    
    for fmt in date_formats:
        try:
            datetime.strptime(date_str.strip(), fmt)
            return date_str.strip()
        except ValueError:
            continue
    
    return date_str  # Return original if no format matches


def read_transactions(filename):
    """
    Read transactions from CSV file.
    
    Args:
        filename (str): Path to CSV file
    
    Returns:
        list: List of transaction dictionaries
    """
    transactions = []
    
    try:
        with open(filename, 'r', newline='', encoding='utf-8') as file:
            # Try to detect delimiter
            sample = file.read(1024)
            file.seek(0)
            
            if ',' in sample:
                delimiter = ','
            elif ';' in sample:
                delimiter = ';'
            elif '\t' in sample:
                delimiter = '\t'
            else:
                delimiter = ','
            
            reader = csv.DictReader(file, delimiter=delimiter)
            
            # Try to map common column names
            fieldnames = reader.fieldnames
            if not fieldnames:
                raise ValueError("CSV file has no headers")
            
            # Map field names (case-insensitive)
            field_mapping = {}
            for field in fieldnames:
                field_lower = field.lower().strip()
                if 'date' in field_lower:
                    field_mapping['date'] = field
                elif 'desc' in field_lower or 'transaction' in field_lower:
                    field_mapping['description'] = field
                elif 'amount' in field_lower or 'value' in field_lower:
                    field_mapping['amount'] = field
            
            # If exact mapping not found, use first three columns
            if len(field_mapping) < 3:
                field_mapping = {
                    'date': fieldnames[0],
                    'description': fieldnames[1],
                    'amount': fieldnames[2] if len(fieldnames) > 2 else fieldnames[1]
                }
            
            for row in reader:
                if not any(row.values()):  # Skip empty rows
                    continue
                
                transaction = {
                    'date': validate_date(row.get(field_mapping['date'], '')),
                    'description': row.get(field_mapping['description'], ''),
                    'amount': parse_amount(row.get(field_mapping['amount'], ''))
                }
                transactions.append(transaction)
                
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return []
    except Exception as e:
        print(f"Error reading file '{filename}': {e}")
        return []
    
    return transactions


def write_categorized_transactions(transactions, filename):
    """