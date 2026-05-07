```python
"""
Bank Statement Transaction Categorizer

This module reads CSV bank statements, categorizes transactions using regex patterns,
and stores the data in a SQLite database. It automatically categorizes transactions
into predefined categories like groceries, utilities, entertainment, dining, and transport.

Usage: python script.py

Requirements:
- CSV file named 'bank_statement.csv' in the same directory
- CSV should have columns: date, description, amount
- Creates 'transactions.db' SQLite database with categorized data
"""

import csv
import sqlite3
import re
import os
from datetime import datetime
from typing import List, Tuple, Optional


class TransactionCategorizer:
    def __init__(self, db_path: str = "transactions.db"):
        self.db_path = db_path
        self.category_patterns = {
            'groceries': [
                r'\b(walmart|target|kroger|safeway|whole foods|trader joe|costco|sam\'s club)\b',
                r'\b(grocery|supermarket|market|food store)\b',
                r'\b(publix|wegmans|harris teeter|giant|stop & shop)\b'
            ],
            'utilities': [
                r'\b(electric|electricity|gas company|water|sewer|internet|cable|phone)\b',
                r'\b(utility|utilities|power company|telecom|broadband)\b',
                r'\b(verizon|at&t|comcast|spectrum|duke energy)\b'
            ],
            'entertainment': [
                r'\b(netflix|hulu|spotify|disney|amazon prime|youtube)\b',
                r'\b(movie|theater|cinema|concert|show|event)\b',
                r'\b(entertainment|streaming|music|games)\b'
            ],
            'dining': [
                r'\b(restaurant|cafe|coffee|starbucks|mcdonald|burger|pizza)\b',
                r'\b(dining|food delivery|doordash|uber eats|grubhub)\b',
                r'\b(bar|pub|brewery|fast food|takeout)\b'
            ],
            'transport': [
                r'\b(gas station|fuel|gasoline|shell|exxon|bp|chevron)\b',
                r'\b(uber|lyft|taxi|bus|train|subway|metro)\b',
                r'\b(parking|toll|transportation|car payment|insurance)\b'
            ]
        }
    
    def create_database_schema(self) -> None:
        """Create SQLite database with categories and transactions tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create categories table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS categories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create transactions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        description TEXT NOT NULL,
                        amount REAL NOT NULL,
                        category_id INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (category_id) REFERENCES categories (id)
                    )
                ''')
                
                # Insert default categories
                categories = list(self.category_patterns.keys()) + ['other']
                for category in categories:
                    cursor.execute('''
                        INSERT OR IGNORE INTO categories (name) VALUES (?)
                    ''', (category,))
                
                conn.commit()
                print(f"Database schema created successfully at {self.db_path}")
                
        except sqlite3.Error as e:
            print(f"Error creating database schema: {e}")
            raise
    
    def categorize_transaction(self, description: str) -> str:
        """Categorize a transaction based on its description using regex patterns."""
        description_lower = description.lower()
        
        for category, patterns in self.category_patterns.items():
            for pattern in patterns:
                if re.search(pattern, description_lower, re.IGNORECASE):
                    return category
        
        return 'other'
    
    def read_csv_statements(self, csv_path: str) -> List[Tuple[str, str, float]]:
        """Read bank statements from CSV file and return list of transactions."""
        transactions = []
        
        try:
            with open(csv_path, 'r', newline='', encoding='utf-8') as file:
                # Try to detect delimiter
                sample = file.read(1024)
                file.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(file, delimiter=delimiter)
                
                for row in reader:
                    # Handle various possible column names
                    date_col = None
                    desc_col = None
                    amount_col = None
                    
                    # Find appropriate columns
                    for col in row.keys():
                        col_lower = col.lower().strip()
                        if 'date' in col_lower:
                            date_col = col
                        elif any(word in col_lower for word in ['description', 'desc', 'memo', 'payee']):
                            desc_col = col
                        elif any(word in col_lower for word in ['amount', 'debit', 'credit', 'transaction']):
                            amount_col = col
                    
                    if not all([date_col, desc_col, amount_col]):
                        print(f"Warning: Could not identify all required columns in CSV")
                        print(f"Available columns: {list(row.keys())}")
                        continue
                    
                    try:
                        date = row[date_col].strip()
                        description = row[desc_col].strip()
                        amount = float(row[amount_col].replace('$', '').replace(',', '').strip())
                        
                        transactions.append((date, description, amount))
                        
                    except (ValueError, KeyError) as e:
                        print(f"Warning: Skipping malformed row: {e}")
                        continue
            
            print(f"Successfully read {len(transactions)} transactions from {csv_path}")
            return transactions
            
        except FileNotFoundError:
            print(f"Error: CSV file '{csv_path}' not found")
            return []
        except csv.Error as e:
            print(f"Error reading CSV file: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error reading CSV: {e}")
            return []
    
    def insert_transactions(self, transactions: List[Tuple[str, str, float]]) -> None:
        """Insert transactions into the database with categories."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get category IDs
                cursor.execute("SELECT id, name FROM categories")
                category_map = {name: id for id, name in cursor.fetchall()}
                
                inserted_count = 0
                for date, description, amount in transactions:
                    try:
                        category = self.categorize_transaction(description)
                        category_id = category_map.get(category, category_map['other'])
                        
                        cursor.execute('''
                            INSERT INTO transactions (date, description, amount, category_id)
                            VALUES (?, ?, ?, ?)
                        ''', (date, description, amount, category_id))
                        
                        inserted_count += 1
                        
                    except sqlite3.Error as e:
                        print(f"Error inserting transaction '{description}': {e}")
                        continue
                
                conn.commit()
                print(f"Successfully inserted {inserted_count} transactions into database")
                
        except sqlite3.Error as e:
            print(f"Database error during insertion: {e}")
            raise
    
    def print_summary(self) -> None:
        """Print a summary of categorized transactions."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()