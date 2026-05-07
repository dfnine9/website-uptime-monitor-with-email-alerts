```python
#!/usr/bin/env python3
"""
Personal Finance Analytics Tool

A comprehensive financial analysis application that processes CSV transaction data,
categorizes transactions using AI, analyzes spending patterns, calculates budgets,
and generates text-based charts. Designed to help users understand their financial
habits and make informed budgeting decisions.

Features:
- CSV transaction import with flexible column mapping
- AI-powered transaction categorization using Anthropic's Claude
- Spending pattern analysis with trend detection
- Budget calculation based on historical data
- Text-based chart generation for visualization
- Command-line interface for easy operation

Usage:
    python script.py [--file transactions.csv] [--api-key YOUR_KEY]

Dependencies:
    - httpx: For HTTP requests to Anthropic API
    - anthropic: For AI categorization (optional)
    - Standard library modules: csv, json, argparse, datetime, etc.
"""

import csv
import json
import argparse
import sys
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Optional
import re
import statistics

try:
    import httpx
except ImportError:
    httpx = None

try:
    import anthropic
except ImportError:
    anthropic = None


class TransactionAnalyzer:
    """Main class for financial transaction analysis."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.transactions = []
        self.categories = {}
        self.api_key = api_key
        self.client = None
        
        if api_key and anthropic:
            try:
                self.client = anthropic.Anthropic(api_key=api_key)
            except Exception as e:
                print(f"Warning: Could not initialize Anthropic client: {e}")
    
    def import_csv(self, filepath: str) -> bool:
        """Import transactions from CSV file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                # Try to detect CSV dialect
                sample = file.read(1024)
                file.seek(0)
                
                sniffer = csv.Sniffer()
                delimiter = ','
                try:
                    dialect = sniffer.sniff(sample, delimiters=',;\t')
                    delimiter = dialect.delimiter
                except:
                    pass
                
                reader = csv.DictReader(file, delimiter=delimiter)
                headers = reader.fieldnames
                
                if not headers:
                    raise ValueError("No headers found in CSV file")
                
                # Try to map common column names
                column_mapping = self._detect_columns(headers)
                
                for row in reader:
                    try:
                        transaction = self._parse_transaction(row, column_mapping)
                        if transaction:
                            self.transactions.append(transaction)
                    except Exception as e:
                        print(f"Warning: Skipping invalid row: {e}")
                        continue
                
                print(f"Successfully imported {len(self.transactions)} transactions")
                return True
                
        except Exception as e:
            print(f"Error importing CSV: {e}")
            return False
    
    def _detect_columns(self, headers: List[str]) -> Dict[str, str]:
        """Detect column mappings from CSV headers."""
        mapping = {}
        headers_lower = [h.lower() for h in headers]
        
        # Date column detection
        date_patterns = ['date', 'transaction_date', 'posted_date', 'timestamp']
        for pattern in date_patterns:
            for i, header in enumerate(headers_lower):
                if pattern in header:
                    mapping['date'] = headers[i]
                    break
            if 'date' in mapping:
                break
        
        # Amount column detection
        amount_patterns = ['amount', 'value', 'total', 'sum', 'debit', 'credit']
        for pattern in amount_patterns:
            for i, header in enumerate(headers_lower):
                if pattern in header:
                    mapping['amount'] = headers[i]
                    break
            if 'amount' in mapping:
                break
        
        # Description column detection
        desc_patterns = ['description', 'memo', 'merchant', 'payee', 'details']
        for pattern in desc_patterns:
            for i, header in enumerate(headers_lower):
                if pattern in header:
                    mapping['description'] = headers[i]
                    break
            if 'description' in mapping:
                break
        
        # Category column detection (optional)
        cat_patterns = ['category', 'type', 'class']
        for pattern in cat_patterns:
            for i, header in enumerate(headers_lower):
                if pattern in header:
                    mapping['category'] = headers[i]
                    break
        
        return mapping
    
    def _parse_transaction(self, row: Dict, mapping: Dict[str, str]) -> Optional[Dict]:
        """Parse a single transaction from CSV row."""
        if 'date' not in mapping or 'amount' not in mapping or 'description' not in mapping:
            raise ValueError("Required columns not found")
        
        # Parse date
        date_str = row[mapping['date']].strip()
        date_obj = self._parse_date(date_str)
        if not date_obj:
            raise ValueError(f"Could not parse date: {date_str}")
        
        # Parse amount
        amount_str = row[mapping['amount']].strip()
        amount = self._parse_amount(amount_str)
        if amount is None:
            raise ValueError(f"Could not parse amount: {amount_str}")
        
        # Get description
        description = row[mapping['description']].strip()
        if not description:
            raise ValueError("Empty description")
        
        # Get category if available
        category = None
        if 'category' in mapping and mapping['category'] in row:
            category = row[mapping['category']].strip()
        
        return {
            'date': date_obj,
            'amount': amount,
            'description': description,
            'category': category
        }
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string into datetime object."""
        date_formats = [
            '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d',
            '%m-%d-%Y', '%d-%m-%Y', '%Y.%m.%d', '%m.%d.%Y',
            '%d.%m.%Y', '%Y%m%d'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None
    
    def _parse_amount(self, amount_str: str) -> Optional[float]:
        """Parse amount string into float."""
        # Remove currency symbols and whitespace
        cleaned = re.sub(r'[^\d\-\+\.,]', '', amount_str)
        
        if not cleaned:
            return None
        
        # Handle parentheses as negative
        if amount_str.strip().startswith('(') and amount_str.strip().endswith(')'):
            cleaned = '-' + cleaned
        
        # Replace comma with dot for decimal
        if ',' in cleaned and '.' in cleaned:
            # Assume comma is thousands separator
            cleaned = cleaned.replace(',', '')
        elif cleaned.count(',') == 1 and cleaned.index(',') > len(cleaned) - 4:
            # Assume comma is decimal separator
            cleaned = cleaned.replace(',', '.')
        
        try:
            return float(cleaned)
        except ValueError:
            return None
    
    def categorize_transactions(self) -> None:
        """Categorize transactions using AI or rule-based approach."""
        print("Categorizing transactions...")
        
        uncategorized = [t for t in self.transactions if not t['category']]
        
        if self.client and uncategorized:
            self._categorize_with_ai(uncategorized)
        else:
            self._categorize_with_rules()
        
        print(f"Categorization complete. {len(set(t['category'] for t in self.transactions))} categories identified.")
    
    def