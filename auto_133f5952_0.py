```python
#!/usr/bin/env python3
"""
CSV Transaction Categorizer

This module parses CSV transaction files and automatically categorizes transactions
based on configurable keyword matching and regex patterns. It supports common
expense categories like groceries, gas, restaurants, utilities, etc.

The script reads CSV files with columns: date, description, amount, account
and outputs categorized transactions with assigned categories based on
description text matching against predefined patterns.

Usage:
    python script.py

The script expects a 'transactions.csv' file in the same directory.
Sample CSV format:
    date,description,amount,account
    2024-01-15,"GROCERY STORE #123",-45.67,checking
    2024-01-16,"SHELL GAS STATION",-32.50,credit
"""

import csv
import re
import sys
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Transaction:
    """Represents a single financial transaction"""
    date: str
    description: str
    amount: float
    account: str
    category: str = "Uncategorized"


class TransactionCategorizer:
    """Categorizes transactions based on keyword and regex pattern matching"""
    
    def __init__(self):
        self.category_patterns = self._initialize_patterns()
    
    def _initialize_patterns(self) -> Dict[str, List[str]]:
        """Initialize category patterns with keywords and regex patterns"""
        return {
            "Groceries": [
                r"grocery|supermarket|food|market",
                r"walmart|target|costco|kroger|safeway",
                r"whole foods|trader joe|aldi",
                r"food lion|publix|wegmans"
            ],
            "Gas": [
                r"shell|exxon|mobil|chevron|bp|texaco",
                r"gas station|fuel|petroleum",
                r"pilot|loves|circle k|speedway"
            ],
            "Restaurants": [
                r"restaurant|cafe|diner|bistro",
                r"mcdonald|burger|pizza|taco|subway",
                r"starbucks|dunkin|coffee",
                r"dining|food truck|bar & grill"
            ],
            "Utilities": [
                r"electric|power|gas company|water",
                r"utility|duke energy|pg&e|con edison",
                r"internet|cable|phone|wireless",
                r"verizon|att|comcast|spectrum"
            ],
            "Shopping": [
                r"amazon|ebay|online|store",
                r"department|clothing|apparel",
                r"home depot|lowes|best buy",
                r"pharmacy|cvs|walgreens"
            ],
            "Transportation": [
                r"uber|lyft|taxi|bus|train",
                r"parking|toll|metro|transit",
                r"airline|flight|airport"
            ],
            "Healthcare": [
                r"medical|doctor|hospital|clinic",
                r"pharmacy|prescription|dental",
                r"insurance|health|medicare"
            ],
            "Entertainment": [
                r"movie|theater|cinema|netflix",
                r"spotify|gaming|entertainment",
                r"concert|sports|tickets"
            ],
            "Banking": [
                r"fee|atm|overdraft|interest",
                r"transfer|deposit|withdrawal",
                r"maintenance|service charge"
            ]
        }
    
    def categorize_transaction(self, description: str) -> str:
        """
        Categorize a transaction based on its description
        
        Args:
            description: Transaction description text
            
        Returns:
            Category name or "Uncategorized" if no match found
        """
        description_lower = description.lower().strip()
        
        for category, patterns in self.category_patterns.items():
            for pattern in patterns:
                if re.search(pattern, description_lower, re.IGNORECASE):
                    return category
        
        return "Uncategorized"
    
    def add_custom_pattern(self, category: str, pattern: str) -> None:
        """Add a custom pattern to a category"""
        if category not in self.category_patterns:
            self.category_patterns[category] = []
        self.category_patterns[category].append(pattern)


def parse_csv_file(filepath: str) -> List[Transaction]:
    """
    Parse CSV transaction file and return list of Transaction objects
    
    Args:
        filepath: Path to CSV file
        
    Returns:
        List of Transaction objects
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If CSV format is invalid
    """
    transactions = []
    
    try:
        with open(filepath, 'r', newline='', encoding='utf-8') as csvfile:
            # Detect delimiter
            sample = csvfile.read(1024)
            csvfile.seek(0)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
            reader = csv.DictReader(csvfile, delimiter=delimiter)
            
            # Validate required columns
            required_columns = {'date', 'description', 'amount', 'account'}
            if not required_columns.issubset(set(reader.fieldnames)):
                missing = required_columns - set(reader.fieldnames)
                raise ValueError(f"Missing required columns: {missing}")
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    # Clean and validate data
                    date = row['date'].strip()
                    description = row['description'].strip()
                    amount = float(row['amount'].replace('$', '').replace(',', ''))
                    account = row['account'].strip()
                    
                    if not description:
                        print(f"Warning: Empty description at row {row_num}")
                        continue
                    
                    transactions.append(Transaction(date, description, amount, account))
                    
                except (ValueError, KeyError) as e:
                    print(f"Error parsing row {row_num}: {e}")
                    continue
                    
    except FileNotFoundError:
        raise FileNotFoundError(f"Transaction file not found: {filepath}")
    except Exception as e:
        raise ValueError(f"Error reading CSV file: {e}")
    
    return transactions


def create_sample_data() -> None:
    """Create a sample transactions.csv file for testing"""
    sample_data = [
        ['date', 'description', 'amount', 'account'],
        ['2024-01-15', 'KROGER GROCERY STORE #123', '-45.67', 'checking'],
        ['2024-01-16', 'SHELL GAS STATION', '-32.50', 'credit'],
        ['2024-01-17', 'STARBUCKS COFFEE #456', '-8.25', 'debit'],
        ['2024-01-18', 'DUKE ENERGY ELECTRIC BILL', '-125.00', 'checking'],
        ['2024-01-19', 'AMAZON ONLINE PURCHASE', '-67.89', 'credit'],
        ['2024-01-20', 'UBER RIDE TO AIRPORT', '-25.50', 'credit'],
        ['2024-01-21', 'DENTIST OFFICE VISIT', '-150.00', 'checking'],
        ['2024-01-22', 'NETFLIX MONTHLY SUB', '-15.99', 'credit'],
        ['2024-01-23', 'ATM WITHDRAWAL FEE', '-3.50', 'checking'],
        ['2024-01-24', 'LOCAL PIZZA PLACE', '-28.75', 'debit']
    ]
    
    with open('transactions.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(sample_data)


def print_categorization_summary(transactions: List[Transaction]) -> None:
    """Print summary of categorization results"""
    category_totals = {}
    category_counts = {}
    
    for transaction in transactions:
        category = transaction.category
        category_totals[category] = category_totals.get(category, 0) + abs(transaction.amount)
        category_