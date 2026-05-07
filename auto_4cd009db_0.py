```python
"""
Bank Statement Transaction Classifier

This module parses CSV bank statements and automatically classifies transactions
into categories based on description keywords. It creates a comprehensive mapping
dictionary for common transaction types and provides detailed classification
results with spending summaries.

Features:
- Parses CSV files with flexible column detection
- Built-in category mapping for common merchants and transaction types
- Fuzzy keyword matching for transaction classification
- Spending analysis by category
- Error handling for malformed data
- Self-contained with no external dependencies beyond standard library

Usage: python script.py
"""

import csv
import re
from datetime import datetime
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Optional


class BankStatementClassifier:
    def __init__(self):
        self.category_mapping = self._create_category_mapping()
        self.transactions = []
        self.classified_transactions = []
    
    def _create_category_mapping(self) -> Dict[str, str]:
        """Create a comprehensive category mapping dictionary."""
        return {
            # Food & Dining
            'restaurant': 'Food & Dining',
            'cafe': 'Food & Dining',
            'coffee': 'Food & Dining',
            'pizza': 'Food & Dining',
            'burger': 'Food & Dining',
            'mcdonald': 'Food & Dining',
            'subway': 'Food & Dining',
            'starbucks': 'Food & Dining',
            'doordash': 'Food & Dining',
            'ubereats': 'Food & Dining',
            'grubhub': 'Food & Dining',
            'dining': 'Food & Dining',
            'food': 'Food & Dining',
            'bistro': 'Food & Dining',
            'grill': 'Food & Dining',
            
            # Groceries
            'grocery': 'Groceries',
            'supermarket': 'Groceries',
            'walmart': 'Groceries',
            'target': 'Groceries',
            'safeway': 'Groceries',
            'kroger': 'Groceries',
            'whole foods': 'Groceries',
            'costco': 'Groceries',
            'trader joe': 'Groceries',
            'market': 'Groceries',
            
            # Transportation
            'gas': 'Transportation',
            'fuel': 'Transportation',
            'shell': 'Transportation',
            'chevron': 'Transportation',
            'exxon': 'Transportation',
            'bp': 'Transportation',
            'uber': 'Transportation',
            'lyft': 'Transportation',
            'taxi': 'Transportation',
            'metro': 'Transportation',
            'transit': 'Transportation',
            'parking': 'Transportation',
            'toll': 'Transportation',
            
            # Shopping
            'amazon': 'Shopping',
            'ebay': 'Shopping',
            'mall': 'Shopping',
            'store': 'Shopping',
            'shop': 'Shopping',
            'retail': 'Shopping',
            'clothing': 'Shopping',
            'fashion': 'Shopping',
            'shoes': 'Shopping',
            
            # Utilities
            'electric': 'Utilities',
            'water': 'Utilities',
            'gas company': 'Utilities',
            'utility': 'Utilities',
            'power': 'Utilities',
            'energy': 'Utilities',
            
            # Entertainment
            'movie': 'Entertainment',
            'theater': 'Entertainment',
            'cinema': 'Entertainment',
            'netflix': 'Entertainment',
            'spotify': 'Entertainment',
            'gaming': 'Entertainment',
            'entertainment': 'Entertainment',
            'concert': 'Entertainment',
            'show': 'Entertainment',
            
            # Healthcare
            'medical': 'Healthcare',
            'doctor': 'Healthcare',
            'hospital': 'Healthcare',
            'pharmacy': 'Healthcare',
            'dental': 'Healthcare',
            'health': 'Healthcare',
            'clinic': 'Healthcare',
            'cvs': 'Healthcare',
            'walgreens': 'Healthcare',
            
            # Banking & Finance
            'bank': 'Banking & Finance',
            'atm': 'Banking & Finance',
            'fee': 'Banking & Finance',
            'interest': 'Banking & Finance',
            'transfer': 'Banking & Finance',
            'payment': 'Banking & Finance',
            'loan': 'Banking & Finance',
            'mortgage': 'Banking & Finance',
            'credit': 'Banking & Finance',
            
            # Insurance
            'insurance': 'Insurance',
            'auto insurance': 'Insurance',
            'health insurance': 'Insurance',
            'life insurance': 'Insurance',
            
            # Income
            'salary': 'Income',
            'payroll': 'Income',
            'deposit': 'Income',
            'refund': 'Income',
            'bonus': 'Income',
            'dividend': 'Income',
            
            # Subscriptions
            'subscription': 'Subscriptions',
            'monthly': 'Subscriptions',
            'adobe': 'Subscriptions',
            'microsoft': 'Subscriptions',
            'apple': 'Subscriptions',
            'google': 'Subscriptions',
        }
    
    def _normalize_description(self, description: str) -> str:
        """Normalize transaction description for better matching."""
        if not description:
            return ""
        
        # Convert to lowercase and remove extra whitespace
        normalized = re.sub(r'\s+', ' ', description.lower().strip())
        
        # Remove common prefixes/suffixes
        normalized = re.sub(r'^(purchase\s+|sale\s+|payment\s+to\s+)', '', normalized)
        normalized = re.sub(r'\s+(inc|llc|ltd|corp)\.?$', '', normalized)
        
        # Remove special characters except spaces and hyphens
        normalized = re.sub(r'[^\w\s\-]', ' ', normalized)
        
        return normalized.strip()
    
    def classify_transaction(self, description: str, amount: float) -> str:
        """Classify a transaction based on its description and amount."""
        normalized_desc = self._normalize_description(description)
        
        # Handle income (positive amounts or specific keywords)
        if amount > 0 and any(keyword in normalized_desc for keyword in ['salary', 'payroll', 'deposit', 'refund']):
            return 'Income'
        
        # Check for direct keyword matches
        for keyword, category in self.category_mapping.items():
            if keyword in normalized_desc:
                return category
        
        # Fallback categories based on amount patterns
        if abs(amount) > 1000:
            return 'Large Expense'
        elif abs(amount) < 10:
            return 'Small Purchase'
        
        return 'Other'
    
    def parse_csv_file(self, filename: str) -> bool:
        """Parse CSV bank statement file with flexible column detection."""
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                # Try to detect delimiter
                sample = file.read(1024)
                file.seek(0)
                
                delimiter = ',' if sample.count(',') > sample.count(';') else ';'
                
                reader = csv.DictReader(file, delimiter=delimiter)
                headers = [header.lower().strip() for header in reader.fieldnames or []]
                
                print(f"Detected headers: {headers}")
                
                # Map common header variations
                date_cols = ['date', 'transaction_date', 'posted_date', 'date_posted']
                desc_cols = ['description', 'memo', 'details', 'transaction_details', 'payee']
                amount_cols = ['amount', 'transaction_amount', 'debit', 'credit']
                
                date_col = next((col for col in headers if any(dc in col for dc in date_cols)), None)
                desc_col = next((col for col in headers if any(dc in col for dc in desc_cols)), None)
                amount_col = next((col for col in headers if any(ac in col for ac in