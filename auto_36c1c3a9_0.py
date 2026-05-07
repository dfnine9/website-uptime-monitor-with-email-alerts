```python
"""
Bank CSV Transaction Categorizer

This module reads bank CSV files and categorizes transactions using regex pattern matching.
It identifies expenses in categories like groceries, gas, restaurants, utilities, and entertainment,
then outputs the categorized transactions with basic validation.

The script expects CSV files with columns: Date, Description, Amount
Negative amounts are treated as expenses, positive as income.
"""

import csv
import re
import sys
import os
from typing import Dict, List, Tuple, Optional
from datetime import datetime


class TransactionCategorizer:
    """Categorizes bank transactions based on description patterns."""
    
    def __init__(self):
        self.category_patterns = {
            'groceries': [
                r'\b(walmart|target|kroger|safeway|publix|whole foods|trader joe|costco)\b',
                r'\b(grocery|market|food|supermarket)\b',
                r'\b(aldi|wegmans|harris teeter|giant|food lion)\b'
            ],
            'gas': [
                r'\b(shell|exxon|mobil|chevron|bp|texaco|citgo|marathon)\b',
                r'\b(gas|fuel|station|pump)\b',
                r'\b(speedway|wawa|sheetz|circle k)\b'
            ],
            'restaurants': [
                r'\b(mcdonald|burger king|subway|starbucks|dunkin|kfc|pizza)\b',
                r'\b(restaurant|diner|cafe|bistro|grill)\b',
                r'\b(chipotle|panera|taco bell|wendy|domino|papa)\b'
            ],
            'utilities': [
                r'\b(electric|power|gas company|water|sewer)\b',
                r'\b(utility|utilities|pge|duke energy|dominion)\b',
                r'\b(internet|cable|phone|wireless|verizon|att|comcast)\b'
            ],
            'entertainment': [
                r'\b(netflix|spotify|amazon prime|disney|hulu)\b',
                r'\b(movie|theater|cinema|concert|show)\b',
                r'\b(game|gaming|steam|playstation|xbox)\b'
            ]
        }
        
        # Compile patterns for efficiency
        self.compiled_patterns = {}
        for category, patterns in self.category_patterns.items():
            self.compiled_patterns[category] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]
    
    def categorize_transaction(self, description: str) -> str:
        """Categorize a transaction based on its description."""
        for category, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(description):
                    return category
        return 'other'
    
    def validate_transaction(self, row: Dict[str, str]) -> Tuple[bool, str]:
        """Validate a transaction row."""
        try:
            # Check required fields
            if not all(key in row for key in ['Date', 'Description', 'Amount']):
                return False, "Missing required fields"
            
            # Validate date format
            try:
                datetime.strptime(row['Date'], '%Y-%m-%d')
            except ValueError:
                try:
                    datetime.strptime(row['Date'], '%m/%d/%Y')
                except ValueError:
                    return False, f"Invalid date format: {row['Date']}"
            
            # Validate amount
            try:
                float(row['Amount'])
            except ValueError:
                return False, f"Invalid amount format: {row['Amount']}"
            
            # Check description is not empty
            if not row['Description'].strip():
                return False, "Empty description"
            
            return True, ""
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"


def read_csv_file(filename: str) -> List[Dict[str, str]]:
    """Read CSV file and return list of transaction dictionaries."""
    transactions = []
    
    try:
        with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
            # Try to detect delimiter
            sample = csvfile.read(1024)
            csvfile.seek(0)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
            reader = csv.DictReader(csvfile, delimiter=delimiter)
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 for header
                # Clean whitespace from values
                cleaned_row = {key.strip(): value.strip() for key, value in row.items()}
                transactions.append(cleaned_row)
                
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    except csv.Error as e:
        print(f"Error reading CSV file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error reading file: {e}")
        sys.exit(1)
    
    return transactions


def process_transactions(transactions: List[Dict[str, str]]) -> Dict[str, List[Dict]]:
    """Process and categorize transactions."""
    categorizer = TransactionCategorizer()
    categorized = {
        'groceries': [],
        'gas': [],
        'restaurants': [],
        'utilities': [],
        'entertainment': [],
        'other': [],
        'invalid': []
    }
    
    for i, transaction in enumerate(transactions, start=1):
        try:
            # Validate transaction
            is_valid, error_msg = categorizer.validate_transaction(transaction)
            
            if not is_valid:
                transaction['error'] = error_msg
                categorized['invalid'].append(transaction)
                print(f"Warning: Row {i} validation failed: {error_msg}")
                continue
            
            # Categorize transaction
            description = transaction['Description']
            category = categorizer.categorize_transaction(description)
            
            # Add metadata
            transaction['category'] = category
            transaction['row_number'] = i
            
            # Only categorize expenses (negative amounts or clearly expense descriptions)
            try:
                amount = float(transaction['Amount'])
                if amount < 0 or any(word in description.lower() for word in 
                                   ['purchase', 'payment', 'debit', 'withdrawal']):
                    categorized[category].append(transaction)
                else:
                    categorized['other'].append(transaction)
            except ValueError:
                categorized['invalid'].append(transaction)
                
        except Exception as e:
            print(f"Error processing row {i}: {e}")
            transaction['error'] = str(e)
            categorized['invalid'].append(transaction)
    
    return categorized


def print_results(categorized: Dict[str, List[Dict]]):
    """Print categorized transactions to stdout."""
    print("=" * 80)
    print("BANK TRANSACTION CATEGORIZATION RESULTS")
    print("=" * 80)
    
    # Summary statistics
    total_transactions = sum(len(transactions) for transactions in categorized.values())
    print(f"\nSUMMARY:")
    print(f"Total transactions processed: {total_transactions}")
    
    for category, transactions in categorized.items():
        if transactions:
            count = len(transactions)
            if category != 'invalid':
                total_amount = sum(float(t['Amount']) for t in transactions 
                                 if 'Amount' in t and t['Amount'])
                print(f"{category.upper()}: {count} transactions, Total: ${abs(total_amount):.2f}")
            else:
                print(f"{category.upper()}: {count} invalid transactions")
    
    print("\n" + "=" * 80)
    
    # Detailed results
    for category, transactions in categorized.items():
        if not transactions:
            continue
            
        print(f"\n{category.upper()} TRANSACTIONS:")
        print("-" * 40)
        
        for transaction in transactions:
            try:
                date = transaction.get('Date', 'N/A')
                desc = transaction.get('Description', 'N/A')[: