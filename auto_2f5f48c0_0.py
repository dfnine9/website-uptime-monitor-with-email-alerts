```python
#!/usr/bin/env python3
"""
Bank Statement Transaction Categorizer

This module reads CSV bank statements, applies regex patterns to categorize 
transactions by merchant names, and outputs a categorized spending report.

The script processes transaction data from CSV files, matches merchant names
against predefined regex patterns to assign categories, and generates a
summary report showing spending by category.

Usage:
    python script.py

Requirements:
    - CSV file named 'bank_statement.csv' in the same directory
    - CSV should have columns: date, description, amount
    - Standard library only (no external dependencies)
"""

import csv
import re
import sys
from collections import defaultdict
from datetime import datetime
from decimal import Decimal, InvalidOperation


def load_categorization_rules():
    """
    Load regex patterns for merchant categorization.
    
    Returns:
        dict: Category name mapped to list of regex patterns
    """
    return {
        'Groceries': [
            r'\b(walmart|kroger|safeway|whole foods|trader joe|costco|target)\b',
            r'\b(grocery|supermarket|food market)\b',
            r'\b(publix|harris teeter|food lion)\b'
        ],
        'Restaurants': [
            r'\b(mcdonald|burger king|subway|starbucks|chipotle)\b',
            r'\b(restaurant|cafe|bistro|pizza|diner)\b',
            r'\b(kfc|taco bell|domino|papa john)\b'
        ],
        'Gas/Transportation': [
            r'\b(shell|exxon|chevron|bp|mobil|texaco)\b',
            r'\b(gas station|fuel|petro)\b',
            r'\b(uber|lyft|taxi|metro|transit)\b'
        ],
        'Shopping': [
            r'\b(amazon|ebay|best buy|apple store)\b',
            r'\b(mall|shopping|retail|store)\b',
            r'\b(clothing|apparel|shoes)\b'
        ],
        'Utilities': [
            r'\b(electric|water|gas utility|internet|phone)\b',
            r'\b(verizon|at&t|comcast|xfinity)\b',
            r'\b(utility|power company)\b'
        ],
        'Healthcare': [
            r'\b(pharmacy|cvs|walgreens|hospital|medical)\b',
            r'\b(doctor|dentist|clinic|health)\b'
        ],
        'Entertainment': [
            r'\b(netflix|spotify|hulu|disney|movie)\b',
            r'\b(theater|cinema|entertainment|games)\b'
        ]
    }


def categorize_transaction(description, rules):
    """
    Categorize a transaction based on its description.
    
    Args:
        description (str): Transaction description
        rules (dict): Categorization rules
        
    Returns:
        str: Category name or 'Other' if no match found
    """
    description_lower = description.lower()
    
    for category, patterns in rules.items():
        for pattern in patterns:
            if re.search(pattern, description_lower, re.IGNORECASE):
                return category
                
    return 'Other'


def parse_amount(amount_str):
    """
    Parse amount string to Decimal, handling various formats.
    
    Args:
        amount_str (str): Amount string from CSV
        
    Returns:
        Decimal: Parsed amount or 0 if invalid
    """
    try:
        # Remove currency symbols and parentheses
        cleaned = re.sub(r'[\$,\(\)]', '', str(amount_str).strip())
        
        # Handle negative amounts (sometimes in parentheses)
        if amount_str.strip().startswith('(') and amount_str.strip().endswith(')'):
            cleaned = '-' + cleaned
            
        return Decimal(cleaned)
    except (InvalidOperation, ValueError):
        return Decimal('0')


def read_bank_statement(filename):
    """
    Read bank statement from CSV file.
    
    Args:
        filename (str): Path to CSV file
        
    Returns:
        list: List of transaction dictionaries
        
    Raises:
        FileNotFoundError: If CSV file doesn't exist
        csv.Error: If CSV parsing fails
    """
    transactions = []
    
    with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
        # Try to detect delimiter
        sample = csvfile.read(1024)
        csvfile.seek(0)
        sniffer = csv.Sniffer()
        delimiter = sniffer.sniff(sample).delimiter
        
        reader = csv.DictReader(csvfile, delimiter=delimiter)
        
        # Handle different possible column names
        fieldnames = [field.lower().strip() for field in reader.fieldnames]
        
        for row_num, row in enumerate(reader, start=2):
            try:
                # Normalize column names
                normalized_row = {k.lower().strip(): v for k, v in row.items()}
                
                # Extract data with flexible column name matching
                date_field = None
                desc_field = None
                amount_field = None
                
                for field in normalized_row.keys():
                    if any(keyword in field for keyword in ['date', 'transaction_date', 'posted']):
                        date_field = field
                    elif any(keyword in field for keyword in ['description', 'merchant', 'payee']):
                        desc_field = field
                    elif any(keyword in field for keyword in ['amount', 'debit', 'credit']):
                        amount_field = field
                
                if not all([date_field, desc_field, amount_field]):
                    continue
                
                transaction = {
                    'date': normalized_row[date_field],
                    'description': normalized_row[desc_field],
                    'amount': parse_amount(normalized_row[amount_field])
                }
                
                transactions.append(transaction)
                
            except Exception as e:
                print(f"Warning: Error processing row {row_num}: {e}", file=sys.stderr)
                continue
    
    return transactions


def generate_spending_report(transactions, rules):
    """
    Generate categorized spending report.
    
    Args:
        transactions (list): List of transaction dictionaries
        rules (dict): Categorization rules
        
    Returns:
        dict: Spending summary by category
    """
    category_spending = defaultdict(Decimal)
    category_counts = defaultdict(int)
    
    for transaction in transactions:
        category = categorize_transaction(transaction['description'], rules)
        amount = abs(transaction['amount'])  # Use absolute value for spending
        
        category_spending[category] += amount
        category_counts[category] += 1
    
    return dict(category_spending), dict(category_counts)


def main():
    """Main function to process bank statement and generate report."""
    try:
        # Load categorization rules
        rules = load_categorization_rules()
        
        # Read bank statement
        filename = 'bank_statement.csv'
        print(f"Reading bank statement from {filename}...")
        transactions = read_bank_statement(filename)
        
        if not transactions:
            print("No valid transactions found in the CSV file.")
            return
        
        print(f"Processed {len(transactions)} transactions")
        
        # Generate spending report
        category_spending, category_counts = generate_spending_report(transactions, rules)
        
        # Calculate totals
        total_spending = sum(category_spending.values())
        total_transactions = sum(category_counts.values())
        
        # Print report
        print("\n" + "="*60)
        print("CATEGORIZED SPENDING REPORT")
        print("="*60)
        
        print(f"\nTotal Transactions: {total_transactions}")
        print(f"Total Spending: ${total_spending:,.2f}")
        print("\nSpending by Category:")
        print("-" * 40)
        
        # Sort categories by spending amount (descending)
        sorted_categories = sorted(category_spending.items(), 
                                 key=lambda x: x[1], reverse=True)
        
        for category, amount in sorted_categories:
            count = category_