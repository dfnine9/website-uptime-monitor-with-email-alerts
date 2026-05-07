```python
"""
Transaction Categorization System

This module implements keyword-based transaction categorization using merchant name patterns.
It parses transaction data and applies predefined categories based on merchant names.
For example, 'STARBUCKS' transactions are categorized as 'Food & Dining',
'SHELL' transactions as 'Gas & Transportation', etc.

The system includes:
- Predefined merchant-to-category mapping
- Fuzzy matching for partial merchant names
- Transaction parsing and categorization
- Error handling for malformed data
- Results output to stdout

Usage: python script.py
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class TransactionCategorizer:
    """Categorizes transactions based on merchant name patterns."""
    
    def __init__(self):
        """Initialize categorizer with predefined merchant patterns."""
        self.category_patterns = {
            'Food & Dining': [
                'STARBUCKS', 'MCDONALDS', 'SUBWAY', 'CHIPOTLE', 'DOMINOS',
                'PIZZA', 'RESTAURANT', 'CAFE', 'DINER', 'BISTRO',
                'BURGER', 'TACO', 'SUSHI', 'BBQ', 'GRILL'
            ],
            'Gas & Transportation': [
                'SHELL', 'EXXON', 'MOBIL', 'BP', 'CHEVRON', 'CITGO',
                'UBER', 'LYFT', 'TAXI', 'BUS', 'METRO', 'TRANSIT',
                'PARKING', 'TOLL', 'GAS STATION'
            ],
            'Groceries': [
                'WALMART', 'TARGET', 'SAFEWAY', 'KROGER', 'PUBLIX',
                'WHOLE FOODS', 'TRADER JOES', 'COSTCO', 'SAMS CLUB',
                'GROCERY', 'SUPERMARKET', 'MARKET'
            ],
            'Shopping': [
                'AMAZON', 'EBAY', 'BEST BUY', 'HOME DEPOT', 'LOWES',
                'MACYS', 'NORDSTROM', 'GAP', 'NIKE', 'APPLE STORE',
                'MALL', 'OUTLET', 'RETAIL'
            ],
            'Healthcare': [
                'PHARMACY', 'CVS', 'WALGREENS', 'RITE AID', 'HOSPITAL',
                'CLINIC', 'DOCTOR', 'DENTAL', 'MEDICAL', 'HEALTH'
            ],
            'Entertainment': [
                'NETFLIX', 'SPOTIFY', 'CINEMA', 'THEATER', 'MOVIES',
                'GAME', 'ENTERTAINMENT', 'CONCERT', 'SPORTS', 'GYM'
            ],
            'Utilities': [
                'ELECTRIC', 'POWER', 'WATER', 'GAS COMPANY', 'INTERNET',
                'CABLE', 'PHONE', 'UTILITY', 'ENERGY', 'TELECOM'
            ],
            'Banking & Finance': [
                'BANK', 'ATM', 'CREDIT', 'LOAN', 'FINANCE', 'INVESTMENT',
                'INSURANCE', 'MORTGAGE', 'FEE'
            ]
        }
        
        # Compile regex patterns for better performance
        self.compiled_patterns = {}
        for category, patterns in self.category_patterns.items():
            regex_pattern = '|'.join([re.escape(pattern) for pattern in patterns])
            self.compiled_patterns[category] = re.compile(regex_pattern, re.IGNORECASE)
    
    def categorize_merchant(self, merchant_name: str) -> str:
        """
        Categorize a merchant based on name patterns.
        
        Args:
            merchant_name: The merchant name to categorize
            
        Returns:
            Category name or 'Other' if no match found
        """
        if not merchant_name:
            return 'Other'
        
        merchant_clean = merchant_name.strip().upper()
        
        # Check each category pattern
        for category, pattern in self.compiled_patterns.items():
            if pattern.search(merchant_clean):
                return category
        
        return 'Other'
    
    def parse_transaction_line(self, line: str) -> Optional[Dict]:
        """
        Parse a transaction line in CSV format.
        Expected format: date,amount,merchant,description
        
        Args:
            line: Transaction line to parse
            
        Returns:
            Parsed transaction dict or None if invalid
        """
        try:
            parts = [part.strip().strip('"') for part in line.split(',')]
            if len(parts) < 3:
                return None
            
            # Parse date
            date_str = parts[0]
            try:
                transaction_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                try:
                    transaction_date = datetime.strptime(date_str, '%m/%d/%Y').date()
                except ValueError:
                    transaction_date = datetime.now().date()
            
            # Parse amount
            amount_str = parts[1].replace('$', '').replace(',', '')
            try:
                amount = float(amount_str)
            except ValueError:
                amount = 0.0
            
            # Extract merchant and description
            merchant = parts[2] if len(parts) > 2 else 'Unknown'
            description = parts[3] if len(parts) > 3 else merchant
            
            return {
                'date': transaction_date.isoformat(),
                'amount': amount,
                'merchant': merchant,
                'description': description
            }
            
        except Exception as e:
            print(f"Error parsing line '{line}': {e}")
            return None
    
    def categorize_transactions(self, transactions: List[Dict]) -> List[Dict]:
        """
        Categorize a list of transactions.
        
        Args:
            transactions: List of transaction dictionaries
            
        Returns:
            List of transactions with categories added
        """
        categorized = []
        
        for transaction in transactions:
            try:
                merchant = transaction.get('merchant', '')
                category = self.categorize_merchant(merchant)
                
                categorized_transaction = transaction.copy()
                categorized_transaction['category'] = category
                categorized.append(categorized_transaction)
                
            except Exception as e:
                print(f"Error categorizing transaction {transaction}: {e}")
                continue
        
        return categorized


def generate_sample_transactions() -> List[str]:
    """Generate sample transaction data for testing."""
    sample_data = [
        "2024-01-15,$4.75,STARBUCKS COFFEE,Coffee purchase",
        "2024-01-16,$45.20,SHELL GAS STATION,Gas fill-up",
        "2024-01-17,$127.89,WALMART SUPERCENTER,Grocery shopping",
        "2024-01-18,$12.99,NETFLIX STREAMING,Monthly subscription",
        "2024-01-19,$67.43,AMAZON PURCHASE,Online shopping",
        "2024-01-20,$8.50,MCDONALDS RESTAURANT,Fast food",
        "2024-01-21,$15.75,UBER RIDE,Transportation",
        "2024-01-22,$89.12,TARGET STORE,Retail shopping",
        "2024-01-23,$25.60,CVS PHARMACY,Prescription pickup",
        "2024-01-24,$156.78,WHOLE FOODS MARKET,Organic groceries",
        "2024-01-25,$3.50,METRO TRANSIT,Bus fare",
        "2024-01-26,$45.00,CHIPOTLE MEXICAN GRILL,Lunch",
        "2024-01-27,$78.90,EXXON MOBIL,Gas station",
        "2024-01-28,$234.56,HOME DEPOT,Home improvement",
        "2024-01-29,$19.99,SPOTIFY PREMIUM,Music subscription"
    ]
    return sample_data


def print