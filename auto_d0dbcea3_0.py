```python
#!/usr/bin/env python3
"""
Transaction Categorizer and Spending Analyzer

This module reads CSV files containing transaction data, categorizes transactions
using keyword matching against predefined categories, and calculates total
spending by category. It provides a simple way to analyze personal or business
spending patterns from bank statements or financial exports.

The script expects CSV files with columns for transaction descriptions and amounts.
It uses keyword matching to automatically categorize transactions into predefined
categories like groceries, dining, transportation, etc.

Usage: python script.py
"""

import csv
import sys
import os
from collections import defaultdict
from typing import Dict, List, Tuple


# Predefined categories with keywords for matching
CATEGORY_KEYWORDS = {
    'groceries': ['grocery', 'supermarket', 'walmart', 'target', 'kroger', 'safeway', 'whole foods', 'trader joe'],
    'dining': ['restaurant', 'cafe', 'pizza', 'starbucks', 'mcdonald', 'burger', 'diner', 'food', 'eat'],
    'transportation': ['gas', 'fuel', 'uber', 'lyft', 'taxi', 'metro', 'bus', 'parking', 'toll'],
    'utilities': ['electric', 'gas bill', 'water', 'internet', 'phone', 'cable', 'utility'],
    'entertainment': ['movie', 'netflix', 'spotify', 'theater', 'concert', 'game', 'streaming'],
    'shopping': ['amazon', 'ebay', 'store', 'mall', 'purchase', 'retail'],
    'healthcare': ['doctor', 'hospital', 'pharmacy', 'medical', 'dental', 'clinic'],
    'banking': ['fee', 'interest', 'transfer', 'atm', 'bank'],
    'other': []  # Default category for unmatched transactions
}


def categorize_transaction(description: str) -> str:
    """
    Categorize a transaction based on its description using keyword matching.
    
    Args:
        description (str): Transaction description to categorize
        
    Returns:
        str: Category name that best matches the description
    """
    description_lower = description.lower()
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        if category == 'other':
            continue
        for keyword in keywords:
            if keyword in description_lower:
                return category
    
    return 'other'


def parse_amount(amount_str: str) -> float:
    """
    Parse amount string and convert to float, handling various formats.
    
    Args:
        amount_str (str): Amount string that may contain currency symbols
        
    Returns:
        float: Parsed amount as a float
        
    Raises:
        ValueError: If amount cannot be parsed
    """
    try:
        # Remove common currency symbols and whitespace
        cleaned = amount_str.strip().replace('$', '').replace(',', '').replace('€', '').replace('£', '')
        
        # Handle negative amounts in parentheses (accounting format)
        if cleaned.startswith('(') and cleaned.endswith(')'):
            cleaned = '-' + cleaned[1:-1]
        
        return float(cleaned)
    except ValueError:
        raise ValueError(f"Unable to parse amount: {amount_str}")


def read_csv_file(filepath: str) -> List[Dict[str, str]]:
    """
    Read CSV file and return list of transaction dictionaries.
    
    Args:
        filepath (str): Path to the CSV file
        
    Returns:
        List[Dict[str, str]]: List of transaction records
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If CSV format is invalid
    """
    transactions = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            # Try to detect delimiter
            sample = file.read(1024)
            file.seek(0)
            
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
            reader = csv.DictReader(file, delimiter=delimiter)
            
            for row_num, row in enumerate(reader, start=2):
                if row:  # Skip empty rows
                    transactions.append(row)
                    
        return transactions
        
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file not found: {filepath}")
    except csv.Error as e:
        raise ValueError(f"Error reading CSV file: {e}")


def find_amount_description_columns(headers: List[str]) -> Tuple[str, str]:
    """
    Automatically detect amount and description columns from CSV headers.
    
    Args:
        headers (List[str]): List of column headers
        
    Returns:
        Tuple[str, str]: (description_column, amount_column)
        
    Raises:
        ValueError: If required columns cannot be identified
    """
    description_col = None
    amount_col = None
    
    # Common column names for descriptions
    desc_keywords = ['description', 'desc', 'memo', 'details', 'transaction', 'merchant']
    # Common column names for amounts
    amount_keywords = ['amount', 'value', 'debit', 'credit', 'total', 'sum']
    
    headers_lower = [h.lower() for h in headers]
    
    # Find description column
    for keyword in desc_keywords:
        for i, header in enumerate(headers_lower):
            if keyword in header:
                description_col = headers[i]
                break
        if description_col:
            break
    
    # Find amount column
    for keyword in amount_keywords:
        for i, header in enumerate(headers_lower):
            if keyword in header:
                amount_col = headers[i]
                break
        if amount_col:
            break
    
    if not description_col or not amount_col:
        raise ValueError(f"Could not identify description and amount columns from: {headers}")
    
    return description_col, amount_col


def process_transactions(transactions: List[Dict[str, str]]) -> Dict[str, float]:
    """
    Process transactions and calculate spending totals by category.
    
    Args:
        transactions (List[Dict[str, str]]): List of transaction records
        
    Returns:
        Dict[str, float]: Dictionary mapping categories to total spending
    """
    if not transactions:
        return {}
    
    # Auto-detect columns
    headers = list(transactions[0].keys())
    description_col, amount_col = find_amount_description_columns(headers)
    
    category_totals = defaultdict(float)
    processed_count = 0
    error_count = 0
    
    for transaction in transactions:
        try:
            description = transaction.get(description_col, '').strip()
            amount_str = transaction.get(amount_col, '').strip()
            
            if not description or not amount_str:
                continue
            
            amount = parse_amount(amount_str)
            category = categorize_transaction(description)
            
            # Only count expenses (negative amounts or positive amounts as expenses)
            expense_amount = abs(amount)
            category_totals[category] += expense_amount
            processed_count += 1
            
        except (ValueError, KeyError) as e:
            error_count += 1
            print(f"Warning: Skipped transaction due to error: {e}", file=sys.stderr)
    
    print(f"\nProcessed {processed_count} transactions successfully.")
    if error_count > 0:
        print(f"Skipped {error_count} transactions due to errors.")
    
    return dict(category_totals)


def create_sample_csv():
    """Create a sample CSV file for demonstration purposes."""
    sample_data = [
        ['Date', 'Description', 'Amount'],
        ['2024-01-01', 'Whole Foods Market', '-156.78'],
        ['2024-01-02', 'Shell Gas Station', '-45.23'],
        ['2024-01-03', 'Netflix Subscription', '-15.99'],
        ['2024-01-04', 'Amazon Purchase', '-89.45'],
        ['2024-01-05', 'Starbucks Coffee', '-12.50'],