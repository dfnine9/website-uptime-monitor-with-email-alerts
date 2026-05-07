```python
"""
Transaction Categorization Script

This script reads CSV files containing financial transaction data, applies regex patterns 
to categorize transactions based on merchant names or descriptions, and outputs a 
categorized spending summary.

The script expects CSV files with columns: date, description, amount
It categorizes transactions into predefined categories using regex patterns and 
provides a summary of spending by category.

Usage: python script.py
"""

import csv
import re
import sys
from collections import defaultdict
from pathlib import Path


def load_transaction_patterns():
    """Define regex patterns for transaction categorization."""
    return {
        'Groceries': [
            r'(?i)(walmart|target|kroger|safeway|whole foods|trader joe|costco|grocery)',
            r'(?i)(supermarket|market|food.*store)',
        ],
        'Restaurants': [
            r'(?i)(restaurant|cafe|coffee|starbucks|mcdonald|burger|pizza)',
            r'(?i)(dine|dining|eatery|bistro|grill)',
        ],
        'Gas/Fuel': [
            r'(?i)(shell|exxon|bp|chevron|mobil|gas|fuel|station)',
            r'(?i)(petrol|gasoline)',
        ],
        'Shopping': [
            r'(?i)(amazon|ebay|store|shop|retail|mall)',
            r'(?i)(department|clothing|apparel)',
        ],
        'Utilities': [
            r'(?i)(electric|water|gas.*company|utility|power|internet|phone)',
            r'(?i)(comcast|verizon|att|spectrum)',
        ],
        'Healthcare': [
            r'(?i)(hospital|medical|doctor|pharmacy|health|dental)',
            r'(?i)(cvs|walgreens|clinic)',
        ],
        'Transportation': [
            r'(?i)(uber|lyft|taxi|bus|train|metro|parking|toll)',
            r'(?i)(transit|transportation)',
        ],
        'Entertainment': [
            r'(?i)(movie|theater|netflix|spotify|game|entertainment)',
            r'(?i)(cinema|music|streaming)',
        ],
        'Banking/Finance': [
            r'(?i)(bank|atm|fee|interest|loan|credit|transfer)',
            r'(?i)(payment|finance|investment)',
        ]
    }


def categorize_transaction(description, patterns):
    """Categorize a transaction based on its description using regex patterns."""
    description = description.strip()
    
    for category, regex_list in patterns.items():
        for pattern in regex_list:
            if re.search(pattern, description):
                return category
    
    return 'Other'


def read_csv_file(filepath):
    """Read CSV file and return transaction data."""
    transactions = []
    
    try:
        with open(filepath, 'r', newline='', encoding='utf-8') as file:
            # Try to detect if file has headers
            sample = file.read(1024)
            file.seek(0)
            
            # Check if first line looks like headers
            first_line = file.readline().strip().lower()
            file.seek(0)
            
            has_headers = any(header in first_line for header in ['date', 'description', 'amount'])
            
            reader = csv.reader(file)
            
            if has_headers:
                next(reader)  # Skip header row
            
            for row_num, row in enumerate(reader, start=1):
                if len(row) < 3:
                    print(f"Warning: Row {row_num} has insufficient columns, skipping")
                    continue
                
                try:
                    date = row[0].strip()
                    description = row[1].strip()
                    amount = float(row[2].strip().replace('$', '').replace(',', ''))
                    
                    transactions.append({
                        'date': date,
                        'description': description,
                        'amount': amount
                    })
                except (ValueError, IndexError) as e:
                    print(f"Warning: Error parsing row {row_num}: {e}")
                    continue
                    
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found")
        return []
    except Exception as e:
        print(f"Error reading file '{filepath}': {e}")
        return []
    
    return transactions


def generate_sample_csv():
    """Generate a sample CSV file for testing if none exists."""
    sample_data = [
        ['Date', 'Description', 'Amount'],
        ['2024-01-15', 'WALMART SUPERCENTER', '-89.45'],
        ['2024-01-16', 'STARBUCKS COFFEE', '-5.75'],
        ['2024-01-17', 'SHELL GAS STATION', '-45.20'],
        ['2024-01-18', 'AMAZON PURCHASE', '-125.99'],
        ['2024-01-19', 'ELECTRIC COMPANY', '-150.00'],
        ['2024-01-20', 'CVS PHARMACY', '-23.45'],
        ['2024-01-21', 'UBER RIDE', '-15.30'],
        ['2024-01-22', 'NETFLIX SUBSCRIPTION', '-15.99'],
        ['2024-01-23', 'BANK TRANSFER FEE', '-3.00'],
        ['2024-01-24', 'LOCAL RESTAURANT', '-42.85']
    ]
    
    try:
        with open('sample_transactions.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(sample_data)
        print("Generated sample_transactions.csv for testing")
        return 'sample_transactions.csv'
    except Exception as e:
        print(f"Error creating sample file: {e}")
        return None


def main():
    """Main function to process transactions and generate categorized summary."""
    patterns = load_transaction_patterns()
    
    # Look for CSV files in current directory
    csv_files = list(Path('.').glob('*.csv'))
    
    if not csv_files:
        print("No CSV files found in current directory.")
        sample_file = generate_sample_csv()
        if sample_file:
            csv_files = [Path(sample_file)]
        else:
            print("Unable to create sample file. Exiting.")
            sys.exit(1)
    
    all_transactions = []
    
    # Process all CSV files
    for csv_file in csv_files:
        print(f"\nProcessing file: {csv_file}")
        transactions = read_csv_file(csv_file)
        
        if not transactions:
            continue
            
        print(f"Loaded {len(transactions)} transactions from {csv_file}")
        all_transactions.extend(transactions)
    
    if not all_transactions:
        print("No valid transactions found in any CSV file.")
        sys.exit(1)
    
    # Categorize transactions
    category_totals = defaultdict(float)
    category_counts = defaultdict(int)
    categorized_transactions = []
    
    for transaction in all_transactions:
        category = categorize_transaction(transaction['description'], patterns)
        transaction['category'] = category
        categorized_transactions.append(transaction)
        
        category_totals[category] += abs(transaction['amount'])  # Use absolute value for spending
        category_counts[category] += 1
    
    # Generate summary
    print("\n" + "="*80)
    print("TRANSACTION CATEGORIZATION SUMMARY")
    print("="*80)
    
    total_spending = sum(category_totals.values())
    
    print(f"\nTotal Transactions Processed: {len(all_transactions)}")
    print(f"Total Spending: ${total_spending:,.2f}")
    print("\nSpending by Category:")
    print("-" * 60)
    
    # Sort categories by spending amount (descending)
    sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
    
    for category, amount in sorted_categories:
        percentage = (amount / total_spending) * 100 if total_spending > 0 else 0