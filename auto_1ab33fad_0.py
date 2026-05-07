```python
#!/usr/bin/env python3
"""
Bank Transaction Categorizer

This module reads CSV bank exports, cleans transaction descriptions by removing 
special characters and standardizing text, then applies rule-based categorization 
using predefined keyword dictionaries for categories like groceries, utilities, 
entertainment, etc.

The script processes CSV files with transaction data, cleans the descriptions,
and categorizes each transaction based on keyword matching. Results are printed
to stdout in a formatted table.

Usage: python script.py

Requirements: Python 3.6+ with pandas (will attempt to install if missing)
"""

import csv
import re
import sys
import subprocess
import os
from typing import Dict, List, Any

# Category definitions with keywords
CATEGORIES = {
    'Groceries': [
        'grocery', 'supermarket', 'walmart', 'target', 'kroger', 'safeway',
        'whole foods', 'trader joe', 'costco', 'sam\'s club', 'food lion',
        'publix', 'wegmans', 'stop shop', 'giant', 'food', 'market'
    ],
    'Utilities': [
        'electric', 'electricity', 'gas', 'water', 'sewer', 'internet',
        'cable', 'phone', 'cellular', 'utility', 'power', 'energy',
        'comcast', 'verizon', 'att', 'spectrum', 'xfinity'
    ],
    'Entertainment': [
        'netflix', 'spotify', 'hulu', 'disney', 'amazon prime', 'youtube',
        'movie', 'theater', 'cinema', 'concert', 'spotify', 'apple music',
        'gaming', 'steam', 'playstation', 'xbox', 'entertainment'
    ],
    'Transportation': [
        'gas station', 'fuel', 'gasoline', 'shell', 'exxon', 'bp', 'chevron',
        'uber', 'lyft', 'taxi', 'parking', 'metro', 'bus', 'train',
        'airline', 'flight', 'car rental', 'dmv'
    ],
    'Restaurants': [
        'restaurant', 'fast food', 'mcdonald', 'burger king', 'subway',
        'starbucks', 'coffee', 'pizza', 'chinese', 'mexican', 'italian',
        'diner', 'cafe', 'bistro', 'grill', 'bar'
    ],
    'Healthcare': [
        'pharmacy', 'cvs', 'walgreens', 'rite aid', 'hospital', 'clinic',
        'doctor', 'dental', 'medical', 'health', 'insurance', 'copay'
    ],
    'Shopping': [
        'amazon', 'ebay', 'store', 'retail', 'clothing', 'department',
        'mall', 'outlet', 'shop', 'purchase', 'buy', 'merchandise'
    ],
    'Banking': [
        'bank', 'atm', 'fee', 'transfer', 'deposit', 'withdrawal',
        'interest', 'loan', 'mortgage', 'credit card', 'payment'
    ]
}

def install_pandas():
    """Install pandas if not available."""
    try:
        import pandas
        return pandas
    except ImportError:
        print("Installing pandas...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pandas'])
            import pandas
            return pandas
        except Exception as e:
            print(f"Failed to install pandas: {e}")
            print("Please install pandas manually: pip install pandas")
            sys.exit(1)

def clean_description(description: str) -> str:
    """
    Clean transaction description by removing special characters and standardizing text.
    
    Args:
        description (str): Raw transaction description
        
    Returns:
        str: Cleaned description
    """
    if not description or not isinstance(description, str):
        return ""
    
    # Convert to lowercase
    cleaned = description.lower().strip()
    
    # Remove special characters but keep spaces and alphanumeric
    cleaned = re.sub(r'[^\w\s]', ' ', cleaned)
    
    # Replace multiple spaces with single space
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    # Remove extra whitespace
    cleaned = cleaned.strip()
    
    return cleaned

def categorize_transaction(description: str, categories: Dict[str, List[str]]) -> str:
    """
    Categorize transaction based on description keywords.
    
    Args:
        description (str): Cleaned transaction description
        categories (Dict[str, List[str]]): Category keyword dictionary
        
    Returns:
        str: Category name or 'Other' if no match found
    """
    if not description:
        return 'Other'
    
    description_lower = description.lower()
    
    # Check each category for keyword matches
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword.lower() in description_lower:
                return category
    
    return 'Other'

def create_sample_csv():
    """Create a sample CSV file for demonstration."""
    sample_data = [
        ['Date', 'Description', 'Amount'],
        ['2024-01-01', 'WALMART SUPERCENTER #123', '-85.42'],
        ['2024-01-02', 'SHELL GAS STATION', '-45.00'],
        ['2024-01-03', 'NETFLIX.COM MONTHLY', '-15.99'],
        ['2024-01-04', 'STARBUCKS COFFEE #456', '-5.75'],
        ['2024-01-05', 'CVS PHARMACY #789', '-23.50'],
        ['2024-01-06', 'COMCAST CABLE PAYMENT', '-89.99'],
        ['2024-01-07', 'AMAZON.COM PURCHASE', '-67.83'],
        ['2024-01-08', 'UBER RIDE 01/08', '-12.50'],
        ['2024-01-09', 'KROGER GROCERY STORE', '-156.78'],
        ['2024-01-10', 'BANK ATM FEE', '-3.00']
    ]
    
    with open('sample_transactions.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(sample_data)
    
    return 'sample_transactions.csv'

def process_csv_file(filename: str, pd) -> None:
    """
    Process CSV file and categorize transactions.
    
    Args:
        filename (str): Path to CSV file
        pd: pandas module
    """
    try:
        # Read CSV file
        df = pd.read_csv(filename)
        
        # Ensure required columns exist
        if 'Description' not in df.columns:
            print("Error: CSV file must contain 'Description' column")
            return
        
        # Clean descriptions
        df['Cleaned_Description'] = df['Description'].apply(clean_description)
        
        # Categorize transactions
        df['Category'] = df['Cleaned_Description'].apply(
            lambda x: categorize_transaction(x, CATEGORIES)
        )
        
        # Display results
        print("\n" + "="*80)
        print("BANK TRANSACTION CATEGORIZATION RESULTS")
        print("="*80)
        
        # Show sample of processed data
        print(f"\nProcessed {len(df)} transactions")
        print(f"File: {filename}")
        
        # Display categorization summary
        category_counts = df['Category'].value_counts()
        print("\nCategory Summary:")
        print("-" * 40)
        for category, count in category_counts.items():
            print(f"{category:<20}: {count:>3} transactions")
        
        # Display detailed results
        print(f"\nDetailed Transaction List:")
        print("-" * 80)
        
        for idx, row in df.iterrows():
            date = row.get('Date', 'N/A')
            original_desc = str(row['Description'])[:40] + "