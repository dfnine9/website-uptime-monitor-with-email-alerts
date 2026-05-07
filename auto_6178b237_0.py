```python
#!/usr/bin/env python3
"""
Bank Transaction Categorizer

A self-contained Python script that parses bank CSV exports, validates transaction data,
and categorizes transactions based on configurable keyword mapping rules.

Features:
- Parses CSV files with flexible column mapping
- Validates date formats, amounts, and required fields
- Configurable keyword-to-category mapping system
- Case-insensitive keyword matching in transaction descriptions
- Comprehensive error handling and logging
- Outputs categorized transactions with statistics

Usage: python script.py
"""

import csv
import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict
import sys


@dataclass
class Transaction:
    """Represents a bank transaction with validation."""
    date: str
    description: str
    amount: float
    category: str = "Uncategorized"
    
    def __post_init__(self):
        """Validate transaction data after initialization."""
        if not self.date or not self.description:
            raise ValueError("Date and description are required")
        if not isinstance(self.amount, (int, float)):
            raise ValueError("Amount must be numeric")


class BankCSVParser:
    """Parses and categorizes bank transaction CSV files."""
    
    def __init__(self):
        self.transactions: List[Transaction] = []
        self.category_rules = self._load_default_categories()
        self.column_mapping = {
            'date': ['date', 'transaction_date', 'posting_date'],
            'description': ['description', 'memo', 'payee', 'transaction_description'],
            'amount': ['amount', 'debit', 'credit', 'transaction_amount']
        }
        
    def _load_default_categories(self) -> Dict[str, List[str]]:
        """Load default keyword-to-category mapping rules."""
        return {
            "Food & Dining": [
                "restaurant", "cafe", "coffee", "pizza", "burger", "food",
                "dining", "lunch", "dinner", "breakfast", "takeout", "delivery"
            ],
            "Transportation": [
                "gas", "fuel", "uber", "lyft", "taxi", "parking", "metro",
                "bus", "train", "airline", "flight", "car wash", "auto"
            ],
            "Shopping": [
                "amazon", "walmart", "target", "costco", "mall", "store",
                "shopping", "purchase", "retail", "outlet"
            ],
            "Entertainment": [
                "movie", "cinema", "theater", "concert", "music", "streaming",
                "netflix", "spotify", "game", "entertainment"
            ],
            "Utilities": [
                "electric", "water", "gas bill", "internet", "phone", "cable",
                "utility", "power", "energy", "telecom"
            ],
            "Healthcare": [
                "doctor", "hospital", "pharmacy", "medical", "dental",
                "health", "clinic", "prescription", "medicine"
            ],
            "Banking": [
                "atm", "fee", "interest", "transfer", "deposit", "withdrawal",
                "bank", "credit card", "loan payment"
            ]
        }
    
    def detect_columns(self, headers: List[str]) -> Dict[str, str]:
        """Detect column mapping from CSV headers."""
        mapping = {}
        headers_lower = [h.lower().strip() for h in headers]
        
        for field, possible_names in self.column_mapping.items():
            for possible_name in possible_names:
                if possible_name in headers_lower:
                    mapping[field] = headers[headers_lower.index(possible_name)]
                    break
        
        return mapping
    
    def validate_date(self, date_str: str) -> str:
        """Validate and normalize date format."""
        if not date_str:
            raise ValueError("Date cannot be empty")
            
        # Common date formats
        date_formats = [
            "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%m-%d-%Y",
            "%Y/%m/%d", "%d-%m-%Y", "%m/%d/%y", "%d/%m/%y"
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str.strip(), fmt)
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue
                
        raise ValueError(f"Invalid date format: {date_str}")
    
    def validate_amount(self, amount_str: str) -> float:
        """Validate and parse amount string to float."""
        if not amount_str:
            raise ValueError("Amount cannot be empty")
            
        # Clean amount string
        cleaned = re.sub(r'[,$\s]', '', str(amount_str).strip())
        
        # Handle parentheses for negative amounts
        if cleaned.startswith('(') and cleaned.endswith(')'):
            cleaned = '-' + cleaned[1:-1]
            
        try:
            return float(cleaned)
        except ValueError:
            raise ValueError(f"Invalid amount format: {amount_str}")
    
    def categorize_transaction(self, description: str) -> str:
        """Categorize transaction based on description keywords."""
        description_lower = description.lower()
        
        for category, keywords in self.category_rules.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category
                    
        return "Uncategorized"
    
    def parse_csv_file(self, filepath: str) -> None:
        """Parse CSV file and extract transactions."""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                # Detect delimiter
                sample = file.read(1024)
                file.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(file, delimiter=delimiter)
                headers = reader.fieldnames
                
                if not headers:
                    raise ValueError("CSV file has no headers")
                
                # Detect column mapping
                column_map = self.detect_columns(headers)
                
                required_fields = ['date', 'description', 'amount']
                missing_fields = [f for f in required_fields if f not in column_map]
                if missing_fields:
                    raise ValueError(f"Missing required columns: {missing_fields}")
                
                print(f"Detected columns: {column_map}")
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        # Extract and validate data
                        date = self.validate_date(row[column_map['date']])
                        description = row[column_map['description']].strip()
                        amount = self.validate_amount(row[column_map['amount']])
                        
                        # Categorize transaction
                        category = self.categorize_transaction(description)
                        
                        # Create transaction
                        transaction = Transaction(
                            date=date,
                            description=description,
                            amount=amount,
                            category=category
                        )
                        
                        self.transactions.append(transaction)
                        
                    except (ValueError, KeyError) as e:
                        print(f"Warning: Skipping row {row_num} - {e}")
                        continue
                        
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file not found: {filepath}")
        except Exception as e:
            raise Exception(f"Error parsing CSV file: {e}")
    
    def generate_sample_csv(self, filepath: str) -> None:
        """Generate a sample CSV file for testing."""
        sample_data = [
            ["2024-01-15", "STARBUCKS COFFEE", "-5.50"],
            ["2024-01-16", "AMAZON.COM PURCHASE", "-45.99"],
            ["2024-01-17", "SALARY DEPOSIT", "3000.00"],
            ["2024-01-18", "SHELL GAS STATION", "-35.20"],
            ["2024-01-19", "NETFLIX SUBSCRIPTION", "-15.