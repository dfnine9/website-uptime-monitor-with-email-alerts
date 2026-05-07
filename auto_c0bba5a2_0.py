```python
"""
Transaction Categorizer and Expense Analyzer

This module reads CSV files containing transaction data, categorizes transactions
based on merchant names using regex patterns, and generates expense breakdowns
by category. It processes financial data to provide insights into spending patterns.

The script expects CSV files with columns containing merchant/description data
and transaction amounts. It uses predefined regex patterns to automatically
categorize expenses into logical groups like groceries, restaurants, gas, etc.

Usage:
    python script.py

The script will look for CSV files in the current directory and process them
to generate categorized expense reports.
"""

import csv
import re
import os
import sys
from typing import Dict, List, Tuple, Optional
from decimal import Decimal, InvalidOperation


class TransactionCategorizer:
    """Categorizes financial transactions based on merchant names using regex patterns."""
    
    def __init__(self):
        """Initialize the categorizer with predefined merchant patterns."""
        self.category_patterns = {
            'Groceries': [
                r'walmart|target|kroger|safeway|whole foods|trader joe|costco|sam\'s club',
                r'grocery|supermarket|food.*store|market.*place'
            ],
            'Restaurants': [
                r'mcdonald|burger king|subway|starbucks|chipotle|pizza|restaurant',
                r'cafe|diner|grill|bistro|eatery|food.*truck'
            ],
            'Gas/Fuel': [
                r'shell|exxon|bp|chevron|mobil|texaco|arco|circle k',
                r'gas.*station|fuel|petroleum'
            ],
            'Entertainment': [
                r'netflix|spotify|amazon prime|disney|hulu|movie|theater|cinema',
                r'game|entertainment|amusement|park'
            ],
            'Shopping': [
                r'amazon|ebay|best buy|home depot|lowes|ikea|macy|nordstrom',
                r'store|shop|retail|mall|outlet'
            ],
            'Healthcare': [
                r'pharmacy|cvs|walgreens|rite aid|hospital|clinic|medical|doctor|dentist',
                r'health|dental|vision|prescription'
            ],
            'Transportation': [
                r'uber|lyft|taxi|bus|train|subway|airline|airport|parking',
                r'transport|metro|transit'
            ],
            'Utilities': [
                r'electric|water|gas.*utility|internet|phone|cable|telecom',
                r'utility|power|energy'
            ]
        }
        
        self.compiled_patterns = {}
        for category, patterns in self.category_patterns.items():
            self.compiled_patterns[category] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]
    
    def categorize_transaction(self, merchant_name: str) -> str:
        """
        Categorize a transaction based on merchant name.
        
        Args:
            merchant_name: The merchant or description string
            
        Returns:
            Category name or 'Other' if no pattern matches
        """
        if not merchant_name:
            return 'Other'
        
        for category, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(merchant_name):
                    return category
        
        return 'Other'


class CSVProcessor:
    """Processes CSV files containing transaction data."""
    
    def __init__(self, categorizer: TransactionCategorizer):
        """Initialize with a transaction categorizer."""
        self.categorizer = categorizer
    
    def detect_csv_structure(self, filepath: str) -> Optional[Tuple[str, str]]:
        """
        Detect the structure of a CSV file to identify merchant and amount columns.
        
        Args:
            filepath: Path to the CSV file
            
        Returns:
            Tuple of (merchant_column, amount_column) names or None if not detected
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                headers = next(reader)
                
                merchant_col = None
                amount_col = None
                
                # Look for common column names
                for header in headers:
                    header_lower = header.lower().strip()
                    
                    if not merchant_col and any(term in header_lower for term in 
                                              ['merchant', 'description', 'payee', 'vendor', 'store']):
                        merchant_col = header
                    
                    if not amount_col and any(term in header_lower for term in 
                                            ['amount', 'total', 'charge', 'debit', 'credit']):
                        amount_col = header
                
                return (merchant_col, amount_col) if merchant_col and amount_col else None
                
        except Exception as e:
            print(f"Error detecting CSV structure for {filepath}: {e}")
            return None
    
    def process_csv_file(self, filepath: str) -> Dict[str, Decimal]:
        """
        Process a CSV file and return categorized expenses.
        
        Args:
            filepath: Path to the CSV file
            
        Returns:
            Dictionary mapping categories to total amounts
        """
        structure = self.detect_csv_structure(filepath)
        if not structure:
            print(f"Could not detect CSV structure for {filepath}")
            return {}
        
        merchant_col, amount_col = structure
        category_totals = {}
        processed_count = 0
        
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    try:
                        merchant = row.get(merchant_col, '').strip()
                        amount_str = row.get(amount_col, '0').strip()
                        
                        # Clean amount string (remove currency symbols, parentheses)
                        amount_str = re.sub(r'[\$,\(\)]', '', amount_str)
                        amount_str = amount_str.replace('(', '-')  # Handle negative amounts in parentheses
                        
                        amount = Decimal(amount_str)
                        
                        # Only process expenses (negative amounts or positive depending on format)
                        if amount != 0:
                            category = self.categorizer.categorize_transaction(merchant)
                            
                            if category not in category_totals:
                                category_totals[category] = Decimal('0')
                            
                            category_totals[category] += abs(amount)  # Use absolute value for expenses
                            processed_count += 1
                    
                    except (InvalidOperation, ValueError, KeyError) as e:
                        continue  # Skip invalid rows
                        
            print(f"Processed {processed_count} transactions from {filepath}")
            return category_totals
            
        except Exception as e:
            print(f"Error processing {filepath}: {e}")
            return {}


def find_csv_files() -> List[str]:
    """Find all CSV files in the current directory."""
    csv_files = []
    try:
        for filename in os.listdir('.'):
            if filename.lower().endswith('.csv'):
                csv_files.append(filename)
    except Exception as e:
        print(f"Error scanning directory: {e}")
    
    return csv_files


def generate_expense_report(all_categories: Dict[str, Decimal]) -> None:
    """
    Generate and print a formatted expense report.
    
    Args:
        all_categories: Dictionary mapping categories to total amounts
    """
    if not all_categories:
        print("No transactions found to categorize.")
        return
    
    # Calculate total expenses
    total_amount = sum(all_categories.values())
    
    print("\n" + "="*60)
    print("EXPENSE BREAKDOWN BY CATEGORY")
    print("="*60)
    
    # Sort categories by amount (descending)
    sorted_categories = sorted(all_categories.items(), key=lambda x: x[1], reverse=True)
    
    for category, amount in sorted_categories:
        percentage = (amount / total_amount * 100) if total_amount > 0 else 0
        print(f"{category:<20} ${amount:>