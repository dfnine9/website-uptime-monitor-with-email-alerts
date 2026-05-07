```python
"""
CSV Bank Statement Expense Categorizer

This module parses CSV bank statements and categorizes transactions based on
keyword matching rules. It creates a dictionary mapping transaction descriptions
to predefined expense categories such as groceries, dining, transportation, etc.

The script processes CSV files with transaction data and applies intelligent
keyword-based categorization to help with expense tracking and budgeting.

Usage: python script.py
"""

import csv
import re
import json
from typing import Dict, List, Tuple
from io import StringIO


def create_sample_csv() -> str:
    """Create a sample CSV bank statement for demonstration."""
    sample_data = """Date,Description,Amount,Type
2024-01-15,WALMART SUPERCENTER #1234,-125.67,DEBIT
2024-01-14,SHELL GAS STATION,-45.32,DEBIT
2024-01-13,STARBUCKS COFFEE #567,-8.75,DEBIT
2024-01-12,AMAZON.COM PURCHASE,-89.99,DEBIT
2024-01-11,MCDONALDS RESTAURANT,-12.45,DEBIT
2024-01-10,UBER RIDE 123456,-18.50,DEBIT
2024-01-09,TARGET STORE #789,-67.23,DEBIT
2024-01-08,SPOTIFY PREMIUM,-9.99,DEBIT
2024-01-07,NETFLIX SUBSCRIPTION,-15.99,DEBIT
2024-01-06,CHEVRON GAS STATION,-52.18,DEBIT
2024-01-05,WHOLE FOODS MARKET,-98.76,DEBIT
2024-01-04,LYFT RIDE 789123,-22.30,DEBIT
2024-01-03,COSTCO WHOLESALE,-156.89,DEBIT
2024-01-02,PANERA BREAD,-11.25,DEBIT
2024-01-01,VERIZON WIRELESS,-85.99,DEBIT"""
    return sample_data


def define_category_rules() -> Dict[str, List[str]]:
    """Define keyword rules for expense categorization."""
    return {
        "Groceries": [
            "walmart", "target", "costco", "kroger", "safeway", "whole foods",
            "trader joe", "grocery", "supermarket", "market", "food lion",
            "wegmans", "publix", "giant", "stop shop"
        ],
        "Dining": [
            "restaurant", "mcdonalds", "burger king", "starbucks", "coffee",
            "pizza", "panera", "chipotle", "subway", "taco bell", "kfc",
            "dominos", "dunkin", "cafe", "bistro", "diner"
        ],
        "Transportation": [
            "gas", "shell", "chevron", "exxon", "bp", "uber", "lyft",
            "taxi", "metro", "bus", "train", "parking", "toll",
            "auto", "car wash", "mechanic"
        ],
        "Entertainment": [
            "netflix", "spotify", "hulu", "disney", "amazon prime",
            "theater", "cinema", "movie", "concert", "game", "steam"
        ],
        "Utilities": [
            "electric", "gas company", "water", "internet", "verizon",
            "at&t", "comcast", "spectrum", "utility", "phone", "wireless"
        ],
        "Shopping": [
            "amazon", "ebay", "best buy", "apple store", "clothing",
            "department store", "mall", "online", "retail"
        ],
        "Healthcare": [
            "pharmacy", "cvs", "walgreens", "hospital", "doctor",
            "medical", "dental", "clinic", "urgent care"
        ],
        "Other": []  # Catch-all category
    }


def normalize_description(description: str) -> str:
    """Normalize transaction description for better matching."""
    try:
        # Convert to lowercase and remove extra whitespace
        normalized = re.sub(r'\s+', ' ', description.lower().strip())
        
        # Remove common transaction codes and numbers
        normalized = re.sub(r'#\d+', '', normalized)
        normalized = re.sub(r'\d{10,}', '', normalized)
        
        # Remove special characters except spaces and hyphens
        normalized = re.sub(r'[^\w\s\-]', ' ', normalized)
        
        return normalized.strip()
    except Exception as e:
        print(f"Warning: Error normalizing description '{description}': {e}")
        return description.lower()


def categorize_transaction(description: str, category_rules: Dict[str, List[str]]) -> str:
    """Categorize a transaction based on its description."""
    try:
        normalized_desc = normalize_description(description)
        
        # Check each category's keywords
        for category, keywords in category_rules.items():
            if category == "Other":
                continue
            
            for keyword in keywords:
                if keyword.lower() in normalized_desc:
                    return category
        
        # If no match found, return "Other"
        return "Other"
    
    except Exception as e:
        print(f"Warning: Error categorizing transaction '{description}': {e}")
        return "Other"


def parse_csv_bank_statement(csv_content: str) -> List[Dict[str, str]]:
    """Parse CSV bank statement content and return list of transactions."""
    transactions = []
    
    try:
        csv_reader = csv.DictReader(StringIO(csv_content))
        
        for row_num, row in enumerate(csv_reader, start=2):
            try:
                # Validate required fields
                if 'Description' not in row or not row['Description'].strip():
                    print(f"Warning: Missing description in row {row_num}")
                    continue
                
                transactions.append({
                    'date': row.get('Date', '').strip(),
                    'description': row.get('Description', '').strip(),
                    'amount': row.get('Amount', '').strip(),
                    'type': row.get('Type', '').strip()
                })
                
            except Exception as e:
                print(f"Warning: Error processing row {row_num}: {e}")
                continue
                
    except Exception as e:
        print(f"Error reading CSV content: {e}")
        raise
    
    return transactions


def create_expense_mapping(transactions: List[Dict[str, str]], 
                         category_rules: Dict[str, List[str]]) -> Dict[str, str]:
    """Create mapping of transaction descriptions to expense categories."""
    expense_mapping = {}
    
    try:
        for transaction in transactions:
            description = transaction['description']
            category = categorize_transaction(description, category_rules)
            expense_mapping[description] = category
            
    except Exception as e:
        print(f"Error creating expense mapping: {e}")
        raise
    
    return expense_mapping


def print_categorization_summary(expense_mapping: Dict[str, str]) -> None:
    """Print a summary of the categorization results."""
    try:
        # Count transactions per category
        category_counts = {}
        for category in expense_mapping.values():
            category_counts[category] = category_counts.get(category, 0) + 1
        
        print("\n" + "="*60)
        print("EXPENSE CATEGORIZATION SUMMARY")
        print("="*60)
        
        print(f"\nTotal transactions processed: {len(expense_mapping)}")
        print(f"Categories found: {len(category_counts)}")
        
        print("\nTransactions per category:")
        for category, count in sorted(category_counts.items()):
            print(f"  {category}: {count} transactions")
        
        print("\n" + "="*60)
        print("DETAILED TRANSACTION MAPPING")
        print("="*60)
        
        # Group by category for better readability
        for category in sorted(set(expense_mapping.values())):
            print(f"\n{category.upper()}:")
            for description, cat in expense_mapping.items():
                if cat == category:
                    print(f"  • {description}")
    
    except Exception as e