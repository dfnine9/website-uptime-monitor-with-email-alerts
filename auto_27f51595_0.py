```python
#!/usr/bin/env python3
"""
Transaction Categorization System

This module parses CSV transaction data and automatically categorizes transactions
using rule-based matching with regex patterns and keywords. It includes predefined
categorization rules for common expense categories like groceries, gas, dining, etc.

The script processes transaction data from a CSV file (or creates sample data),
applies categorization rules based on transaction descriptions, and outputs
the categorized results with statistics.

Usage:
    python script.py

Dependencies:
    - Standard library only (csv, re, sys, os)
"""

import csv
import re
import sys
import os
from typing import Dict, List, Tuple, Optional
from collections import defaultdict


class TransactionCategorizer:
    """Handles transaction categorization using regex and keyword matching."""
    
    def __init__(self):
        """Initialize with predefined categorization rules."""
        self.rules = self._create_categorization_rules()
        self.transactions = []
        self.categorized_transactions = []
    
    def _create_categorization_rules(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Create categorization rules dictionary with regex patterns and keywords.
        
        Returns:
            Dict mapping categories to their matching rules
        """
        return {
            'Groceries': {
                'keywords': ['grocery', 'supermarket', 'food', 'market', 'walmart', 'target', 'safeway', 'kroger'],
                'regex_patterns': [r'\b(whole\s*foods|trader\s*joe)', r'market$', r'grocery']
            },
            'Gas & Fuel': {
                'keywords': ['gas', 'fuel', 'shell', 'chevron', 'bp', 'exxon', 'mobil', 'arco'],
                'regex_patterns': [r'\b(gas|fuel)\b', r'shell|chevron|bp|exxon|mobil']
            },
            'Dining & Restaurants': {
                'keywords': ['restaurant', 'cafe', 'coffee', 'pizza', 'burger', 'diner', 'starbucks', 'mcdonalds'],
                'regex_patterns': [r'\b(restaurant|cafe|coffee)\b', r'(pizza|burger|diner)']
            },
            'Transportation': {
                'keywords': ['uber', 'lyft', 'taxi', 'metro', 'bus', 'train', 'parking', 'toll'],
                'regex_patterns': [r'\b(uber|lyft|taxi)\b', r'(metro|bus|train|parking)']
            },
            'Shopping': {
                'keywords': ['amazon', 'ebay', 'store', 'shop', 'retail', 'purchase'],
                'regex_patterns': [r'\b(amazon|ebay)\b', r'(store|shop|retail)']
            },
            'Utilities': {
                'keywords': ['electric', 'gas bill', 'water', 'internet', 'phone', 'cable', 'utility'],
                'regex_patterns': [r'\b(electric|water|internet|phone|cable|utility)\b']
            },
            'Healthcare': {
                'keywords': ['doctor', 'hospital', 'pharmacy', 'medical', 'dental', 'vision'],
                'regex_patterns': [r'\b(doctor|hospital|pharmacy|medical|dental)\b']
            },
            'Entertainment': {
                'keywords': ['movie', 'theater', 'netflix', 'spotify', 'game', 'entertainment'],
                'regex_patterns': [r'\b(movie|theater|netflix|spotify|game)\b']
            }
        }
    
    def categorize_transaction(self, description: str) -> str:
        """
        Categorize a single transaction based on its description.
        
        Args:
            description: Transaction description string
            
        Returns:
            Category name or 'Other' if no match found
        """
        description_lower = description.lower().strip()
        
        for category, rules in self.rules.items():
            # Check keywords
            for keyword in rules['keywords']:
                if keyword.lower() in description_lower:
                    return category
            
            # Check regex patterns
            for pattern in rules['regex_patterns']:
                if re.search(pattern, description_lower, re.IGNORECASE):
                    return category
        
        return 'Other'
    
    def load_csv_data(self, file_path: str) -> bool:
        """
        Load transaction data from CSV file.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                self.transactions = list(reader)
                return True
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
            return False
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return False
    
    def create_sample_data(self) -> None:
        """Create sample transaction data for demonstration."""
        sample_transactions = [
            {'date': '2024-01-15', 'description': 'Whole Foods Market', 'amount': '-89.45'},
            {'date': '2024-01-16', 'description': 'Shell Gas Station', 'amount': '-45.20'},
            {'date': '2024-01-17', 'description': 'Starbucks Coffee', 'amount': '-5.85'},
            {'date': '2024-01-18', 'description': 'Amazon Purchase', 'amount': '-125.99'},
            {'date': '2024-01-19', 'description': 'Electric Company Bill', 'amount': '-78.50'},
            {'date': '2024-01-20', 'description': 'Uber Ride', 'amount': '-18.75'},
            {'date': '2024-01-21', 'description': 'Local Grocery Store', 'amount': '-67.80'},
            {'date': '2024-01-22', 'description': 'Netflix Subscription', 'amount': '-15.99'},
            {'date': '2024-01-23', 'description': 'Dr. Smith Medical', 'amount': '-150.00'},
            {'date': '2024-01-24', 'description': 'Pizza Palace', 'amount': '-28.45'},
            {'date': '2024-01-25', 'description': 'Parking Meter', 'amount': '-2.50'},
            {'date': '2024-01-26', 'description': 'Unknown Vendor XYZ', 'amount': '-35.00'}
        ]
        self.transactions = sample_transactions
    
    def process_transactions(self) -> None:
        """Process all transactions and assign categories."""
        self.categorized_transactions = []
        
        for transaction in self.transactions:
            try:
                categorized = transaction.copy()
                description = transaction.get('description', '')
                categorized['category'] = self.categorize_transaction(description)
                self.categorized_transactions.append(categorized)
            except Exception as e:
                print(f"Error processing transaction: {transaction}. Error: {e}")
    
    def generate_statistics(self) -> Dict[str, Dict]:
        """
        Generate categorization statistics.
        
        Returns:
            Dictionary with category statistics
        """
        stats = defaultdict(lambda: {'count': 0, 'total_amount': 0.0})
        
        for transaction in self.categorized_transactions:
            category = transaction['category']
            try:
                amount = float(transaction.get('amount', 0))
                stats[category]['count'] += 1
                stats[category]['total_amount'] += abs(amount)  # Use absolute value for spending
            except (ValueError, TypeError):
                stats[category]['count'] += 1
        
        return dict(stats)
    
    def print_results(self) -> None:
        """Print categorized transactions and statistics to stdout."""
        print("=" * 80)
        print("TRANSACTION CATEGORIZATION RESULTS")
        print("=" * 80)