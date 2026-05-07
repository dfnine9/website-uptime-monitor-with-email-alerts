```python
"""
Bank Statement Transaction Categorizer

This module parses CSV bank statements and automatically categorizes transactions
using regex pattern matching on merchant names and transaction descriptions.
It validates categorization accuracy and provides detailed reporting.

Features:
- CSV parsing with pandas-like functionality using only standard library
- Regex-based transaction categorization
- Category validation and accuracy reporting
- Comprehensive error handling
- Sample data generation for testing

Usage: python script.py
"""

import csv
import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from collections import defaultdict, Counter
import random


class BankStatementCategorizer:
    """Categorizes bank transactions using regex pattern matching."""
    
    def __init__(self):
        self.categories = {
            'Groceries': [
                r'(?i)\b(walmart|target|kroger|safeway|whole foods|trader joe|costco|sam\'s club)\b',
                r'(?i)\b(grocery|market|food|supermarket)\b',
                r'(?i)\b(aldi|publix|wegmans|harris teeter)\b'
            ],
            'Gas': [
                r'(?i)\b(shell|exxon|bp|chevron|mobil|texaco|sunoco|marathon)\b',
                r'(?i)\b(gas|fuel|station|pump)\b'
            ],
            'Dining': [
                r'(?i)\b(mcdonald|burger king|subway|starbucks|pizza|restaurant)\b',
                r'(?i)\b(cafe|bistro|grill|bar|diner|food truck)\b',
                r'(?i)\b(doordash|uber eats|grubhub|postmates)\b'
            ],
            'Shopping': [
                r'(?i)\b(amazon|ebay|etsy|best buy|home depot|lowes)\b',
                r'(?i)\b(store|shop|retail|mall|outlet)\b',
                r'(?i)\b(clothing|apparel|shoes|electronics)\b'
            ],
            'Utilities': [
                r'(?i)\b(electric|electricity|power|gas company|water|sewer)\b',
                r'(?i)\b(utility|utilities|bill|service)\b',
                r'(?i)\b(internet|cable|phone|wireless|verizon|at&t|comcast)\b'
            ],
            'Transportation': [
                r'(?i)\b(uber|lyft|taxi|bus|metro|transit|parking)\b',
                r'(?i)\b(airline|flight|rental car|train|amtrak)\b'
            ],
            'Healthcare': [
                r'(?i)\b(doctor|medical|hospital|pharmacy|cvs|walgreens)\b',
                r'(?i)\b(dental|dentist|vision|optometry|health)\b'
            ],
            'Banking': [
                r'(?i)\b(atm|withdrawal|deposit|transfer|fee|charge)\b',
                r'(?i)\b(bank|credit|debit|finance|loan)\b'
            ]
        }
        
        self.transactions = []
        self.categorized_transactions = []
        
    def generate_sample_data(self, filename: str = 'sample_bank_statement.csv') -> None:
        """Generate sample CSV bank statement for testing."""
        sample_transactions = [
            ['2024-01-15', 'WALMART SUPERCENTER', -89.42, 'Debit'],
            ['2024-01-14', 'STARBUCKS #1234', -5.75, 'Debit'],
            ['2024-01-13', 'SHELL GAS STATION', -45.20, 'Debit'],
            ['2024-01-12', 'AMAZON.COM PURCHASE', -156.78, 'Debit'],
            ['2024-01-11', 'ELECTRIC COMPANY BILL', -127.35, 'ACH'],
            ['2024-01-10', 'UBER TRIP', -23.50, 'Debit'],
            ['2024-01-09', 'CVS PHARMACY', -18.95, 'Debit'],
            ['2024-01-08', 'ATM WITHDRAWAL', -100.00, 'ATM'],
            ['2024-01-07', 'PIZZA HUT ONLINE', -28.65, 'Debit'],
            ['2024-01-06', 'HOME DEPOT STORE', -234.89, 'Debit'],
            ['2024-01-05', 'SALARY DEPOSIT', 3500.00, 'Direct Deposit'],
            ['2024-01-04', 'KROGER GROCERY', -67.43, 'Debit'],
            ['2024-01-03', 'EXXON MOBIL', -52.30, 'Debit'],
            ['2024-01-02', 'NETFLIX MONTHLY', -15.99, 'ACH'],
            ['2024-01-01', 'DOORDASH DELIVERY', -35.75, 'Debit']
        ]
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Date', 'Description', 'Amount', 'Type'])
                writer.writerows(sample_transactions)
            print(f"Generated sample data in {filename}")
        except Exception as e:
            print(f"Error generating sample data: {e}")
    
    def parse_csv(self, filename: str) -> bool:
        """Parse CSV bank statement file."""
        try:
            with open(filename, 'r', encoding='utf-8') as csvfile:
                # Detect delimiter
                sample = csvfile.read(1024)
                csvfile.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        # Normalize column names
                        normalized_row = {}
                        for key, value in row.items():
                            key_lower = key.lower().strip()
                            if 'date' in key_lower:
                                normalized_row['date'] = value.strip()
                            elif 'description' in key_lower or 'merchant' in key_lower or 'payee' in key_lower:
                                normalized_row['description'] = value.strip()
                            elif 'amount' in key_lower:
                                normalized_row['amount'] = value.strip()
                            elif 'type' in key_lower or 'category' in key_lower:
                                normalized_row['type'] = value.strip()
                        
                        # Validate required fields
                        if 'date' not in normalized_row or 'description' not in normalized_row or 'amount' not in normalized_row:
                            print(f"Warning: Row {row_num} missing required fields, skipping")
                            continue
                        
                        # Parse amount
                        amount_str = normalized_row['amount'].replace('$', '').replace(',', '')
                        amount = float(amount_str)
                        
                        transaction = {
                            'date': normalized_row['date'],
                            'description': normalized_row['description'],
                            'amount': amount,
                            'type': normalized_row.get('type', ''),
                            'row_number': row_num
                        }
                        
                        self.transactions.append(transaction)
                        
                    except (ValueError, KeyError) as e:
                        print(f"Error parsing row {row_num}: {e}")
                        continue
                
                print(f"Successfully parsed {len(self.transactions)} transactions")
                return True
                
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found")
            return False
        except Exception as e:
            print(f"Error parsing CSV: {e}")
            return False
    
    def categorize_transaction(self, description: str) -> Tuple[str, float]:
        """Categor