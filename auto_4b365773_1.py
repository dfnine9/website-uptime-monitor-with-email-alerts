```python
"""
Transaction Data Validation and Preprocessing Module

This module provides comprehensive data validation and preprocessing capabilities
for transaction data. It standardizes formats, handles edge cases like duplicate
transactions and missing fields, and ensures data quality for downstream processing.

Key Features:
- Transaction deduplication using multiple strategies
- Missing field detection and handling
- Data type validation and conversion
- Amount normalization and validation
- Date/timestamp standardization
- Configurable validation rules
- Comprehensive error reporting

Usage:
    python script.py

The script demonstrates validation of sample transaction data and outputs
processed results with detailed reporting of any issues found.
"""

import json
import re
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Any, Optional, Tuple, Set
import hashlib
import uuid


class TransactionValidationError(Exception):
    """Custom exception for transaction validation errors."""
    pass


class TransactionValidator:
    """
    Validates and preprocesses transaction data with configurable rules.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize validator with configuration.
        
        Args:
            config: Optional configuration dictionary for validation rules
        """
        self.config = config or self._get_default_config()
        self.validation_errors = []
        self.processed_count = 0
        self.duplicate_count = 0
        self.error_count = 0
        
    def _get_default_config(self) -> Dict:
        """Get default validation configuration."""
        return {
            'required_fields': ['transaction_id', 'amount', 'date', 'type'],
            'optional_fields': ['description', 'category', 'account_id', 'reference'],
            'amount_precision': 2,
            'max_amount': 1000000.00,
            'min_amount': 0.01,
            'valid_types': ['debit', 'credit', 'transfer', 'fee'],
            'date_formats': ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S'],
            'duplicate_strategy': 'hash',  # 'hash', 'field_match', 'strict'
            'handle_missing_fields': True,
            'normalize_amounts': True
        }
    
    def validate_and_preprocess(self, transactions: List[Dict]) -> Tuple[List[Dict], Dict]:
        """
        Validate and preprocess a list of transactions.
        
        Args:
            transactions: List of transaction dictionaries
            
        Returns:
            Tuple of (processed_transactions, summary_report)
        """
        try:
            print("Starting transaction validation and preprocessing...")
            
            # Reset counters
            self.validation_errors = []
            self.processed_count = 0
            self.duplicate_count = 0
            self.error_count = 0
            
            # Remove duplicates first
            unique_transactions = self._remove_duplicates(transactions)
            print(f"Removed {len(transactions) - len(unique_transactions)} duplicate transactions")
            
            # Process each transaction
            processed_transactions = []
            for i, transaction in enumerate(unique_transactions):
                try:
                    processed_tx = self._process_single_transaction(transaction, i)
                    if processed_tx:
                        processed_transactions.append(processed_tx)
                        self.processed_count += 1
                except TransactionValidationError as e:
                    self.error_count += 1
                    self.validation_errors.append({
                        'transaction_index': i,
                        'error': str(e),
                        'transaction': transaction
                    })
                    print(f"Validation error for transaction {i}: {e}")
            
            # Generate summary report
            summary = self._generate_summary_report(
                len(transactions), 
                len(processed_transactions)
            )
            
            return processed_transactions, summary
            
        except Exception as e:
            print(f"Critical error during processing: {e}")
            raise
    
    def _remove_duplicates(self, transactions: List[Dict]) -> List[Dict]:
        """
        Remove duplicate transactions based on configured strategy.
        
        Args:
            transactions: List of transaction dictionaries
            
        Returns:
            List of unique transactions
        """
        strategy = self.config.get('duplicate_strategy', 'hash')
        seen = set()
        unique_transactions = []
        
        for transaction in transactions:
            try:
                if strategy == 'hash':
                    # Create hash of key fields
                    key_fields = ['amount', 'date', 'type']
                    key_data = {k: transaction.get(k) for k in key_fields if k in transaction}
                    tx_hash = hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()
                    
                elif strategy == 'field_match':
                    # Use specific fields for matching
                    match_fields = ['transaction_id', 'amount', 'date']
                    tx_hash = tuple(transaction.get(f) for f in match_fields)
                    
                elif strategy == 'strict':
                    # Exact match on all fields
                    tx_hash = hashlib.md5(json.dumps(transaction, sort_keys=True).encode()).hexdigest()
                
                if tx_hash not in seen:
                    seen.add(tx_hash)
                    unique_transactions.append(transaction)
                else:
                    self.duplicate_count += 1
                    
            except Exception as e:
                print(f"Error processing transaction for duplicates: {e}")
                # Include transaction anyway if duplicate detection fails
                unique_transactions.append(transaction)
        
        return unique_transactions
    
    def _process_single_transaction(self, transaction: Dict, index: int) -> Dict:
        """
        Process and validate a single transaction.
        
        Args:
            transaction: Transaction dictionary
            index: Transaction index for error reporting
            
        Returns:
            Processed transaction dictionary
            
        Raises:
            TransactionValidationError: If validation fails
        """
        processed_tx = transaction.copy()
        
        # Validate required fields
        missing_fields = self._check_required_fields(processed_tx)
        if missing_fields and not self.config.get('handle_missing_fields'):
            raise TransactionValidationError(f"Missing required fields: {missing_fields}")
        
        # Handle missing fields
        if missing_fields and self.config.get('handle_missing_fields'):
            processed_tx = self._handle_missing_fields(processed_tx, missing_fields)
        
        # Validate and normalize amount
        processed_tx = self._validate_and_normalize_amount(processed_tx)
        
        # Validate and normalize date
        processed_tx = self._validate_and_normalize_date(processed_tx)
        
        # Validate transaction type
        processed_tx = self._validate_transaction_type(processed_tx)
        
        # Add processing metadata
        processed_tx['_processed_at'] = datetime.now(timezone.utc).isoformat()
        processed_tx['_validation_status'] = 'valid'
        
        return processed_tx
    
    def _check_required_fields(self, transaction: Dict) -> List[str]:
        """Check for missing required fields."""
        required = self.config.get('required_fields', [])
        missing = [field for field in required if field not in transaction or transaction[field] is None]
        return missing
    
    def _handle_missing_fields(self, transaction: Dict, missing_fields: List[str]) -> Dict:
        """
        Handle missing required fields with default values.
        
        Args:
            transaction: Transaction dictionary
            missing_fields: List of missing field names
            
        Returns:
            Transaction with default values for missing fields
        """
        defaults = {
            'transaction_id': lambda: str(uuid.uuid4()),
            'amount': 0.00,
            'date': datetime.now(timezone.utc).isoformat(),
            'type': 'unknown',
            'description': 'No description provided',
            'category': 'uncategorized',
            'account_id': 'unknown',
            'reference': ''
        }
        
        for field in missing