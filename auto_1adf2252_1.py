```python
"""
Transaction Data Processing Module

This module provides comprehensive transaction data processing capabilities including:
- Transaction data validation (amount, date, description format checking)
- Duplicate detection using multiple criteria (amount, date, description similarity)
- Transaction description normalization for improved keyword matching
- Monthly summary statistics generation with spending trends analysis
- Category breakdown and analysis

The module is designed to be self-contained and handles various data quality issues
commonly found in financial transaction datasets.
"""

import json
import re
import hashlib
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import List, Dict, Any, Tuple, Optional
import difflib


class TransactionProcessor:
    def __init__(self):
        self.transactions = []
        self.validated_transactions = []
        self.duplicate_transactions = []
        
        # Common merchant name mappings for normalization
        self.merchant_mappings = {
            r'AMAZON.*': 'Amazon',
            r'WALMART.*': 'Walmart',
            r'TARGET.*': 'Target',
            r'STARBUCKS.*': 'Starbucks',
            r'MCDONALD.*': 'McDonalds',
            r'SHELL.*': 'Shell Gas',
            r'BP.*': 'BP Gas',
            r'CHEVRON.*': 'Chevron Gas',
            r'COSTCO.*': 'Costco',
            r'HOME DEPOT.*': 'Home Depot',
            r'SAFEWAY.*': 'Safeway',
            r'KROGER.*': 'Kroger',
        }
        
        # Category keywords for auto-categorization
        self.category_keywords = {
            'Groceries': ['safeway', 'kroger', 'whole foods', 'trader joe', 'grocery', 'food market'],
            'Gas': ['shell', 'bp', 'chevron', 'exxon', 'gas station', 'fuel'],
            'Restaurants': ['restaurant', 'cafe', 'pizza', 'burger', 'mcdonald', 'subway', 'starbucks'],
            'Shopping': ['amazon', 'target', 'walmart', 'costco', 'store', 'retail'],
            'Bills': ['electric', 'gas bill', 'water', 'internet', 'phone', 'insurance'],
            'Healthcare': ['pharmacy', 'doctor', 'medical', 'hospital', 'dental'],
            'Entertainment': ['netflix', 'spotify', 'movie', 'theater', 'game'],
            'Transportation': ['uber', 'lyft', 'taxi', 'parking', 'metro', 'transit']
        }

    def validate_transaction(self, transaction: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate a single transaction record."""
        errors = []
        
        # Check required fields
        required_fields = ['date', 'amount', 'description']
        for field in required_fields:
            if field not in transaction:
                errors.append(f"Missing required field: {field}")
        
        if errors:
            return False, errors
        
        # Validate date format
        try:
            if isinstance(transaction['date'], str):
                datetime.strptime(transaction['date'], '%Y-%m-%d')
        except ValueError:
            try:
                datetime.strptime(transaction['date'], '%m/%d/%Y')
                # Convert to standard format
                transaction['date'] = datetime.strptime(transaction['date'], '%m/%d/%Y').strftime('%Y-%m-%d')
            except ValueError:
                errors.append("Invalid date format. Use YYYY-MM-DD or MM/DD/YYYY")
        
        # Validate amount
        try:
            amount = float(transaction['amount'])
            if amount <= 0:
                errors.append("Amount must be positive")
        except (ValueError, TypeError):
            errors.append("Invalid amount format")
        
        # Validate description
        if not isinstance(transaction['description'], str) or len(transaction['description'].strip()) == 0:
            errors.append("Description must be a non-empty string")
        
        return len(errors) == 0, errors

    def normalize_description(self, description: str) -> str:
        """Normalize transaction description for better matching."""
        if not description:
            return ""
        
        # Convert to uppercase for consistency
        normalized = description.upper().strip()
        
        # Remove common transaction codes and references
        normalized = re.sub(r'\b\d{4}\*+\d{4}\b', '', normalized)  # Remove card numbers
        normalized = re.sub(r'\bREF#\s*\w+', '', normalized)       # Remove reference numbers
        normalized = re.sub(r'\b\d{6,}\b', '', normalized)         # Remove long numbers
        normalized = re.sub(r'\b[A-Z]{2}\d+[A-Z]*\b', '', normalized)  # Remove transaction IDs
        
        # Apply merchant mappings
        for pattern, replacement in self.merchant_mappings.items():
            if re.search(pattern, normalized):
                normalized = replacement.upper()
                break
        
        # Remove extra whitespace and special characters
        normalized = re.sub(r'[^\w\s]', ' ', normalized)
        normalized = ' '.join(normalized.split())
        
        return normalized

    def detect_duplicates(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect duplicate transactions using multiple criteria."""
        duplicates = []
        seen_hashes = set()
        
        for i, transaction in enumerate(transactions):
            # Create hash based on amount, date, and normalized description
            normalized_desc = self.normalize_description(transaction['description'])
            hash_string = f"{transaction['date']}-{transaction['amount']}-{normalized_desc}"
            transaction_hash = hashlib.md5(hash_string.encode()).hexdigest()
            
            if transaction_hash in seen_hashes:
                duplicates.append({
                    'index': i,
                    'transaction': transaction,
                    'hash': transaction_hash
                })
            else:
                seen_hashes.add(transaction_hash)
        
        # Additional similarity check for near-duplicates
        for i, trans1 in enumerate(transactions):
            for j, trans2 in enumerate(transactions[i+1:], i+1):
                if (abs(float(trans1['amount']) - float(trans2['amount'])) < 0.01 and
                    trans1['date'] == trans2['date']):
                    
                    desc1 = self.normalize_description(trans1['description'])
                    desc2 = self.normalize_description(trans2['description'])
                    similarity = difflib.SequenceMatcher(None, desc1, desc2).ratio()
                    
                    if similarity > 0.85:  # 85% similarity threshold
                        duplicate_entry = {
                            'index': j,
                            'transaction': trans2,
                            'similarity': similarity,
                            'matched_with': i
                        }
                        if duplicate_entry not in duplicates:
                            duplicates.append(duplicate_entry)
        
        return duplicates

    def categorize_transaction(self, description: str) -> str:
        """Auto-categorize transaction based on description."""
        normalized_desc = description.lower()
        
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword in normalized_desc:
                    return category
        
        return 'Other'

    def process_transactions(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Main processing pipeline for transaction data."""
        results = {
            'total_transactions': len(transactions),
            'valid_transactions': 0,
            'invalid_transactions': 0,
            'duplicate_transactions': 0,
            'validation_errors': [],
            'processing_summary': {}
        }
        
        try:
            # Step 1: Validate transactions
            print("Step 1: Validating transactions...")
            for i, transaction in enumerate(transactions):
                is_valid, errors = self.validate_transaction(transaction)
                if is_valid:
                    # Add normalized description and category
                    transaction['normalized_description'] = self