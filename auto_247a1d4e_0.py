#!/usr/bin/env python3
"""
Bank Statement Transaction Categorizer

This module reads CSV bank statements, automatically categorizes transactions
using keyword matching rules, and calculates spending totals by category.

The script expects a CSV file named 'bank_statements.csv' in the same directory
with columns: Date, Description, Amount (negative for expenses, positive for income).

Categories are assigned based on keywords found in transaction descriptions.
Results include total spending by category and individual transaction details.

Usage: python script.py
"""

import csv
import sys
from collections import defaultdict
from decimal import Decimal, InvalidOperation
import re


def load_categorization_rules():
    """Define keyword-based categorization rules."""
    return {
        'groceries': ['grocery', 'supermarket', 'walmart', 'target', 'costco', 'food mart', 'kroger'],
        'restaurants': ['restaurant', 'cafe', 'pizza', 'mcdonald', 'starbucks', 'coffee', 'diner'],
        'gas': ['gas station', 'shell', 'exxon', 'bp', 'chevron', 'fuel'],
        'utilities': ['electric', 'water', 'internet', 'phone', 'cable', 'utility'],
        'entertainment': ['movie', 'theater', 'netflix', 'spotify', 'gaming', 'concert'],
        'shopping': ['amazon', 'ebay', 'mall', 'store', 'retail', 'clothing'],
        'healthcare': ['pharmacy', 'doctor', 'hospital', 'medical', 'dental'],
        'transportation': ['uber', 'lyft', 'taxi', 'bus', 'train', 'parking'],
        'banking': ['fee', 'interest', 'atm', 'transfer', 'payment'],
        'income': ['salary', 'paycheck', 'deposit', 'refund', 'dividend']
    }


def categorize_transaction(description, rules):
    """Categorize a transaction based on description keywords."""
    description_lower = description.lower()
    
    for category, keywords in rules.items():
        if any(keyword in description_lower for keyword in keywords):
            return category
    
    return 'other'


def parse_amount(amount_str):
    """Parse amount string to Decimal, handling various formats."""
    try:
        # Remove currency symbols and whitespace
        cleaned = re.sub(r'[$,\s]', '', str(amount_str))
        
        # Handle parentheses as negative (accounting format)
        if cleaned.startswith('(') and cleaned.endswith(')'):
            cleaned = '-' + cleaned[1:-1]
        
        return Decimal(cleaned)
    except (InvalidOperation, ValueError):
        raise ValueError(f"Cannot parse amount: {amount_str}")


def read_bank_statements(filename):
    """Read and parse CSV bank statements."""
    transactions = []
    
    try:
        with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
            # Try to detect delimiter
            sample = csvfile.read(1024)
            csvfile.seek(0)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
            reader = csv.DictReader(csvfile, delimiter=delimiter)
            
            # Handle various possible column names
            fieldnames = [field.lower().strip() for field in reader.fieldnames]
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 for header
                try:
                    # Map common column variations
                    date = None
                    description = None
                    amount = None
                    
                    for key, value in row.items():
                        key_lower = key.lower().strip()
                        if key_lower in ['date', 'transaction date', 'trans date']:
                            date = value.strip()
                        elif key_lower in ['description', 'memo', 'transaction', 'details']:
                            description = value.strip()
                        elif key_lower in ['amount', 'debit', 'credit', 'transaction amount']:
                            amount = value.strip()
                    
                    if not all([date, description, amount]):
                        print(f"Warning: Skipping row {row_num} - missing required fields")
                        continue
                    
                    parsed_amount = parse_amount(amount)
                    
                    transactions.append({
                        'date': date,
                        'description': description,
                        'amount': parsed_amount
                    })
                    
                except (ValueError, KeyError) as e:
                    print(f"Warning: Error parsing row {row_num}: {e}")
                    continue
    
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    return transactions


def categorize_transactions(transactions, rules):
    """Categorize all transactions and calculate totals."""
    categorized = []
    category_totals = defaultdict(Decimal)
    
    for transaction in transactions:
        category = categorize_transaction(transaction['description'], rules)
        
        categorized_transaction = {
            'date': transaction['date'],
            'description': transaction['description'],
            'amount': transaction['amount'],
            'category': category
        }
        
        categorized.append(categorized_transaction)
        
        # Only count expenses (negative amounts) in spending totals
        if transaction['amount'] < 0:
            category_totals[category] += abs(transaction['amount'])
    
    return categorized, dict(category_totals)


def print_results(transactions, category_totals):
    """Print categorized transactions and spending summary."""
    print("=" * 80)
    print("BANK STATEMENT TRANSACTION CATEGORIZER RESULTS")
    print("=" * 80)
    
    print(f"\nProcessed {len(transactions)} transactions\n")
    
    # Print spending summary
    print("SPENDING SUMMARY BY CATEGORY:")
    print("-" * 40)
    
    total_spending = Decimal('0')
    for category, amount in sorted(category_totals.items()):
        print(f"{category.upper():<20}: ${amount:>10.2f}")
        total_spending += amount
    
    print("-" * 40)
    print(f"{'TOTAL SPENDING':<20}: ${total_spending:>10.2f}")
    
    # Print transaction details
    print("\n\nTRANSACTION DETAILS:")
    print("-" * 80)
    print(f"{'Date':<12} {'Category':<15} {'Amount':<12} {'Description'}")
    print("-" * 80)
    
    for transaction in sorted(transactions, key=lambda x: x['date']):
        amount_str = f"${transaction['amount']:>9.2f}"
        description = transaction['description'][:40] + "..." if len(transaction['description']) > 40 else transaction['description']
        
        print(f"{transaction['date']:<12} "
              f"{transaction['category']:<15} "
              f"{amount_str:<12} "
              f"{description}")


def main():
    """Main execution function."""
    filename = 'bank_statements.csv'
    
    try:
        # Load categorization rules
        rules = load_categorization_rules()
        
        # Read and parse transactions
        print(f"Reading bank statements from '{filename}'...")
        transactions = read_bank_statements(filename)
        
        if not transactions:
            print("No valid transactions found in the file.")
            sys.exit(1)
        
        # Categorize transactions
        print("Categorizing transactions...")
        categorized_transactions, category_totals = categorize_transactions(transactions, rules)
        
        # Print results
        print_results(categorized_transactions, category_totals)
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()