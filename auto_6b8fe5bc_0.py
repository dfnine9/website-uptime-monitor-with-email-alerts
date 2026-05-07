```python
#!/usr/bin/env python3
"""
Transaction Categorization Script

This module reads CSV files containing financial transactions, applies keyword-based
categorization rules, and outputs categorized transactions with spending summaries
to new CSV files. It processes transaction data to automatically categorize expenses
based on description patterns and generates summary reports.

Features:
- Reads transaction data from CSV files
- Applies customizable keyword-based categorization rules
- Generates categorized transaction output
- Creates spending summaries by category
- Handles multiple input formats with error recovery
- Self-contained with minimal dependencies

Usage: python script.py
"""

import csv
import re
import os
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Any

class TransactionCategorizer:
    """Handles transaction categorization and summary generation."""
    
    def __init__(self):
        self.categories = {
            'Food & Dining': [
                'restaurant', 'cafe', 'coffee', 'pizza', 'burger', 'food', 'dining',
                'mcdonalds', 'starbucks', 'subway', 'kfc', 'dominos', 'uber eats',
                'doordash', 'grubhub', 'takeout', 'delivery'
            ],
            'Transportation': [
                'gas', 'fuel', 'uber', 'lyft', 'taxi', 'parking', 'toll', 'metro',
                'bus', 'train', 'airline', 'flight', 'car wash', 'auto', 'vehicle'
            ],
            'Shopping': [
                'amazon', 'target', 'walmart', 'costco', 'store', 'shopping',
                'retail', 'purchase', 'buy', 'mall', 'boutique'
            ],
            'Utilities': [
                'electric', 'electricity', 'gas bill', 'water', 'internet',
                'phone', 'mobile', 'cable', 'utility', 'power', 'energy'
            ],
            'Healthcare': [
                'pharmacy', 'doctor', 'hospital', 'medical', 'health', 'clinic',
                'dental', 'vision', 'prescription', 'medicine', 'cvs', 'walgreens'
            ],
            'Entertainment': [
                'movie', 'theater', 'netflix', 'spotify', 'gaming', 'game',
                'entertainment', 'concert', 'show', 'ticket', 'streaming'
            ],
            'Banking & Finance': [
                'bank', 'atm', 'fee', 'interest', 'loan', 'credit', 'finance',
                'payment', 'transfer', 'withdrawal', 'deposit'
            ],
            'Home & Garden': [
                'home depot', 'lowes', 'hardware', 'garden', 'furniture',
                'appliance', 'repair', 'maintenance', 'cleaning'
            ]
        }
    
    def categorize_transaction(self, description: str) -> str:
        """Categorize a transaction based on its description."""
        description_lower = description.lower()
        
        # Check each category's keywords
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'Other'
    
    def process_transactions(self, transactions: List[Dict]) -> Tuple[List[Dict], Dict[str, Dict]]:
        """Process transactions and generate summaries."""
        categorized_transactions = []
        category_summaries = defaultdict(lambda: {'count': 0, 'total': 0.0, 'transactions': []})
        
        for transaction in transactions:
            try:
                # Extract and clean amount
                amount_str = str(transaction.get('amount', '0')).replace('$', '').replace(',', '')
                amount = float(amount_str)
                
                # Categorize transaction
                description = transaction.get('description', '')
                category = self.categorize_transaction(description)
                
                # Add category to transaction
                categorized_transaction = transaction.copy()
                categorized_transaction['category'] = category
                categorized_transactions.append(categorized_transaction)
                
                # Update summaries
                category_summaries[category]['count'] += 1
                category_summaries[category]['total'] += abs(amount)  # Use absolute value for summaries
                category_summaries[category]['transactions'].append(categorized_transaction)
                
            except (ValueError, TypeError) as e:
                print(f"Warning: Error processing transaction {transaction}: {e}")
                # Add uncategorized transaction
                categorized_transaction = transaction.copy()
                categorized_transaction['category'] = 'Error'
                categorized_transactions.append(categorized_transaction)
        
        return categorized_transactions, dict(category_summaries)

def detect_csv_format(filepath: str) -> Dict[str, str]:
    """Detect CSV format and return column mappings."""
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            # Read first few lines to detect format
            sample = file.read(1024)
            file.seek(0)
            
            # Try to detect delimiter
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
            # Read header row
            reader = csv.DictReader(file, delimiter=delimiter)
            fieldnames = reader.fieldnames or []
            
            # Map common column variations to standard names
            column_mapping = {}
            for field in fieldnames:
                field_lower = field.lower()
                if any(term in field_lower for term in ['date', 'time']):
                    column_mapping['date'] = field
                elif any(term in field_lower for term in ['amount', 'value', 'sum', 'total']):
                    column_mapping['amount'] = field
                elif any(term in field_lower for term in ['desc', 'description', 'memo', 'detail']):
                    column_mapping['description'] = field
                elif any(term in field_lower for term in ['merchant', 'vendor', 'payee']):
                    column_mapping['merchant'] = field
            
            return {'delimiter': delimiter, 'columns': column_mapping}
            
    except Exception as e:
        print(f"Error detecting CSV format: {e}")
        return {'delimiter': ',', 'columns': {}}

def read_transactions_csv(filepath: str) -> List[Dict]:
    """Read transactions from CSV file with automatic format detection."""
    transactions = []
    
    try:
        format_info = detect_csv_format(filepath)
        delimiter = format_info.get('delimiter', ',')
        column_mapping = format_info.get('columns', {})
        
        with open(filepath, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=delimiter)
            
            for row_num, row in enumerate(reader, 1):
                try:
                    # Map columns to standard format
                    transaction = {
                        'date': row.get(column_mapping.get('date', 'date'), ''),
                        'amount': row.get(column_mapping.get('amount', 'amount'), '0'),
                        'description': row.get(column_mapping.get('description', 'description'), ''),
                        'merchant': row.get(column_mapping.get('merchant', 'merchant'), ''),
                        'original_row': row_num
                    }
                    
                    # If no column mapping found, try to use row as-is
                    if not column_mapping:
                        transaction.update(row)
                    
                    transactions.append(transaction)
                    
                except Exception as e:
                    print(f"Warning: Error reading row {row_num}: {e}")
                    
    except FileNotFoundError:
        print(f"Error: File {filepath} not found")
    except Exception as e:
        print(f"Error reading CSV file: {e}")
    
    return transactions

def write_categorized_csv(transactions: List[Dict], output_filepath: str):
    """Write categorized transactions to CSV file."""
    try:
        if not transactions:
            print("No transactions to write")