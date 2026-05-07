```python
"""
CSV Transaction Categorizer

This script reads CSV transaction files and categorizes expenses based on keyword matching.
It parses transaction data (date, description, amount) and applies predefined categorization
rules using dictionaries for common expense categories.

Categories supported:
- Groceries
- Utilities  
- Entertainment
- Dining
- Transportation
- Healthcare
- Shopping
- Other (uncategorized)

Usage: python script.py
"""

import csv
import re
from datetime import datetime
from collections import defaultdict
import os

# Categorization rules - keywords mapped to categories
CATEGORY_RULES = {
    'groceries': [
        'grocery', 'supermarket', 'market', 'food store', 'walmart', 'target',
        'kroger', 'safeway', 'whole foods', 'trader joe', 'costco', 'sams club'
    ],
    'utilities': [
        'electric', 'gas', 'water', 'sewer', 'internet', 'phone', 'cable',
        'utility', 'power', 'energy', 'comcast', 'verizon', 'att'
    ],
    'entertainment': [
        'netflix', 'spotify', 'hulu', 'disney', 'amazon prime', 'movie',
        'theater', 'cinema', 'concert', 'game', 'steam', 'entertainment'
    ],
    'dining': [
        'restaurant', 'cafe', 'coffee', 'pizza', 'burger', 'fast food',
        'starbucks', 'mcdonalds', 'subway', 'chipotle', 'dining', 'food delivery',
        'doordash', 'ubereats', 'grubhub'
    ],
    'transportation': [
        'gas station', 'fuel', 'uber', 'lyft', 'taxi', 'parking', 'metro',
        'bus', 'train', 'airline', 'car rental', 'auto', 'mechanic'
    ],
    'healthcare': [
        'pharmacy', 'doctor', 'hospital', 'medical', 'dental', 'clinic',
        'cvs', 'walgreens', 'health', 'prescription', 'insurance'
    ],
    'shopping': [
        'amazon', 'ebay', 'store', 'mall', 'clothing', 'shoes', 'electronics',
        'best buy', 'apple store', 'retail', 'shop'
    ]
}

def categorize_transaction(description):
    """
    Categorize a transaction based on its description using keyword matching.
    
    Args:
        description (str): Transaction description
        
    Returns:
        str: Category name or 'other' if no match found
    """
    description_lower = description.lower()
    
    for category, keywords in CATEGORY_RULES.items():
        for keyword in keywords:
            if keyword in description_lower:
                return category
    
    return 'other'

def parse_date(date_str):
    """
    Parse date string in various common formats.
    
    Args:
        date_str (str): Date string to parse
        
    Returns:
        datetime: Parsed date object or None if parsing fails
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

def parse_amount(amount_str):
    """
    Parse amount string, handling various formats including currency symbols.
    
    Args:
        amount_str (str): Amount string to parse
        
    Returns:
        float: Parsed amount or 0.0 if parsing fails
    """
    try:
        # Remove currency symbols, commas, and whitespace
        cleaned = re.sub(r'[\$,\s]', '', amount_str.strip())
        # Handle negative amounts in parentheses
        if cleaned.startswith('(') and cleaned.endswith(')'):
            cleaned = '-' + cleaned[1:-1]
        return float(cleaned)
    except (ValueError, AttributeError):
        return 0.0

def read_csv_transactions(filename):
    """
    Read and parse transactions from CSV file.
    
    Args:
        filename (str): Path to CSV file
        
    Returns:
        list: List of transaction dictionaries
    """
    transactions = []
    
    try:
        with open(filename, 'r', newline='', encoding='utf-8') as file:
            # Try to detect header automatically
            sample = file.read(1024)
            file.seek(0)
            
            # Common CSV dialects
            try:
                dialect = csv.Sniffer().sniff(sample)
                reader = csv.reader(file, dialect)
            except csv.Error:
                reader = csv.reader(file)
            
            rows = list(reader)
            
            if not rows:
                print(f"Warning: {filename} is empty")
                return transactions
            
            # Assume first row might be header, check if it contains typical header words
            header_indicators = ['date', 'description', 'amount', 'transaction', 'debit', 'credit']
            first_row_lower = [cell.lower() for cell in rows[0]]
            has_header = any(indicator in ' '.join(first_row_lower) for indicator in header_indicators)
            
            start_row = 1 if has_header else 0
            
            for i, row in enumerate(rows[start_row:], start_row + 1):
                if len(row) < 3:
                    print(f"Warning: Row {i} has insufficient columns, skipping")
                    continue
                
                # Assume order: date, description, amount (common format)
                date_str = row[0]
                description = row[1]
                amount_str = row[2]
                
                # Parse components
                parsed_date = parse_date(date_str)
                amount = parse_amount(amount_str)
                category = categorize_transaction(description)
                
                transaction = {
                    'row': i,
                    'date_raw': date_str,
                    'date_parsed': parsed_date,
                    'description': description,
                    'amount_raw': amount_str,
                    'amount': amount,
                    'category': category
                }
                
                transactions.append(transaction)
                
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
    except PermissionError:
        print(f"Error: Permission denied reading '{filename}'")
    except Exception as e:
        print(f"Error reading '{filename}': {str(e)}")
    
    return transactions

def analyze_transactions(transactions):
    """
    Analyze transactions and generate summary statistics.
    
    Args:
        transactions (list): List of transaction dictionaries
        
    Returns:
        dict: Analysis results
    """
    if not transactions:
        return {}
    
    category_totals = defaultdict(float)
    category_counts = defaultdict(int)
    total_amount = 0
    valid_dates = 0
    
    for transaction in transactions:
        category = transaction['category']
        amount = transaction['amount']
        
        category_totals[category] += amount
        category_counts[category] += 1
        total_amount += amount
        
        if transaction['date_parsed']:
            valid_dates += 1
    
    return {
        'total_transactions': len(transactions),
        'total_amount': total_amount,
        'valid_dates': valid_dates,
        'category_totals': dict(category_totals),
        'category_counts': dict(category_counts)
    }

def print_results(transactions, analysis, filename):
    """
    Print analysis results to stdout.
    
    Args:
        transactions (list): List of transactions
        analysis (dict): Analysis results
        filename (str): Source filename
    """
    print(f"\n{'='*60}")
    print(f"TRANSACTION ANALYSIS REPORT")