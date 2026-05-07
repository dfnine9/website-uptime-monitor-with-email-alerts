[ACTION:RESEARCH]

```python
"""
Bank Transaction Categorizer

This module reads CSV bank transaction files and automatically categorizes transactions
into predefined spending categories using regex patterns and keyword matching.

Categories include: groceries, utilities, entertainment, transport, dining, shopping,
healthcare, financial, and other.

Usage: python script.py

The script looks for CSV files in the current directory with columns: date, description, amount
"""

import csv
import re
import os
import sys
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import glob

class TransactionCategorizer:
    def __init__(self):
        self.categories = {
            'groceries': [
                r'\b(grocery|supermarket|market|food|kroger|safeway|walmart|target|costco)\b',
                r'\b(whole foods|trader joe|publix|aldi|fresh|produce)\b'
            ],
            'utilities': [
                r'\b(electric|gas|water|sewer|internet|phone|cable|utility)\b',
                r'\b(verizon|att|comcast|duke energy|pg&e|edison)\b'
            ],
            'entertainment': [
                r'\b(netflix|spotify|hulu|disney|cinema|movie|theater|concert|game)\b',
                r'\b(entertainment|subscription|streaming|youtube|amazon prime)\b'
            ],
            'transport': [
                r'\b(gas|fuel|shell|exxon|chevron|uber|lyft|taxi|metro|transit)\b',
                r'\b(parking|toll|car|auto|vehicle|maintenance|repair)\b'
            ],
            'dining': [
                r'\b(restaurant|cafe|coffee|starbucks|mcdonald|burger|pizza|dine)\b',
                r'\b(takeout|delivery|doordash|grubhub|ubereats|bar|pub)\b'
            ],
            'shopping': [
                r'\b(amazon|ebay|store|shop|retail|clothing|apparel|shoes)\b',
                r'\b(home depot|lowes|best buy|apple store|mall)\b'
            ],
            'healthcare': [
                r'\b(medical|doctor|hospital|pharmacy|health|dental|vision)\b',
                r'\b(cvs|walgreens|clinic|insurance|copay)\b'
            ],
            'financial': [
                r'\b(bank|atm|fee|interest|loan|credit|transfer|payment)\b',
                r'\b(investment|savings|deposit|withdrawal)\b'
            ]
        }
    
    def categorize_transaction(self, description: str) -> str:
        """Categorize a transaction based on its description using regex patterns."""
        description_lower = description.lower()
        
        for category, patterns in self.categories.items():
            for pattern in patterns:
                if re.search(pattern, description_lower, re.IGNORECASE):
                    return category
        
        return 'other'
    
    def read_csv_file(self, filepath: str) -> List[Dict]:
        """Read CSV file and return list of transaction dictionaries."""
        transactions = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                # Try to detect delimiter
                sample = file.read(1024)
                file.seek(0)
                
                delimiter = ',' if sample.count(',') > sample.count(';') else ';'
                
                reader = csv.DictReader(file, delimiter=delimiter)
                
                for row in reader:
                    # Normalize column names (handle different CSV formats)
                    normalized_row = {}
                    for key, value in row.items():
                        key_lower = key.lower().strip()
                        if 'date' in key_lower:
                            normalized_row['date'] = value.strip()
                        elif 'desc' in key_lower or 'memo' in key_lower or 'transaction' in key_lower:
                            normalized_row['description'] = value.strip()
                        elif 'amount' in key_lower or 'value' in key_lower:
                            normalized_row['amount'] = value.strip()
                        else:
                            normalized_row[key] = value
                    
                    if 'description' in normalized_row and 'amount' in normalized_row:
                        transactions.append(normalized_row)
                        
        except Exception as e:
            print(f"Error reading {filepath}: {str(e)}")
            
        return transactions
    
    def process_transactions(self, transactions: List[Dict]) -> List[Dict]:
        """Process transactions and add category information."""
        categorized = []
        
        for transaction in transactions:
            try:
                description = transaction.get('description', '')
                category = self.categorize_transaction(description)
                
                categorized_transaction = transaction.copy()
                categorized_transaction['category'] = category
                categorized.append(categorized_transaction)
                
            except Exception as e:
                print(f"Error processing transaction: {str(e)}")
                continue
                
        return categorized
    
    def generate_summary(self, categorized_transactions: List[Dict]) -> Dict:
        """Generate summary statistics by category."""
        summary = {}
        
        for transaction in categorized_transactions:
            category = transaction.get('category', 'other')
            amount_str = transaction.get('amount', '0')
            
            try:
                # Clean amount string (remove currency symbols, spaces)
                amount_clean = re.sub(r'[^\d.-]', '', amount_str)
                amount = float(amount_clean) if amount_clean else 0.0
                
                if category not in summary:
                    summary[category] = {'count': 0, 'total': 0.0}
                
                summary[category]['count'] += 1
                summary[category]['total'] += abs(amount)  # Use absolute value
                
            except ValueError:
                continue
                
        return summary
    
    def print_results(self, categorized_transactions: List[Dict], summary: Dict, filename: str):
        """Print categorized transactions and summary to stdout."""
        print(f"\n{'='*60}")
        print(f"TRANSACTION CATEGORIZATION RESULTS - {filename}")
        print(f"{'='*60}")
        
        print(f"\nProcessed {len(categorized_transactions)} transactions")
        
        # Print sample categorized transactions
        print(f"\nSAMPLE CATEGORIZED TRANSACTIONS:")
        print(f"{'-'*60}")
        for i, transaction in enumerate(categorized_transactions[:10]):
            date = transaction.get('date', 'N/A')
            description = transaction.get('description', 'N/A')[:40]
            amount = transaction.get('amount', 'N/A')
            category = transaction.get('category', 'N/A')
            
            print(f"{date:<12} | {description:<40} | {amount:>10} | {category}")
            
        if len(categorized_transactions) > 10:
            print(f"... and {len(categorized_transactions) - 10} more transactions")
        
        # Print category summary
        print(f"\nCATEGORY SUMMARY:")
        print(f"{'-'*60}")
        print(f"{'Category':<15} | {'Count':<8} | {'Total Amount'}")
        print(f"{'-'*60}")
        
        sorted_categories = sorted(summary.items(), key=lambda x: x[1]['total'], reverse=True)
        
        for category, data in sorted_categories:
            count = data['count']
            total = data['total']
            print(f"{category:<15} | {count:<8} | ${total:,.2f}")
        
        total_amount = sum(data['total'] for data in summary.values())
        total_count = sum(data['count'] for data in summary.values())
        print(f"{'-'*60}")
        print(f"{'TOTAL':<15} | {total_count:<8} | ${total_amount:,.2f}")

def main():
    """Main function to process CSV files and categorize transactions."""
    categorizer = TransactionCategorizer()
    
    try:
        # Look for CSV files in current directory