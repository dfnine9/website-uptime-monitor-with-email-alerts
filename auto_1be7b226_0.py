```python
"""
Transaction Categorization and Analysis Tool

This module provides a CSV parser that automatically categorizes financial transactions
using regex-based rules and generates comprehensive summary statistics. It processes
transaction data from CSV files and classifies entries into predefined categories
such as groceries, utilities, entertainment, etc.

Features:
- Regex-based transaction categorization
- CSV parsing with flexible column mapping
- Statistical analysis and reporting
- Error handling for malformed data
- Summary report generation

Usage:
    python script.py

The script will create sample transaction data if no CSV file is found,
then process and categorize all transactions, generating a detailed
summary report with statistics by category.
"""

import csv
import re
import os
from collections import defaultdict, Counter
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class TransactionCategorizer:
    """Categorizes transactions using regex-based rules."""
    
    def __init__(self):
        # Define categorization rules using regex patterns
        self.category_rules = {
            'Groceries': [
                r'\b(?:grocery|supermarket|food|walmart|target|costco|safeway)\b',
                r'\b(?:kroger|albertsons|whole foods|trader joe)\b'
            ],
            'Utilities': [
                r'\b(?:electric|gas|water|internet|phone|cable|utility)\b',
                r'\b(?:verizon|at&t|comcast|pge|edison)\b'
            ],
            'Transportation': [
                r'\b(?:gas|fuel|uber|lyft|taxi|metro|bus|train|parking)\b',
                r'\b(?:chevron|shell|exxon|mobil|arco)\b'
            ],
            'Entertainment': [
                r'\b(?:movie|cinema|theater|netflix|spotify|game|bar|club)\b',
                r'\b(?:restaurant|dining|coffee|starbucks)\b'
            ],
            'Healthcare': [
                r'\b(?:pharmacy|doctor|hospital|medical|dentist|cvs|walgreens)\b',
                r'\b(?:health|clinic|urgent care)\b'
            ],
            'Shopping': [
                r'\b(?:amazon|ebay|store|retail|mall|shopping)\b',
                r'\b(?:best buy|home depot|lowes)\b'
            ],
            'Banking': [
                r'\b(?:bank|atm|fee|transfer|deposit|withdrawal)\b',
                r'\b(?:chase|wells fargo|bofa|citibank)\b'
            ]
        }
    
    def categorize_transaction(self, description: str, amount: float) -> str:
        """
        Categorize a transaction based on description and amount.
        
        Args:
            description: Transaction description
            amount: Transaction amount
            
        Returns:
            Category name or 'Other' if no match found
        """
        if not description:
            return 'Other'
            
        description_lower = description.lower()
        
        # Check each category's rules
        for category, patterns in self.category_rules.items():
            for pattern in patterns:
                if re.search(pattern, description_lower, re.IGNORECASE):
                    return category
        
        # Special rules based on amount
        if amount < -500:  # Large negative amounts might be rent/mortgage
            if re.search(r'\b(?:rent|mortgage|property)\b', description_lower):
                return 'Housing'
        
        return 'Other'


class TransactionParser:
    """Parses CSV files containing transaction data."""
    
    def __init__(self):
        self.categorizer = TransactionCategorizer()
        
    def parse_csv(self, filepath: str) -> List[Dict]:
        """
        Parse CSV file and return list of transaction dictionaries.
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            List of transaction dictionaries
        """
        transactions = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                # Try to detect delimiter
                sample = file.read(1024)
                file.seek(0)
                
                delimiter = ',' if sample.count(',') > sample.count(';') else ';'
                
                reader = csv.DictReader(file, delimiter=delimiter)
                
                for row_num, row in enumerate(reader, 1):
                    try:
                        transaction = self._parse_transaction_row(row)
                        if transaction:
                            transactions.append(transaction)
                    except Exception as e:
                        print(f"Warning: Error parsing row {row_num}: {e}")
                        continue
                        
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file not found: {filepath}")
        except Exception as e:
            raise Exception(f"Error reading CSV file: {e}")
            
        return transactions
    
    def _parse_transaction_row(self, row: Dict) -> Optional[Dict]:
        """
        Parse a single transaction row from CSV.
        
        Args:
            row: Dictionary representing CSV row
            
        Returns:
            Parsed transaction dictionary or None if invalid
        """
        # Try different common column name variations
        date_fields = ['date', 'Date', 'DATE', 'transaction_date', 'trans_date']
        desc_fields = ['description', 'Description', 'DESC', 'memo', 'Memo']
        amount_fields = ['amount', 'Amount', 'AMOUNT', 'value', 'Value']
        
        # Extract date
        date_str = None
        for field in date_fields:
            if field in row and row[field]:
                date_str = row[field]
                break
                
        if not date_str:
            return None
            
        # Extract description
        description = None
        for field in desc_fields:
            if field in row and row[field]:
                description = row[field].strip()
                break
                
        if not description:
            return None
            
        # Extract amount
        amount_str = None
        for field in amount_fields:
            if field in row and row[field]:
                amount_str = row[field]
                break
                
        if not amount_str:
            return None
            
        # Parse amount (handle various formats)
        try:
            # Remove currency symbols and spaces
            amount_clean = re.sub(r'[^\d.-]', '', str(amount_str))
            amount = float(amount_clean)
        except (ValueError, TypeError):
            return None
            
        # Parse date
        try:
            # Try common date formats
            date_formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']
            parsed_date = None
            
            for date_format in date_formats:
                try:
                    parsed_date = datetime.strptime(date_str, date_format)
                    break
                except ValueError:
                    continue
                    
            if not parsed_date:
                # Fallback: try to parse any recognizable date
                parsed_date = datetime.now()  # Use current date as fallback
                
        except Exception:
            parsed_date = datetime.now()
            
        # Categorize transaction
        category = self.categorizer.categorize_transaction(description, amount)
        
        return {
            'date': parsed_date,
            'description': description,
            'amount': amount,
            'category': category
        }


class StatisticsGenerator:
    """Generates summary statistics for transactions."""
    
    def generate_summary(self, transactions: List[Dict]) -> Dict:
        """
        Generate comprehensive summary statistics.
        
        Args:
            transactions: List of transaction dictionaries
            
        Returns:
            Dictionary containing summary statistics
        """
        if not transactions:
            return {'error': 'No transactions to analyze'}
            
        # Basic statistics
        total_transactions = len(transactions)
        total_amount = sum(t['amount'] for t in transactions)
        avg_amount = total_amount / total_transactions
        
        # Separate income and expenses
        income_transactions = [t for t in transactions if t['amount'] > 0]
        expense_transactions = [t for t in transactions if t['amount'] < 0]
        
        total_income =