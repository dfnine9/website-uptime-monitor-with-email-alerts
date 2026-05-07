```python
#!/usr/bin/env python3
"""
Transaction Categorization System

This module provides a self-contained system for reading CSV transaction files,
categorizing transactions based on configurable keyword rules stored in JSON files,
and validating transaction data fields.

Features:
- Reads transaction data from CSV files
- Applies configurable categorization rules from JSON config
- Validates transaction fields (amount, date format, required fields)
- Handles errors gracefully with detailed error reporting
- Self-contained with minimal dependencies

Usage:
    python script.py

The script expects:
- transactions.csv in the current directory
- config.json for categorization rules
- Creates sample files if they don't exist
"""

import csv
import json
import re
import os
from datetime import datetime
from typing import Dict, List, Any, Optional


class TransactionCategorizer:
    """Handles transaction reading, validation, and categorization."""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize with configuration file path."""
        self.config_path = config_path
        self.categories = {}
        self.load_config()
    
    def load_config(self) -> None:
        """Load categorization rules from JSON config file."""
        try:
            if not os.path.exists(self.config_path):
                self.create_sample_config()
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.categories = config.get('categories', {})
                print(f"Loaded {len(self.categories)} category rules from {self.config_path}")
        
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in config file: {e}")
            self.categories = {}
        except Exception as e:
            print(f"Error loading config: {e}")
            self.categories = {}
    
    def create_sample_config(self) -> None:
        """Create a sample configuration file."""
        sample_config = {
            "categories": {
                "Food & Dining": {
                    "keywords": ["restaurant", "cafe", "pizza", "burger", "starbucks", "mcdonald", "food"],
                    "case_sensitive": False,
                    "priority": 1
                },
                "Transportation": {
                    "keywords": ["uber", "lyft", "gas", "fuel", "parking", "metro", "bus"],
                    "case_sensitive": False,
                    "priority": 2
                },
                "Shopping": {
                    "keywords": ["amazon", "target", "walmart", "store", "shop"],
                    "case_sensitive": False,
                    "priority": 3
                },
                "Bills & Utilities": {
                    "keywords": ["electric", "water", "internet", "phone", "insurance", "rent"],
                    "case_sensitive": False,
                    "priority": 4
                },
                "Entertainment": {
                    "keywords": ["netflix", "spotify", "movie", "theater", "game"],
                    "case_sensitive": False,
                    "priority": 5
                }
            },
            "validation_rules": {
                "required_fields": ["date", "description", "amount"],
                "date_formats": ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"],
                "amount_pattern": "^-?\\d+(\\.\\d{1,2})?$"
            }
        }
        
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(sample_config, f, indent=2)
            print(f"Created sample config file: {self.config_path}")
        except Exception as e:
            print(f"Error creating sample config: {e}")
    
    def validate_transaction(self, transaction: Dict[str, str]) -> tuple[bool, List[str]]:
        """Validate transaction data fields."""
        errors = []
        
        # Check required fields
        required_fields = ["date", "description", "amount"]
        for field in required_fields:
            if field not in transaction or not transaction[field].strip():
                errors.append(f"Missing required field: {field}")
        
        # Validate date format
        if "date" in transaction and transaction["date"].strip():
            date_valid = False
            date_formats = ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"]
            
            for fmt in date_formats:
                try:
                    datetime.strptime(transaction["date"], fmt)
                    date_valid = True
                    break
                except ValueError:
                    continue
            
            if not date_valid:
                errors.append(f"Invalid date format: {transaction['date']}")
        
        # Validate amount format
        if "amount" in transaction and transaction["amount"].strip():
            amount_pattern = r"^-?\d+(\.\d{1,2})?$"
            if not re.match(amount_pattern, transaction["amount"].strip()):
                errors.append(f"Invalid amount format: {transaction['amount']}")
        
        return len(errors) == 0, errors
    
    def categorize_transaction(self, description: str) -> str:
        """Categorize transaction based on description and keyword rules."""
        if not description:
            return "Uncategorized"
        
        # Sort categories by priority
        sorted_categories = sorted(
            self.categories.items(),
            key=lambda x: x[1].get('priority', 999)
        )
        
        for category_name, rules in sorted_categories:
            keywords = rules.get('keywords', [])
            case_sensitive = rules.get('case_sensitive', False)
            
            search_text = description if case_sensitive else description.lower()
            
            for keyword in keywords:
                search_keyword = keyword if case_sensitive else keyword.lower()
                if search_keyword in search_text:
                    return category_name
        
        return "Uncategorized"
    
    def read_csv_transactions(self, csv_path: str) -> List[Dict[str, Any]]:
        """Read and process transactions from CSV file."""
        transactions = []
        
        try:
            if not os.path.exists(csv_path):
                self.create_sample_csv(csv_path)
            
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        # Validate transaction
                        is_valid, errors = self.validate_transaction(row)
                        
                        if is_valid:
                            # Categorize transaction
                            category = self.categorize_transaction(row.get('description', ''))
                            
                            transaction = {
                                'row_number': row_num,
                                'date': row.get('date', '').strip(),
                                'description': row.get('description', '').strip(),
                                'amount': float(row.get('amount', '0')),
                                'category': category,
                                'valid': True,
                                'errors': []
                            }
                        else:
                            transaction = {
                                'row_number': row_num,
                                'date': row.get('date', '').strip(),
                                'description': row.get('description', '').strip(),
                                'amount': row.get('amount', '').strip(),
                                'category': 'Invalid',
                                'valid': False,
                                'errors': errors
                            }
                        
                        transactions.append(transaction)
                    
                    except Exception as e:
                        print(f"Error processing row {row_num}: {e}")
                        transactions.append({
                            'row_number': row_num,
                            'date': row.get('date', ''),
                            'description': row.get('description', ''),
                            'amount': row.get('amount', ''),
                            'category': 'Error',
                            'valid': False,
                            'errors': [str(e)]
                        })
        
        except FileNotFoundError:
            print(f"Error: CSV file not found: {