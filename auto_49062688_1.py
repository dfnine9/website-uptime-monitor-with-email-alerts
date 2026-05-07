```python
"""
Bank Transaction Data Validation and Preprocessing Module

This module provides comprehensive data validation and preprocessing capabilities
for different bank CSV formats. It handles:

1. Multiple CSV format detection and parsing
2. Transaction description cleaning and normalization
3. Date format standardization across different banks
4. Amount format normalization (handling different decimal separators, currency symbols)
5. Data validation with comprehensive error reporting
6. Duplicate transaction detection
7. Missing data handling

Supports common formats from major banks including:
- Chase, Bank of America, Wells Fargo
- European banks (comma decimal separators)
- Custom format detection

Usage: python script.py
"""

import csv
import re
import json
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Any, Optional, Tuple
import io

class BankTransactionProcessor:
    
    def __init__(self):
        self.supported_date_formats = [
            "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%m-%d-%Y", 
            "%d-%m-%Y", "%Y/%m/%d", "%m/%d/%y", "%d/%m/%y",
            "%B %d, %Y", "%b %d, %Y", "%d %b %Y", "%d %B %Y"
        ]
        
        self.bank_formats = {
            'chase': ['Date', 'Description', 'Amount', 'Balance'],
            'bofa': ['Posted Date', 'Payee', 'Amount'],
            'wells_fargo': ['Date', 'Amount', 'Description'],
            'generic': ['date', 'description', 'amount']
        }
        
        self.processed_transactions = []
        self.validation_errors = []
        
    def detect_csv_format(self, csv_content: str) -> Dict[str, Any]:
        """Detect CSV format and return parsing configuration."""
        try:
            # Try different delimiters
            for delimiter in [',', ';', '\t']:
                try:
                    reader = csv.reader(io.StringIO(csv_content), delimiter=delimiter)
                    headers = next(reader)
                    
                    if len(headers) > 1:
                        # Detect bank format
                        bank_type = self._identify_bank_type(headers)
                        return {
                            'delimiter': delimiter,
                            'headers': headers,
                            'bank_type': bank_type,
                            'encoding': 'utf-8'
                        }
                except:
                    continue
                    
            return {'delimiter': ',', 'headers': [], 'bank_type': 'unknown', 'encoding': 'utf-8'}
            
        except Exception as e:
            self.validation_errors.append(f"CSV format detection error: {str(e)}")
            return {'delimiter': ',', 'headers': [], 'bank_type': 'unknown', 'encoding': 'utf-8'}
    
    def _identify_bank_type(self, headers: List[str]) -> str:
        """Identify bank type based on header patterns."""
        headers_lower = [h.lower().strip() for h in headers]
        
        # Check for specific bank patterns
        if any('posted' in h and 'date' in h for h in headers_lower):
            return 'bofa'
        elif 'balance' in headers_lower and 'description' in headers_lower:
            return 'chase'
        elif len(headers) >= 3 and any('amount' in h for h in headers_lower):
            return 'wells_fargo'
        else:
            return 'generic'
    
    def normalize_date(self, date_str: str) -> Optional[str]:
        """Normalize date to YYYY-MM-DD format."""
        if not date_str or str(date_str).lower() in ['nan', 'null', '']:
            return None
            
        date_str = str(date_str).strip()
        
        for fmt in self.supported_date_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        # Try to handle partial dates or clean up common issues
        try:
            # Remove extra spaces and common prefixes
            cleaned = re.sub(r'[^\d\-\/\s\w]', '', date_str)
            for fmt in self.supported_date_formats[:4]:  # Try basic formats
                try:
                    parsed_date = datetime.strptime(cleaned, fmt)
                    return parsed_date.strftime("%Y-%m-%d")
                except ValueError:
                    continue
        except:
            pass
            
        self.validation_errors.append(f"Invalid date format: {date_str}")
        return None
    
    def normalize_amount(self, amount_str: str) -> Optional[Decimal]:
        """Normalize amount to Decimal with proper handling of different formats."""
        if not amount_str or str(amount_str).lower() in ['nan', 'null', '']:
            return None
            
        amount_str = str(amount_str).strip()
        
        try:
            # Remove currency symbols and extra spaces
            cleaned = re.sub(r'[^\d\-\+\.,]', '', amount_str)
            
            # Handle different decimal separators
            if ',' in cleaned and '.' in cleaned:
                # Determine which is decimal separator (last occurrence)
                last_comma = cleaned.rfind(',')
                last_dot = cleaned.rfind('.')
                
                if last_dot > last_comma:
                    # Dot is decimal separator, comma is thousands
                    cleaned = cleaned.replace(',', '')
                else:
                    # Comma is decimal separator, dot is thousands
                    cleaned = cleaned.replace('.', '').replace(',', '.')
                    
            elif ',' in cleaned and len(cleaned.split(',')[-1]) <= 2:
                # Comma as decimal separator (European format)
                cleaned = cleaned.replace(',', '.')
            elif ',' in cleaned:
                # Comma as thousands separator
                cleaned = cleaned.replace(',', '')
            
            return Decimal(cleaned)
            
        except (InvalidOperation, ValueError) as e:
            self.validation_errors.append(f"Invalid amount format: {amount_str} - {str(e)}")
            return None
    
    def clean_description(self, description: str) -> str:
        """Clean and normalize transaction descriptions."""
        if not description or str(description).lower() in ['nan', 'null', '']:
            return ""
            
        description = str(description).strip()
        
        # Remove extra whitespace
        description = re.sub(r'\s+', ' ', description)
        
        # Remove common prefixes/suffixes that add noise
        patterns_to_remove = [
            r'^(DEBIT CARD|CREDIT CARD|ACH|WIRE)\s*-?\s*',
            r'\s*-\s*\d{4}$',  # Remove last 4 digits of card
            r'#\d+\s*$',       # Remove transaction numbers
            r'\*+',            # Remove asterisks
        ]
        
        for pattern in patterns_to_remove:
            description = re.sub(pattern, '', description, flags=re.IGNORECASE)
        
        # Standardize common merchant names
        merchant_mappings = {
            r'AMZN\s*MKTP': 'Amazon Marketplace',
            r'SQ\s*\*': 'Square',
            r'PAYPAL\s*\*': 'PayPal',
            r'UBER\s*TRIP': 'Uber',
            r'SPOTIFY': 'Spotify',
            r'NETFLIX': 'Netflix'
        }
        
        for pattern, replacement in merchant_mappings.items():
            description = re.sub(pattern, replacement, description, flags=re.IGNORECASE)
        
        return description.strip()
    
    def validate_transaction(self, transaction: Dict[str, Any]) -> bool:
        """Validate a single transaction record."""
        required_fields = ['date', 'amount']
        
        for field in required_fields:
            if field not in transaction or transaction[field]