```python
"""
Bank Transaction CSV Parser and Categorizer

This module parses CSV files containing bank transaction data, validates the format,
and uses OpenAI's API to automatically categorize transactions into predefined types
such as food, transport, entertainment, utilities, shopping, etc.

The script expects CSV files with columns: date, description, amount
Transactions are categorized using OpenAI's GPT model based on transaction descriptions.

Usage: python script.py
Place your CSV file as 'transactions.csv' in the same directory.
"""

import csv
import json
import os
import re
from datetime import datetime
from typing import List, Dict, Optional
import httpx


class TransactionCategorizer:
    """Handles transaction parsing, validation, and categorization."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable.")
        
        self.categories = [
            'food', 'transport', 'entertainment', 'utilities', 
            'shopping', 'healthcare', 'education', 'income', 
            'banking', 'insurance', 'other'
        ]
    
    def validate_date(self, date_str: str) -> bool:
        """Validate date format (YYYY-MM-DD or MM/DD/YYYY or DD/MM/YYYY)."""
        try:
            # Try multiple common date formats
            formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']
            for fmt in formats:
                try:
                    datetime.strptime(date_str.strip(), fmt)
                    return True
                except ValueError:
                    continue
            return False
        except Exception:
            return False
    
    def validate_amount(self, amount_str: str) -> bool:
        """Validate amount format (numeric with optional currency symbols)."""
        try:
            # Remove currency symbols and commas
            cleaned = re.sub(r'[$,£€¥]', '', amount_str.strip())
            float(cleaned)
            return True
        except (ValueError, TypeError):
            return False
    
    def parse_csv(self, filename: str) -> List[Dict]:
        """Parse CSV file and validate transaction data."""
        transactions = []
        
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                # Try to detect delimiter
                sample = file.read(1024)
                file.seek(0)
                
                delimiter = ','
                if ';' in sample and sample.count(';') > sample.count(','):
                    delimiter = ';'
                
                reader = csv.DictReader(file, delimiter=delimiter)
                
                # Normalize column names (handle common variations)
                fieldnames = [field.lower().strip() for field in reader.fieldnames or []]
                
                # Map common column name variations
                column_mapping = {}
                for field in fieldnames:
                    if any(name in field for name in ['date', 'transaction_date', 'trans_date']):
                        column_mapping['date'] = reader.fieldnames[fieldnames.index(field)]
                    elif any(name in field for name in ['description', 'desc', 'merchant', 'payee']):
                        column_mapping['description'] = reader.fieldnames[fieldnames.index(field)]
                    elif any(name in field for name in ['amount', 'value', 'debit', 'credit']):
                        column_mapping['amount'] = reader.fieldnames[fieldnames.index(field)]
                
                if len(column_mapping) < 3:
                    raise ValueError("CSV must contain date, description, and amount columns")
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        date = row[column_mapping['date']]
                        description = row[column_mapping['description']]
                        amount = row[column_mapping['amount']]
                        
                        # Validate data
                        if not self.validate_date(date):
                            print(f"Warning: Invalid date format in row {row_num}: {date}")
                            continue
                        
                        if not description or description.strip() == '':
                            print(f"Warning: Empty description in row {row_num}")
                            continue
                        
                        if not self.validate_amount(amount):
                            print(f"Warning: Invalid amount format in row {row_num}: {amount}")
                            continue
                        
                        transactions.append({
                            'date': date.strip(),
                            'description': description.strip(),
                            'amount': amount.strip(),
                            'row_number': row_num
                        })
                    
                    except KeyError as e:
                        print(f"Error: Missing required column in row {row_num}: {e}")
                        continue
        
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file '{filename}' not found")
        except Exception as e:
            raise Exception(f"Error parsing CSV file: {str(e)}")
        
        return transactions
    
    def categorize_transaction(self, description: str) -> str:
        """Categorize a single transaction using OpenAI API."""
        try:
            prompt = f"""
            Categorize this bank transaction description into one of these categories:
            {', '.join(self.categories)}
            
            Transaction description: "{description}"
            
            Respond with only the category name, nothing else.
            """
            
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-3.5-turbo",
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": 20,
                        "temperature": 0.1
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    category = result['choices'][0]['message']['content'].strip().lower()
                    
                    # Validate category is in our predefined list
                    if category in self.categories:
                        return category
                    else:
                        return 'other'
                else:
                    print(f"API Error {response.status_code}: {response.text}")
                    return 'other'
        
        except Exception as e:
            print(f"Error categorizing transaction '{description}': {str(e)}")
            return 'other'
    
    def process_transactions(self, filename: str = 'transactions.csv'):
        """Main processing function."""
        try:
            print("Parsing CSV file...")
            transactions = self.parse_csv(filename)
            
            if not transactions:
                print("No valid transactions found in the CSV file.")
                return
            
            print(f"Found {len(transactions)} valid transactions.")
            print("\nCategorizing transactions...")
            
            categorized = []
            for i, transaction in enumerate(transactions, 1):
                print(f"Processing transaction {i}/{len(transactions)}: {transaction['description'][:50]}...")
                
                category = self.categorize_transaction(transaction['description'])
                
                categorized.append({
                    **transaction,
                    'category': category
                })
            
            # Print results
            print("\n" + "="*80)
            print("CATEGORIZED TRANSACTIONS")
            print("="*80)
            
            for transaction in categorized:
                print(f"Date: {transaction['date']}")
                print(f"Description: {transaction['description']}")
                print(f"Amount: {transaction['amount']}")
                print(f"Category: {transaction['category'].upper()}")
                print("-" * 40)
            
            # Summary by category
            print("\nCATEGORY SUMMARY")
            print("="*30)