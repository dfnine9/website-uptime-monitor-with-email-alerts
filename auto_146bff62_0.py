```python
"""
Bank Transaction Parser and Categorizer

This module provides functionality to parse bank CSV files with configurable column mapping,
validate transaction data format, and automatically categorize transactions using regex-based
keyword matching for common expense types like groceries, gas, restaurants, utilities, etc.

The script supports flexible column mapping to accommodate different bank CSV formats and
includes comprehensive error handling for data validation and file processing.

Usage:
    python script.py

The script will look for 'transactions.csv' in the current directory and output categorized
transactions to stdout.
"""

import csv
import re
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import json


class TransactionCategorizer:
    """Handles categorization of transactions using regex patterns."""
    
    def __init__(self):
        self.category_patterns = {
            'groceries': [
                r'\b(walmart|target|kroger|safeway|publix|whole foods|trader joe|costco|sam\'s club)\b',
                r'\b(grocery|supermarket|market|food)\b',
                r'\b(aldi|wegmans|harris teeter|food lion|giant|stop shop)\b'
            ],
            'gas': [
                r'\b(shell|exxon|bp|chevron|texaco|mobil|sunoco|speedway)\b',
                r'\b(gas|fuel|petroleum)\b',
                r'\b(station|pump)\b'
            ],
            'restaurants': [
                r'\b(restaurant|cafe|bistro|diner|pizza|burger)\b',
                r'\b(mcdonald|burger king|taco bell|subway|kfc|pizza hut|domino)\b',
                r'\b(starbucks|dunkin|coffee)\b',
                r'\b(dining|takeout|delivery)\b'
            ],
            'utilities': [
                r'\b(electric|electricity|power|energy)\b',
                r'\b(gas company|water|sewer|trash|garbage)\b',
                r'\b(utility|utilities|pge|sdge|edison)\b',
                r'\b(internet|cable|phone|wireless|verizon|at&t|comcast)\b'
            ],
            'entertainment': [
                r'\b(netflix|hulu|disney|spotify|amazon prime)\b',
                r'\b(movie|cinema|theater|theatre)\b',
                r'\b(game|gaming|xbox|playstation|steam)\b',
                r'\b(entertainment|recreation)\b'
            ],
            'shopping': [
                r'\b(amazon|ebay|etsy|shopping)\b',
                r'\b(department store|mall|retail)\b',
                r'\b(clothing|apparel|shoes)\b'
            ],
            'healthcare': [
                r'\b(pharmacy|cvs|walgreens|rite aid)\b',
                r'\b(doctor|medical|health|hospital|clinic)\b',
                r'\b(dental|dentist|vision|optometry)\b'
            ],
            'transportation': [
                r'\b(uber|lyft|taxi|rideshare)\b',
                r'\b(metro|bus|train|subway|transit)\b',
                r'\b(parking|toll|bridge)\b'
            ],
            'banking': [
                r'\b(atm|fee|charge|transfer)\b',
                r'\b(bank|credit|debit)\b',
                r'\b(interest|dividend)\b'
            ]
        }
        
        # Compile patterns for efficiency
        self.compiled_patterns = {}
        for category, patterns in self.category_patterns.items():
            self.compiled_patterns[category] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]
    
    def categorize(self, description: str) -> str:
        """Categorize a transaction based on its description."""
        if not description:
            return 'other'
        
        description = description.lower().strip()
        
        for category, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(description):
                    return category
        
        return 'other'


class TransactionValidator:
    """Validates transaction data format and content."""
    
    @staticmethod
    def validate_date(date_str: str, date_formats: List[str]) -> Optional[datetime]:
        """Validate and parse date string using multiple format attempts."""
        if not date_str:
            return None
        
        for date_format in date_formats:
            try:
                return datetime.strptime(date_str.strip(), date_format)
            except ValueError:
                continue
        return None
    
    @staticmethod
    def validate_amount(amount_str: str) -> Optional[float]:
        """Validate and parse amount string."""
        if not amount_str:
            return None
        
        # Remove common currency symbols and whitespace
        cleaned = re.sub(r'[$,\s]', '', amount_str.strip())
        
        try:
            # Handle negative amounts in parentheses
            if cleaned.startswith('(') and cleaned.endswith(')'):
                cleaned = '-' + cleaned[1:-1]
            
            return float(cleaned)
        except ValueError:
            return None
    
    @staticmethod
    def validate_description(description: str) -> str:
        """Validate and clean description string."""
        if not description:
            return ''
        return description.strip()


class BankCSVParser:
    """Main parser class for bank CSV files."""
    
    def __init__(self, column_mapping: Dict[str, str]):
        """
        Initialize parser with column mapping.
        
        Args:
            column_mapping: Dict mapping standard fields to CSV column names
                          Expected keys: 'date', 'description', 'amount'
        """
        self.column_mapping = column_mapping
        self.validator = TransactionValidator()
        self.categorizer = TransactionCategorizer()
        
        # Common date formats to try
        self.date_formats = [
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%m/%d/%y',
            '%d/%m/%Y',
            '%d/%m/%y',
            '%Y/%m/%d',
            '%m-%d-%Y',
            '%m-%d-%y',
            '%d-%m-%Y',
            '%d-%m-%y'
        ]
    
    def parse_csv(self, filename: str) -> List[Dict]:
        """
        Parse CSV file and return list of validated, categorized transactions.
        
        Args:
            filename: Path to CSV file
            
        Returns:
            List of transaction dictionaries
            
        Raises:
            FileNotFoundError: If CSV file doesn't exist
            ValueError: If required columns are missing
        """
        transactions = []
        errors = []
        
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                # Try to detect delimiter
                sample = file.read(1024)
                file.seek(0)
                
                delimiter = ',' if sample.count(',') > sample.count(';') else ';'
                
                reader = csv.DictReader(file, delimiter=delimiter)
                
                # Validate required columns exist
                fieldnames = reader.fieldnames or []
                missing_cols = []
                for required_field, csv_col in self.column_mapping.items():
                    if csv_col not in fieldnames:
                        missing_cols.append(csv_col)
                
                if missing_cols:
                    raise ValueError(f"Missing required columns: {missing_cols}")
                
                for row_num, row in enumerate(reader, start=2):  # Start at 2 for header
                    try:
                        transaction = self._parse_row(row)
                        if transaction:
                            transactions.append(transaction)
                    except Exception as e:
                        errors.append(f"Row {row_num}: {str(e)}")
                        continue
        
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file '{filename}' not found")
        except Exception as e:
            raise ValueError(f"Error reading CSV file: {str(e)}")
        
        if errors:
            print(f"Parsing errors encountered:\n" + "\n".join