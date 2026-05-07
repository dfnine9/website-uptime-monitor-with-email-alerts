```python
#!/usr/bin/env python3
"""
Bank Statement Transaction Classifier

This module parses CSV bank statements and automatically classifies transactions
into categories based on configurable keyword mapping rules. It extracts
transaction descriptions and amounts, applies classification logic, and outputs
the categorized results.

Features:
- CSV parsing with flexible column detection
- Configurable keyword-to-category mapping
- Case-insensitive pattern matching
- Error handling for malformed data
- Summary statistics and reporting

Usage:
    python script.py
"""

import csv
import re
import sys
from typing import Dict, List, Tuple, Optional
from decimal import Decimal, InvalidOperation
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Transaction:
    """Represents a single bank transaction."""
    date: str
    description: str
    amount: Decimal
    category: str = "Uncategorized"
    
    def __str__(self) -> str:
        return f"{self.date:<12} | {self.description:<40} | ${self.amount:>8.2f} | {self.category}"


class TransactionClassifier:
    """Classifies bank transactions based on configurable keyword rules."""
    
    def __init__(self):
        self.categories = {
            "Food & Dining": [
                "restaurant", "cafe", "coffee", "pizza", "burger", "mcdonalds",
                "starbucks", "subway", "food", "dining", "delivery", "doordash",
                "grubhub", "uber eats", "grocery", "supermarket", "walmart", "target"
            ],
            "Transportation": [
                "gas", "fuel", "shell", "exxon", "bp", "chevron", "parking",
                "uber", "lyft", "taxi", "metro", "bus", "train", "airline",
                "flight", "car wash", "auto", "repair"
            ],
            "Shopping": [
                "amazon", "ebay", "walmart", "target", "costco", "mall",
                "store", "retail", "clothing", "electronics", "best buy"
            ],
            "Utilities": [
                "electric", "water", "gas bill", "internet", "phone", "cable",
                "utility", "power", "energy", "comcast", "verizon", "att"
            ],
            "Healthcare": [
                "medical", "doctor", "hospital", "pharmacy", "cvs", "walgreens",
                "dental", "vision", "insurance", "clinic", "health"
            ],
            "Entertainment": [
                "movie", "netflix", "spotify", "hulu", "disney", "theater",
                "concert", "game", "entertainment", "streaming", "youtube"
            ],
            "Banking": [
                "atm", "fee", "transfer", "deposit", "withdrawal", "interest",
                "bank", "credit", "payment", "overdraft"
            ]
        }
    
    def classify(self, description: str) -> str:
        """Classify a transaction description into a category."""
        description_lower = description.lower()
        
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return "Uncategorized"
    
    def add_category(self, category: str, keywords: List[str]) -> None:
        """Add a new category with keywords."""
        self.categories[category] = keywords
    
    def add_keywords(self, category: str, keywords: List[str]) -> None:
        """Add keywords to an existing category."""
        if category in self.categories:
            self.categories[category].extend(keywords)
        else:
            self.categories[category] = keywords


class BankStatementParser:
    """Parses CSV bank statements and extracts transaction data."""
    
    def __init__(self, classifier: TransactionClassifier):
        self.classifier = classifier
        self.transactions: List[Transaction] = []
    
    def detect_columns(self, headers: List[str]) -> Dict[str, int]:
        """Detect column indices based on header names."""
        column_map = {}
        
        # Common header variations
        date_patterns = ['date', 'transaction date', 'posted date', 'trans date']
        desc_patterns = ['description', 'desc', 'memo', 'transaction', 'details']
        amount_patterns = ['amount', 'debit', 'credit', 'transaction amount']
        
        headers_lower = [h.lower().strip() for h in headers]
        
        for i, header in enumerate(headers_lower):
            if any(pattern in header for pattern in date_patterns):
                column_map['date'] = i
            elif any(pattern in header for pattern in desc_patterns):
                column_map['description'] = i
            elif any(pattern in header for pattern in amount_patterns):
                column_map['amount'] = i
        
        return column_map
    
    def parse_amount(self, amount_str: str) -> Optional[Decimal]:
        """Parse amount string to Decimal, handling various formats."""
        try:
            # Remove common characters
            cleaned = re.sub(r'[,$\s]', '', amount_str.strip())
            
            # Handle parentheses as negative
            if cleaned.startswith('(') and cleaned.endswith(')'):
                cleaned = '-' + cleaned[1:-1]
            
            return Decimal(cleaned)
        except (InvalidOperation, ValueError):
            return None
    
    def parse_csv(self, file_path: str) -> bool:
        """Parse CSV file and extract transactions."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # Detect delimiter
                sample = file.read(1024)
                file.seek(0)
                
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.reader(file, delimiter=delimiter)
                headers = next(reader)
                
                column_map = self.detect_columns(headers)
                
                if not all(key in column_map for key in ['date', 'description', 'amount']):
                    print("Error: Could not detect required columns (date, description, amount)")
                    return False
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        if len(row) <= max(column_map.values()):
                            continue
                        
                        date = row[column_map['date']].strip()
                        description = row[column_map['description']].strip()
                        amount = self.parse_amount(row[column_map['amount']])
                        
                        if amount is None:
                            print(f"Warning: Invalid amount in row {row_num}: {row[column_map['amount']]}")
                            continue
                        
                        if not description:
                            description = "No description"
                        
                        category = self.classifier.classify(description)
                        
                        transaction = Transaction(
                            date=date,
                            description=description,
                            amount=amount,
                            category=category
                        )
                        
                        self.transactions.append(transaction)
                        
                    except (IndexError, ValueError) as e:
                        print(f"Warning: Error parsing row {row_num}: {e}")
                        continue
                
                return True
                
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found")
            return False
        except Exception as e:
            print(f"Error reading file: {e}")
            return False
    
    def generate_sample_csv(self, file_path: str) -> None:
        """Generate a sample CSV file for testing."""
        sample_data = [
            ["Date", "Description", "Amount"],
            ["2024-01-15", "STARBUCKS COFFEE #123", "-4.85"],
            ["2024-01-16", "AMAZON.COM PURCHASE", "-67.23"],
            ["2024-01-17", "SHELL GAS STATION", "-45.67"],
            ["2024-01-18", "SALARY DEPOSIT", "2500.00"],
            ["2024-01-19", "WALMART GROCERY", "-89.34"],
            ["2024-