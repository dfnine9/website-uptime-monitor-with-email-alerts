```python
#!/usr/bin/env python3
"""
Bank Statement Transaction Categorizer

This script reads CSV bank statement files and automatically categorizes transactions
into predefined spending categories using regex patterns and keyword matching.

The script processes transaction descriptions and amounts to classify spending into
categories like groceries, utilities, entertainment, dining, transportation, etc.
It then outputs summary totals for each category.

Usage: python script.py

The script expects CSV files with columns: date, description, amount
Place your CSV files in the same directory as this script.
"""

import csv
import re
import os
import glob
from collections import defaultdict
from typing import Dict, List, Tuple


def load_categorization_rules() -> Dict[str, List[str]]:
    """Define categorization rules with keywords and patterns for each category."""
    return {
        'groceries': [
            'walmart', 'target', 'kroger', 'safeway', 'whole foods', 'trader joe',
            'costco', 'sams club', 'grocery', 'market', 'food lion', 'publix',
            'aldi', 'wegmans', 'harris teeter', 'giant', 'stop shop', 'acme'
        ],
        'utilities': [
            'electric', 'gas', 'water', 'sewer', 'internet', 'cable', 'phone',
            'verizon', 'att', 'comcast', 'xfinity', 'spectrum', 'cox',
            'utility', 'power', 'energy', 'pg&e', 'con ed', 'duke energy'
        ],
        'entertainment': [
            'netflix', 'hulu', 'spotify', 'amazon prime', 'disney', 'hbo',
            'movie', 'theater', 'cinema', 'concert', 'ticket', 'games',
            'steam', 'xbox', 'playstation', 'entertainment', 'streaming'
        ],
        'dining': [
            'restaurant', 'cafe', 'coffee', 'starbucks', 'mcdonalds', 'burger',
            'pizza', 'subway', 'kfc', 'taco bell', 'chipotle', 'panera',
            'dining', 'food delivery', 'doordash', 'uber eats', 'grubhub'
        ],
        'transportation': [
            'gas station', 'shell', 'exxon', 'chevron', 'bp', 'mobil',
            'uber', 'lyft', 'taxi', 'bus', 'train', 'metro', 'parking',
            'toll', 'car wash', 'auto', 'vehicle', 'insurance'
        ],
        'shopping': [
            'amazon', 'ebay', 'best buy', 'home depot', 'lowes', 'walmart',
            'target', 'macys', 'nordstrom', 'clothing', 'retail', 'store'
        ],
        'healthcare': [
            'pharmacy', 'cvs', 'walgreens', 'doctor', 'medical', 'hospital',
            'dentist', 'clinic', 'health', 'prescription', 'medicine'
        ],
        'banking': [
            'atm', 'fee', 'overdraft', 'transfer', 'interest', 'maintenance',
            'service charge', 'wire', 'check', 'deposit'
        ],
        'income': [
            'payroll', 'salary', 'deposit', 'refund', 'credit', 'payment received',
            'dividend', 'interest earned', 'bonus', 'reimbursement'
        ]
    }


def categorize_transaction(description: str, amount: float, rules: Dict[str, List[str]]) -> str:
    """
    Categorize a transaction based on its description and amount.
    
    Args:
        description: Transaction description
        amount: Transaction amount (positive for credits, negative for debits)
        rules: Dictionary of category rules
    
    Returns:
        Category name or 'other' if no match found
    """
    description_lower = description.lower()
    
    # Handle income (positive amounts)
    if amount > 0:
        for keyword in rules['income']:
            if keyword in description_lower:
                return 'income'
        return 'income'  # Default positive amounts to income
    
    # Handle expenses (negative amounts)
    for category, keywords in rules.items():
        if category == 'income':
            continue
            
        for keyword in keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', description_lower):
                return category
    
    return 'other'


def parse_csv_file(filepath: str) -> List[Tuple[str, str, float]]:
    """
    Parse CSV file and extract transaction data.
    
    Args:
        filepath: Path to CSV file
    
    Returns:
        List of tuples containing (date, description, amount)
    """
    transactions = []
    
    try:
        with open(filepath, 'r', newline='', encoding='utf-8') as file:
            # Try to detect the CSV format
            sample = file.read(1024)
            file.seek(0)
            
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
            reader = csv.DictReader(file, delimiter=delimiter)
            
            # Common column name variations
            date_cols = ['date', 'transaction_date', 'posting_date', 'Date', 'Transaction Date']
            desc_cols = ['description', 'desc', 'memo', 'Description', 'Memo', 'Transaction Description']
            amount_cols = ['amount', 'Amount', 'debit', 'credit', 'Debit', 'Credit', 'transaction_amount']
            
            # Find the actual column names
            fieldnames = reader.fieldnames or []
            date_col = next((col for col in date_cols if col in fieldnames), fieldnames[0] if fieldnames else 'date')
            desc_col = next((col for col in desc_cols if col in fieldnames), fieldnames[1] if len(fieldnames) > 1 else 'description')
            amount_col = next((col for col in amount_cols if col in fieldnames), fieldnames[2] if len(fieldnames) > 2 else 'amount')
            
            for row in reader:
                try:
                    date = row.get(date_col, '').strip()
                    description = row.get(desc_col, '').strip()
                    amount_str = row.get(amount_col, '0').strip()
                    
                    # Clean and parse amount
                    amount_str = re.sub(r'[,$]', '', amount_str)
                    amount = float(amount_str) if amount_str else 0.0
                    
                    if description:  # Only add rows with descriptions
                        transactions.append((date, description, amount))
                        
                except (ValueError, TypeError) as e:
                    print(f"Warning: Skipping invalid row in {filepath}: {e}")
                    continue
                    
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return []
    
    return transactions


def main():
    """Main function to process bank statement files and categorize transactions."""
    try:
        # Find all CSV files in current directory
        csv_files = glob.glob("*.csv")
        
        if not csv_files:
            print("No CSV files found in current directory.")
            print("Please place your bank statement CSV files in the same directory as this script.")
            return
        
        print(f"Found {len(csv_files)} CSV file(s): {', '.join(csv_files)}")
        print("-" * 60)
        
        # Load categorization rules
        rules = load_categorization_rules()
        
        # Process all transactions
        all_transactions = []
        category_totals = defaultdict(float)
        
        for csv_file in csv_files:
            print(f"Processing {csv_file}...")
            transactions = parse_csv_file(csv_file)
            
            if not transactions:
                print(f"No valid transactions found in {csv_file}")