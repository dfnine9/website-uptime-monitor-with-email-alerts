```python
#!/usr/bin/env python3
"""
Transaction Data Processing Module

This module provides comprehensive transaction data validation, duplicate detection,
category aggregation, and monthly spending analysis functionality. It processes
financial transaction data to generate spending summaries with percentage breakdowns.

Features:
- Transaction data validation with type checking and required field verification
- Duplicate detection based on configurable fields (amount, date, description)
- Category-based spending totals calculation
- Monthly aggregated spending summaries with percentage analysis
- Comprehensive error handling and logging
- Self-contained implementation using only standard library components

Usage:
    python script.py

The script includes sample transaction data and demonstrates all functionality
including validation, duplicate handling, and report generation.
"""

import json
import sys
from collections import defaultdict, Counter
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import List, Dict, Any, Optional, Tuple
import hashlib
import traceback


class TransactionValidator:
    """Validates transaction data structure and content."""
    
    REQUIRED_FIELDS = {'id', 'amount', 'date', 'description', 'category'}
    
    @staticmethod
    def validate_transaction(transaction: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate a single transaction record.
        
        Args:
            transaction: Dictionary containing transaction data
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check required fields
            missing_fields = TransactionValidator.REQUIRED_FIELDS - set(transaction.keys())
            if missing_fields:
                return False, f"Missing required fields: {missing_fields}"
            
            # Validate amount
            try:
                amount = Decimal(str(transaction['amount']))
                if amount < 0:
                    return False, "Amount cannot be negative"
            except (InvalidOperation, ValueError):
                return False, f"Invalid amount format: {transaction['amount']}"
            
            # Validate date
            try:
                datetime.strptime(transaction['date'], '%Y-%m-%d')
            except ValueError:
                return False, f"Invalid date format: {transaction['date']} (expected YYYY-MM-DD)"
            
            # Validate category
            if not isinstance(transaction['category'], str) or not transaction['category'].strip():
                return False, "Category must be a non-empty string"
            
            # Validate description
            if not isinstance(transaction['description'], str):
                return False, "Description must be a string"
            
            return True, ""
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"


class DuplicateDetector:
    """Detects duplicate transactions based on configurable criteria."""
    
    def __init__(self, duplicate_fields: List[str] = None):
        """
        Initialize duplicate detector.
        
        Args:
            duplicate_fields: Fields to use for duplicate detection
        """
        self.duplicate_fields = duplicate_fields or ['amount', 'date', 'description']
    
    def generate_transaction_hash(self, transaction: Dict[str, Any]) -> str:
        """
        Generate a hash for duplicate detection.
        
        Args:
            transaction: Transaction dictionary
            
        Returns:
            Hash string for duplicate detection
        """
        try:
            # Create a normalized representation for hashing
            hash_data = []
            for field in self.duplicate_fields:
                if field in transaction:
                    if field == 'amount':
                        # Normalize amount to string with 2 decimal places
                        hash_data.append(f"{field}:{Decimal(str(transaction[field])):.2f}")
                    else:
                        hash_data.append(f"{field}:{str(transaction[field]).lower().strip()}")
            
            hash_string = "|".join(sorted(hash_data))
            return hashlib.md5(hash_string.encode()).hexdigest()
            
        except Exception as e:
            # Fallback to simple concatenation if hashing fails
            return str(hash(str(transaction.get('id', ''))))
    
    def detect_duplicates(self, transactions: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Detect and separate duplicate transactions.
        
        Args:
            transactions: List of transaction dictionaries
            
        Returns:
            Tuple of (unique_transactions, duplicate_transactions)
        """
        seen_hashes = {}
        unique_transactions = []
        duplicate_transactions = []
        
        for transaction in transactions:
            try:
                transaction_hash = self.generate_transaction_hash(transaction)
                
                if transaction_hash in seen_hashes:
                    duplicate_transactions.append(transaction)
                else:
                    seen_hashes[transaction_hash] = transaction
                    unique_transactions.append(transaction)
                    
            except Exception as e:
                print(f"Error processing transaction {transaction.get('id', 'unknown')}: {e}")
                # Include problematic transactions as unique to avoid data loss
                unique_transactions.append(transaction)
        
        return unique_transactions, duplicate_transactions


class CategoryAggregator:
    """Calculates category-based spending totals."""
    
    @staticmethod
    def calculate_category_totals(transactions: List[Dict[str, Any]]) -> Dict[str, Decimal]:
        """
        Calculate total spending by category.
        
        Args:
            transactions: List of validated transaction dictionaries
            
        Returns:
            Dictionary mapping categories to total amounts
        """
        category_totals = defaultdict(Decimal)
        
        for transaction in transactions:
            try:
                category = transaction['category'].strip().title()
                amount = Decimal(str(transaction['amount']))
                category_totals[category] += amount
            except Exception as e:
                print(f"Error processing transaction {transaction.get('id', 'unknown')}: {e}")
        
        return dict(category_totals)


class MonthlyAnalyzer:
    """Generates monthly spending summaries and analysis."""
    
    @staticmethod
    def generate_monthly_summary(transactions: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Generate monthly spending summaries with percentage breakdowns.
        
        Args:
            transactions: List of validated transaction dictionaries
            
        Returns:
            Dictionary with monthly summaries including totals and percentages
        """
        monthly_data = defaultdict(lambda: defaultdict(Decimal))
        
        # Aggregate data by month and category
        for transaction in transactions:
            try:
                date = datetime.strptime(transaction['date'], '%Y-%m-%d')
                month_key = date.strftime('%Y-%m')
                category = transaction['category'].strip().title()
                amount = Decimal(str(transaction['amount']))
                
                monthly_data[month_key][category] += amount
                
            except Exception as e:
                print(f"Error processing transaction {transaction.get('id', 'unknown')}: {e}")
        
        # Calculate percentages and totals
        monthly_summary = {}
        for month, categories in monthly_data.items():
            total_spending = sum(categories.values())
            
            category_breakdown = {}
            for category, amount in categories.items():
                percentage = (amount / total_spending * 100) if total_spending > 0 else Decimal('0')
                category_breakdown[category] = {
                    'amount': float(amount),
                    'percentage': float(percentage.quantize(Decimal('0.01')))
                }
            
            monthly_summary[month] = {
                'total_spending': float(total_spending),
                'categories': category_breakdown,
                'transaction_count': sum(1 for t in transactions 
                                       if datetime.strptime(t['date'], '%Y-%m-%d').strftime('%Y-%m') == month)
            }
        
        return monthly_summary


class TransactionProcessor:
    """Main processor that coordinates all transaction processing operations."""
    
    def __init__(self):
        """Initialize the transaction processor with all components."""
        self.validator = TransactionValidator()
        self.duplicate_detector = DuplicateDetector()
        self.category_aggregator = CategoryAggregator()
        self.monthly_analyzer = Monthly