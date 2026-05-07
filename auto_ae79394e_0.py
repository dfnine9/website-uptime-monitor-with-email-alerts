```python
#!/usr/bin/env python3
"""
Bank Statement Transaction Analyzer

This module reads CSV bank statements, categorizes transactions using regex patterns,
and generates spending analysis with matplotlib charts. It processes transaction data
to identify spending patterns by merchant categories and provides visual analytics.

The script expects a CSV file with columns: date, description, amount
It categorizes transactions into predefined merchant categories using regex matching
and generates bar charts showing spending by category and time trends.

Usage: python script.py
"""

import csv
import re
import sys
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Merchant categorization patterns
CATEGORY_PATTERNS = {
    'Groceries': [
        r'walmart|target|kroger|safeway|whole foods|trader joe|costco|sam\'s club',
        r'grocery|supermarket|market|food|fresh'
    ],
    'Restaurants': [
        r'restaurant|cafe|coffee|starbucks|mcdonald|burger|pizza|taco|subway',
        r'dining|eatery|bistro|grill|bar & grill'
    ],
    'Gas/Fuel': [
        r'shell|exxon|chevron|bp|mobil|texaco|arco|valero|gas station',
        r'fuel|gasoline|gas '
    ],
    'Shopping': [
        r'amazon|ebay|best buy|home depot|lowes|macys|nordstrom',
        r'store|shop|retail|mall|outlet'
    ],
    'Bills/Utilities': [
        r'electric|water|gas bill|internet|phone|cable|insurance|utility',
        r'payment.*auto|autopay|bill pay'
    ],
    'Healthcare': [
        r'medical|doctor|hospital|pharmacy|dental|vision|clinic',
        r'health|medicare|prescription'
    ],
    'Entertainment': [
        r'movie|theater|netflix|spotify|gaming|gym|fitness',
        r'entertainment|recreation|streaming'
    ],
    'Banking': [
        r'bank|atm|fee|interest|transfer|deposit',
        r'overdraft|maintenance|service charge'
    ]
}

def categorize_transaction(description: str) -> str:
    """
    Categorize a transaction based on its description using regex patterns.
    
    Args:
        description: Transaction description string
        
    Returns:
        Category name or 'Other' if no match found
    """
    description_lower = description.lower()
    
    for category, patterns in CATEGORY_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, description_lower):
                return category
    
    return 'Other'

def read_csv_statements(filename: str) -> List[Dict]:
    """
    Read bank statement CSV file and return list of transaction dictionaries.
    
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
        with open(filename, 'r', encoding='utf-8') as file:
            # Try to detect delimiter
            sample = file.read(1024)
            file.seek(0)
            
            delimiter = ',' if ',' in sample else '\t' if '\t' in sample else ';'
            reader = csv.DictReader(file, delimiter=delimiter)
            
            for row_num, row in enumerate(reader, 1):
                try:
                    # Handle common column name variations
                    date_col = None
                    desc_col = None
                    amount_col = None
                    
                    for key in row.keys():
                        key_lower = key.lower()
                        if 'date' in key_lower:
                            date_col = key
                        elif 'description' in key_lower or 'desc' in key_lower or 'merchant' in key_lower:
                            desc_col = key
                        elif 'amount' in key_lower or 'debit' in key_lower or 'credit' in key_lower:
                            amount_col = key
                    
                    if not all([date_col, desc_col, amount_col]):
                        raise ValueError(f"Required columns not found. Available: {list(row.keys())}")
                    
                    # Parse transaction data
                    date_str = row[date_col].strip()
                    description = row[desc_col].strip()
                    amount_str = row[amount_col].strip()
                    
                    # Parse date (try multiple formats)
                    date_obj = None
                    date_formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S']
                    
                    for date_format in date_formats:
                        try:
                            date_obj = datetime.strptime(date_str, date_format)
                            break
                        except ValueError:
                            continue
                    
                    if not date_obj:
                        print(f"Warning: Could not parse date '{date_str}' on row {row_num}")
                        continue
                    
                    # Parse amount (handle negative signs, currency symbols)
                    amount_clean = re.sub(r'[^\d.-]', '', amount_str)
                    amount = float(amount_clean) if amount_clean else 0.0
                    
                    # Categorize transaction
                    category = categorize_transaction(description)
                    
                    transactions.append({
                        'date': date_obj,
                        'description': description,
                        'amount': amount,
                        'category': category
                    })
                    
                except (ValueError, KeyError) as e:
                    print(f"Warning: Error processing row {row_num}: {e}")
                    continue
                    
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file '{filename}' not found")
    except Exception as e:
        raise ValueError(f"Error reading CSV file: {e}")
    
    return transactions

def analyze_spending(transactions: List[Dict]) -> Tuple[Dict[str, float], Dict[str, List[Tuple]]]:
    """
    Analyze spending patterns by category and time.
    
    Args:
        transactions: List of transaction dictionaries
        
    Returns:
        Tuple of (category_totals, monthly_spending)
    """
    category_totals = defaultdict(float)
    monthly_spending = defaultdict(lambda: defaultdict(float))
    
    for transaction in transactions:
        amount = abs(transaction['amount'])  # Use absolute value for spending analysis
        category = transaction['category']
        month_key = transaction['date'].strftime('%Y-%m')
        
        category_totals[category] += amount
        monthly_spending[month_key][category] += amount
    
    # Convert monthly spending to sorted list format
    monthly_data = {}
    for month in sorted(monthly_spending.keys()):
        monthly_data[month] = list(monthly_spending[month].items())
    
    return dict(category_totals), monthly_data

def create_spending_charts(category_totals: Dict[str, float], monthly_spending: Dict[str, List[Tuple]]):
    """
    Create matplotlib charts for spending analysis.
    
    Args:
        category_totals: Dictionary of category spending totals
        monthly_spending: Dictionary of monthly spending by category
    """
    try:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Chart 1: Spending by category (bar chart)
        if category_totals:
            categories = list(category_totals.keys())
            amounts = list(category_totals.values())
            
            bars = ax1.bar(categories, amounts, color='skyblue', edgecolor='navy')
            ax1.set_title('Total Spending by Category', fontsize=14, fontweight='bold')
            ax1.set_xlabel('Category')
            ax1.set_ylabel('Amount ($)')
            ax1.tick_params(axis='x', rotation=45)