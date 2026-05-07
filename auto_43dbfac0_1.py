```python
"""
Transaction Data Processing Module

This module provides functionality to validate and process transaction data,
handling common edge cases such as duplicate transactions and negative amounts.
It categorizes transactions and stores results in a structured format.

Features:
- Transaction validation (amount, ID, timestamp)
- Duplicate detection and removal
- Negative amount handling
- Transaction categorization by amount ranges
- Structured data storage and retrieval
- Comprehensive error handling

Usage:
    python script.py
"""

import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import random
import uuid


class TransactionCategory(Enum):
    """Transaction categories based on amount ranges."""
    MICRO = "micro"          # 0-10
    SMALL = "small"          # 10-100
    MEDIUM = "medium"        # 100-1000
    LARGE = "large"          # 1000-10000
    ENTERPRISE = "enterprise"  # 10000+


@dataclass
class Transaction:
    """Represents a financial transaction."""
    id: str
    amount: float
    timestamp: datetime
    description: str
    merchant: Optional[str] = None
    category: Optional[TransactionCategory] = None
    
    def __post_init__(self):
        """Post-initialization validation."""
        if not isinstance(self.timestamp, datetime):
            if isinstance(self.timestamp, str):
                self.timestamp = datetime.fromisoformat(self.timestamp)
            else:
                raise ValueError(f"Invalid timestamp format: {self.timestamp}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction to dictionary for JSON serialization."""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        result['category'] = self.category.value if self.category else None
        return result


class TransactionProcessor:
    """Main class for processing and validating transaction data."""
    
    def __init__(self):
        self.transactions: List[Transaction] = []
        self.duplicate_count = 0
        self.invalid_count = 0
        self.processed_hashes = set()
    
    def _generate_transaction_hash(self, transaction: Transaction) -> str:
        """Generate a hash for duplicate detection."""
        hash_string = f"{transaction.amount}_{transaction.timestamp.isoformat()}_{transaction.description}"
        return hashlib.md5(hash_string.encode()).hexdigest()
    
    def _categorize_by_amount(self, amount: float) -> TransactionCategory:
        """Categorize transaction based on amount."""
        abs_amount = abs(amount)
        if abs_amount <= 10:
            return TransactionCategory.MICRO
        elif abs_amount <= 100:
            return TransactionCategory.SMALL
        elif abs_amount <= 1000:
            return TransactionCategory.MEDIUM
        elif abs_amount <= 10000:
            return TransactionCategory.LARGE
        else:
            return TransactionCategory.ENTERPRISE
    
    def validate_transaction(self, transaction_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate transaction data.
        
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        try:
            # Check required fields
            required_fields = ['id', 'amount', 'timestamp', 'description']
            for field in required_fields:
                if field not in transaction_data:
                    return False, f"Missing required field: {field}"
            
            # Validate amount
            amount = transaction_data['amount']
            if not isinstance(amount, (int, float)):
                try:
                    amount = float(amount)
                except (ValueError, TypeError):
                    return False, f"Invalid amount format: {amount}"
            
            # Check for zero amount
            if amount == 0:
                return False, "Transaction amount cannot be zero"
            
            # Validate timestamp
            timestamp = transaction_data['timestamp']
            if isinstance(timestamp, str):
                try:
                    timestamp = datetime.fromisoformat(timestamp)
                except ValueError:
                    return False, f"Invalid timestamp format: {timestamp}"
            elif not isinstance(timestamp, datetime):
                return False, f"Invalid timestamp type: {type(timestamp)}"
            
            # Validate description
            description = transaction_data.get('description', '').strip()
            if not description:
                return False, "Description cannot be empty"
            
            return True, ""
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def handle_negative_amount(self, amount: float, description: str) -> Tuple[float, str]:
        """
        Handle negative amounts based on business rules.
        
        Returns:
            Tuple[float, str]: (processed_amount, updated_description)
        """
        if amount < 0:
            # Convert to positive and mark as refund/reversal
            positive_amount = abs(amount)
            updated_description = f"[REFUND] {description}"
            return positive_amount, updated_description
        return amount, description
    
    def process_transaction(self, transaction_data: Dict[str, Any]) -> bool:
        """
        Process a single transaction with validation and duplicate checking.
        
        Returns:
            bool: True if transaction was processed successfully
        """
        try:
            # Validate transaction
            is_valid, error_msg = self.validate_transaction(transaction_data)
            if not is_valid:
                print(f"Invalid transaction rejected: {error_msg}")
                self.invalid_count += 1
                return False
            
            # Handle negative amounts
            amount, description = self.handle_negative_amount(
                transaction_data['amount'], 
                transaction_data['description']
            )
            
            # Create transaction object
            transaction = Transaction(
                id=transaction_data['id'],
                amount=amount,
                timestamp=transaction_data['timestamp'],
                description=description,
                merchant=transaction_data.get('merchant')
            )
            
            # Check for duplicates
            transaction_hash = self._generate_transaction_hash(transaction)
            if transaction_hash in self.processed_hashes:
                print(f"Duplicate transaction detected: {transaction.id}")
                self.duplicate_count += 1
                return False
            
            # Categorize transaction
            transaction.category = self._categorize_by_amount(transaction.amount)
            
            # Store transaction
            self.transactions.append(transaction)
            self.processed_hashes.add(transaction_hash)
            
            return True
            
        except Exception as e:
            print(f"Error processing transaction: {str(e)}")
            self.invalid_count += 1
            return False
    
    def process_batch(self, transactions_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process a batch of transactions.
        
        Returns:
            Dict containing processing summary
        """
        processed_count = 0
        
        for transaction_data in transactions_data:
            if self.process_transaction(transaction_data):
                processed_count += 1
        
        return {
            'total_input': len(transactions_data),
            'processed': processed_count,
            'duplicates': self.duplicate_count,
            'invalid': self.invalid_count,
            'success_rate': (processed_count / len(transactions_data)) * 100 if transactions_data else 0
        }
    
    def get_categorized_results(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get transactions grouped by category."""
        categorized = {}
        for category in TransactionCategory:
            categorized[category.value] = []
        
        for transaction in self.transactions:
            if transaction.category:
                categorized[transaction.category.value].append(transaction.to_dict())
        
        return categorized
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics of processed transactions."""
        if not self.transactions:
            return {"message": "No transactions processed"}
        
        amounts = [t.amount for t in self.transactions]
        categories = {}
        for transaction in self.transactions