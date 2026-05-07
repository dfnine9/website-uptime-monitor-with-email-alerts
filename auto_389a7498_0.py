```python
#!/usr/bin/env python3
"""
Bank Statement Transaction Categorizer

This module reads CSV bank statements from multiple formats, categorizes transactions
using keyword matching and regex patterns, and outputs categorized results.

Supports common bank statement formats and provides extensible categorization rules.
Handles various CSV structures and provides robust error handling.

Usage: python script.py
"""

import csv
import re
import os
import sys
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Transaction:
    """Represents a bank transaction with categorization."""
    date: str
    description: str
    amount: float
    category: str = "Uncategorized"
    original_row: Dict = None


class BankStatementProcessor:
    """Processes bank statements and categorizes transactions."""
    
    def __init__(self):
        self.category_rules = self._initialize_category_rules()
        
    def _initialize_category_rules(self) -> Dict[str, List[Tuple[str, str]]]:
        """Initialize categorization rules with keywords and regex patterns."""
        return {
            "Food & Dining": [
                (r"restaurant|cafe|coffee|pizza|burger|food|dining", "keyword"),
                (r"mcdonalds|starbucks|subway|dominos", "keyword"),
                (r".*restaurant.*|.*cafe.*|.*food.*", "regex")
            ],
            "Transportation": [
                (r"gas|fuel|station|uber|lyft|taxi|parking", "keyword"),
                (r"shell|bp|chevron|exxon|mobil", "keyword"),
                (r".*gas.*|.*fuel.*|.*parking.*", "regex")
            ],
            "Shopping": [
                (r"amazon|walmart|target|costco|store|shop", "keyword"),
                (r"purchase|buy|retail", "keyword"),
                (r".*store.*|.*shop.*|.*retail.*", "regex")
            ],
            "Utilities": [
                (r"electric|water|gas|internet|phone|cable|utility", "keyword"),
                (r"power|energy|telecom", "keyword"),
                (r".*electric.*|.*utility.*|.*telecom.*", "regex")
            ],
            "Healthcare": [
                (r"medical|doctor|hospital|pharmacy|health|dental", "keyword"),
                (r"cvs|walgreens|clinic", "keyword"),
                (r".*medical.*|.*health.*|.*pharmacy.*", "regex")
            ],
            "Entertainment": [
                (r"movie|theater|netflix|spotify|gaming|entertainment", "keyword"),
                (r"cinema|music|streaming", "keyword"),
                (r".*entertainment.*|.*streaming.*", "regex")
            ],
            "Banking": [
                (r"transfer|deposit|withdrawal|fee|interest|bank", "keyword"),
                (r"atm|overdraft|maintenance", "keyword"),
                (r".*transfer.*|.*fee.*|.*interest.*", "regex")
            ]
        }
    
    def detect_csv_format(self, filepath: str) -> Optional[Dict[str, str]]:
        """Detect the CSV format and return column mappings."""
        try:
            with open(filepath, 'r', encoding='utf-8', newline='') as file:
                # Read first few lines to detect format
                sample = file.read(1024)
                file.seek(0)
                
                # Try different delimiters
                for delimiter in [',', ';', '\t']:
                    file.seek(0)
                    reader = csv.reader(file, delimiter=delimiter)
                    headers = next(reader, [])
                    
                    if len(headers) >= 3:  # Minimum columns expected
                        mapping = self._map_columns(headers)
                        if mapping:
                            return {**mapping, 'delimiter': delimiter}
                            
        except Exception as e:
            print(f"Error detecting CSV format: {e}")
            
        return None
    
    def _map_columns(self, headers: List[str]) -> Optional[Dict[str, str]]:
        """Map CSV headers to standard transaction fields."""
        headers_lower = [h.lower().strip() for h in headers]
        
        # Common column name patterns
        date_patterns = ['date', 'transaction date', 'posted date', 'trans date']
        desc_patterns = ['description', 'memo', 'payee', 'transaction', 'details']
        amount_patterns = ['amount', 'debit', 'credit', 'transaction amount']
        
        mapping = {}
        
        # Find date column
        for pattern in date_patterns:
            for i, header in enumerate(headers_lower):
                if pattern in header:
                    mapping['date'] = headers[i]
                    break
            if 'date' in mapping:
                break
                
        # Find description column
        for pattern in desc_patterns:
            for i, header in enumerate(headers_lower):
                if pattern in header:
                    mapping['description'] = headers[i]
                    break
            if 'description' in mapping:
                break
                
        # Find amount column
        for pattern in amount_patterns:
            for i, header in enumerate(headers_lower):
                if pattern in header:
                    mapping['amount'] = headers[i]
                    break
            if 'amount' in mapping:
                break
                
        # Check if we found the essential columns
        if len(mapping) >= 3:
            return mapping
            
        return None
    
    def parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float, handling various formats."""
        try:
            # Remove common currency symbols and whitespace
            cleaned = re.sub(r'[$,\s]', '', str(amount_str))
            
            # Handle parentheses for negative amounts
            if '(' in cleaned and ')' in cleaned:
                cleaned = cleaned.replace('(', '-').replace(')', '')
                
            # Handle negative signs
            if cleaned.startswith('-') or cleaned.endswith('-'):
                cleaned = cleaned.replace('-', '')
                return -float(cleaned)
                
            return float(cleaned)
            
        except (ValueError, TypeError):
            return 0.0
    
    def categorize_transaction(self, description: str, amount: float) -> str:
        """Categorize a transaction based on description and amount."""
        description_lower = description.lower()
        
        for category, rules in self.category_rules.items():
            for pattern, rule_type in rules:
                if rule_type == "keyword":
                    # Simple keyword matching
                    keywords = pattern.split('|')
                    if any(keyword in description_lower for keyword in keywords):
                        return category
                elif rule_type == "regex":
                    # Regex pattern matching
                    if re.search(pattern, description_lower, re.IGNORECASE):
                        return category
                        
        # Special case for large amounts (might be transfers/investments)
        if abs(amount) > 1000:
            return "Large Transaction"
            
        return "Uncategorized"
    
    def read_csv_statements(self, filepath: str) -> List[Transaction]:
        """Read and parse CSV bank statement."""
        transactions = []
        
        try:
            # Detect format
            format_info = self.detect_csv_format(filepath)
            if not format_info:
                raise ValueError("Unable to detect CSV format")
                
            print(f"Detected format: {format_info}")
            
            with open(filepath, 'r', encoding='utf-8', newline='') as file:
                reader = csv.DictReader(file, delimiter=format_info['delimiter'])
                
                for row_num, row in enumerate(reader, 1):
                    try:
                        # Extract transaction data
                        date = row.get(format_info['date'], '').strip()
                        description = row.get(format_info['description'], '').strip()
                        amount = self.parse_amount(row.get(format_info['amount'], '0'))
                        
                        if date and description:  # Only process valid transactions
                            category = self.categorize_transaction(description, amount)
                            
                            transaction = Transaction(
                                date=date,