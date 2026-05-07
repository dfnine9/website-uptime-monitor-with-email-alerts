```python
"""
Expense Categorization Script

This module reads CSV transaction data and automatically categorizes expenses based on
merchant names and transaction descriptions using regex patterns. Categories include
groceries, utilities, entertainment, dining, transportation, shopping, healthcare,
and other common expense types.

The script reads from 'transactions.csv' and outputs to 'categorized_transactions.csv'
with additional category columns added.

Usage: python script.py
"""

import csv
import re
import sys
from typing import Dict, List, Tuple

def create_category_patterns() -> Dict[str, List[str]]:
    """
    Create regex patterns for expense categorization.
    
    Returns:
        Dict mapping category names to lists of regex patterns
    """
    patterns = {
        'Groceries': [
            r'(?i)\b(walmart|target|kroger|safeway|publix|whole foods|trader joe|costco|sam\'s club)\b',
            r'(?i)\b(grocery|supermarket|market|food store)\b',
            r'(?i)\b(aldi|wegmans|giant|harris teeter|fresh market)\b'
        ],
        'Utilities': [
            r'(?i)\b(electric|electricity|gas|water|sewer|internet|cable|phone|wireless)\b',
            r'(?i)\b(verizon|att|t-mobile|comcast|xfinity|spectrum|cox)\b',
            r'(?i)\b(utility|utilities|power company|energy)\b'
        ],
        'Entertainment': [
            r'(?i)\b(netflix|hulu|disney|spotify|apple music|amazon prime)\b',
            r'(?i)\b(movie|cinema|theater|theatre|concert|show)\b',
            r'(?i)\b(entertainment|streaming|subscription)\b'
        ],
        'Dining': [
            r'(?i)\b(restaurant|cafe|coffee|starbucks|dunkin|mcdonald|burger|pizza)\b',
            r'(?i)\b(dining|food delivery|uber eats|doordash|grubhub)\b',
            r'(?i)\b(bar|pub|brewery|tavern)\b'
        ],
        'Transportation': [
            r'(?i)\b(gas station|shell|bp|exxon|chevron|mobil)\b',
            r'(?i)\b(uber|lyft|taxi|parking|metro|transit)\b',
            r'(?i)\b(car|auto|vehicle|maintenance|repair)\b'
        ],
        'Shopping': [
            r'(?i)\b(amazon|ebay|etsy|shopping|retail|store)\b',
            r'(?i)\b(clothing|apparel|shoes|fashion)\b',
            r'(?i)\b(home depot|lowe\'s|furniture|decor)\b'
        ],
        'Healthcare': [
            r'(?i)\b(pharmacy|cvs|walgreens|rite aid|medical|doctor|hospital)\b',
            r'(?i)\b(health|dental|vision|insurance|prescription)\b'
        ],
        'Banking': [
            r'(?i)\b(bank|atm|fee|transfer|withdrawal|deposit)\b',
            r'(?i)\b(interest|finance|loan|credit)\b'
        ]
    }
    return patterns

def categorize_transaction(merchant: str, description: str, patterns: Dict[str, List[str]]) -> str:
    """
    Categorize a transaction based on merchant and description.
    
    Args:
        merchant: Merchant name
        description: Transaction description
        patterns: Category patterns dictionary
        
    Returns:
        Category name or 'Other' if no match found
    """
    text_to_check = f"{merchant} {description}".strip()
    
    for category, pattern_list in patterns.items():
        for pattern in pattern_list:
            if re.search(pattern, text_to_check):
                return category
    
    return 'Other'

def process_transactions(input_file: str, output_file: str) -> Tuple[int, int]:
    """
    Process transactions from input CSV and write categorized results to output CSV.
    
    Args:
        input_file: Path to input CSV file
        output_file: Path to output CSV file
        
    Returns:
        Tuple of (total_transactions, categorized_transactions)
    """
    patterns = create_category_patterns()
    total_transactions = 0
    categorized_transactions = 0
    
    try:
        with open(input_file, 'r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            
            # Get original fieldnames and add category column
            fieldnames = reader.fieldnames
            if not fieldnames:
                raise ValueError("CSV file appears to be empty or invalid")
            
            output_fieldnames = list(fieldnames) + ['Category']
            
            with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=output_fieldnames)
                writer.writeheader()
                
                for row in reader:
                    total_transactions += 1
                    
                    # Extract merchant and description with fallback values
                    merchant = row.get('Merchant', row.get('merchant', ''))
                    description = row.get('Description', row.get('description', ''))
                    
                    # Categorize the transaction
                    category = categorize_transaction(merchant, description, patterns)
                    
                    # Add category to row
                    row['Category'] = category
                    writer.writerow(row)
                    
                    if category != 'Other':
                        categorized_transactions += 1
    
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file '{input_file}' not found")
    except Exception as e:
        raise Exception(f"Error processing transactions: {str(e)}")
    
    return total_transactions, categorized_transactions

def create_sample_data():
    """Create sample transaction data if input file doesn't exist."""
    sample_data = [
        {'Date': '2024-01-15', 'Merchant': 'Walmart', 'Description': 'Grocery Shopping', 'Amount': '-85.42'},
        {'Date': '2024-01-16', 'Merchant': 'Shell Gas Station', 'Description': 'Fuel Purchase', 'Amount': '-45.00'},
        {'Date': '2024-01-17', 'Merchant': 'Netflix', 'Description': 'Monthly Subscription', 'Amount': '-15.99'},
        {'Date': '2024-01-18', 'Merchant': 'Starbucks', 'Description': 'Coffee', 'Amount': '-5.75'},
        {'Date': '2024-01-19', 'Merchant': 'ComEd', 'Description': 'Electric Bill', 'Amount': '-120.33'},
        {'Date': '2024-01-20', 'Merchant': 'Amazon', 'Description': 'Online Purchase', 'Amount': '-35.99'},
        {'Date': '2024-01-21', 'Merchant': 'CVS Pharmacy', 'Description': 'Prescription', 'Amount': '-25.00'},
        {'Date': '2024-01-22', 'Merchant': 'Unknown Merchant', 'Description': 'Misc Purchase', 'Amount': '-12.50'}
    ]
    
    with open('transactions.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['Date', 'Merchant', 'Description', 'Amount'])
        writer.writeheader()
        writer.writerows(sample_data)

def main():
    """Main execution function."""
    input_file = 'transactions.csv'
    output_file = 'categorized_transactions.csv'
    
    try:
        # Check if input file exists, create sample if not
        try:
            with open(input_file, 'r'):
                pass
        except FileNotFoundError:
            print(f"Input file '{input_file}' not found. Creating sample data...")
            create_sample_data()
            print(f"Sample data