```python
#!/usr/bin/env python3
"""
Transaction Categorizer

This script reads CSV transaction files and automatically categorizes transactions 
into predefined expense categories using regex patterns and keyword matching.

Categories supported:
- Food & Dining
- Transportation
- Utilities
- Entertainment
- Healthcare
- Shopping
- Bills & Finance
- Travel
- Education
- Other

The script processes CSV files with transaction data and outputs categorized results
to stdout. It uses pattern matching on transaction descriptions and merchant names
to assign appropriate categories.

Usage: python script.py
"""

import csv
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class TransactionCategorizer:
    def __init__(self):
        self.categories = {
            'Food & Dining': [
                r'\b(restaurant|cafe|coffee|pizza|burger|mcdonald|subway|starbucks|domino|kfc)\b',
                r'\b(grocery|supermarket|walmart|target|costco|safeway|kroger|food|dining)\b',
                r'\b(uber\s*eats|doordash|grubhub|postmates|seamless)\b',
                r'\b(bar|pub|brewery|tavern|bistro|diner|bakery)\b'
            ],
            'Transportation': [
                r'\b(gas|gasoline|fuel|shell|exxon|chevron|bp|mobil)\b',
                r'\b(uber|lyft|taxi|cab|transit|metro|bus|train|parking)\b',
                r'\b(airline|flight|airport|car\s*rental|hertz|avis|enterprise)\b',
                r'\b(toll|bridge|highway|dmv|registration|insurance.*auto)\b'
            ],
            'Utilities': [
                r'\b(electric|electricity|gas\s*company|water|sewer|trash|garbage)\b',
                r'\b(phone|cellular|verizon|at&t|sprint|t-mobile|internet|cable)\b',
                r'\b(utility|pge|edison|comcast|xfinity|spectrum|cox)\b'
            ],
            'Entertainment': [
                r'\b(movie|cinema|theater|netflix|hulu|spotify|amazon\s*prime)\b',
                r'\b(game|gaming|steam|playstation|xbox|nintendo)\b',
                r'\b(concert|event|ticket|entertainment|amusement)\b',
                r'\b(gym|fitness|yoga|sports|recreation)\b'
            ],
            'Healthcare': [
                r'\b(doctor|medical|hospital|pharmacy|cvs|walgreens|rite\s*aid)\b',
                r'\b(dental|dentist|vision|optometry|health|clinic)\b',
                r'\b(prescription|medicine|drug|therapeutic)\b'
            ],
            'Shopping': [
                r'\b(amazon|ebay|shop|store|retail|mall|outlet)\b',
                r'\b(clothing|apparel|fashion|shoes|accessories)\b',
                r'\b(home\s*depot|lowes|furniture|electronics|best\s*buy)\b',
                r'\b(department|boutique|brand)\b'
            ],
            'Bills & Finance': [
                r'\b(bank|credit|loan|mortgage|rent|lease|payment)\b',
                r'\b(fee|charge|interest|penalty|overdraft|transfer)\b',
                r'\b(insurance|tax|irs|subscription|membership)\b'
            ],
            'Travel': [
                r'\b(hotel|motel|airbnb|booking|expedia|travel|vacation)\b',
                r'\b(resort|lodge|inn|hostel|tourism)\b'
            ],
            'Education': [
                r'\b(school|university|college|education|tuition|textbook)\b',
                r'\b(course|class|training|learning|academic)\b'
            ]
        }
        
        # Compile regex patterns for better performance
        self.compiled_patterns = {}
        for category, patterns in self.categories.items():
            self.compiled_patterns[category] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]
    
    def categorize_transaction(self, description: str, merchant: str = "") -> str:
        """
        Categorize a transaction based on description and merchant name.
        
        Args:
            description: Transaction description
            merchant: Merchant name (optional)
            
        Returns:
            Category name or 'Other' if no match found
        """
        text = f"{description} {merchant}".lower().strip()
        
        for category, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(text):
                    return category
        
        return 'Other'
    
    def process_csv(self, filepath: str) -> List[Dict]:
        """
        Process a CSV file and categorize transactions.
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            List of transaction dictionaries with categories
        """
        transactions = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                # Try to detect delimiter
                sample = file.read(1024)
                file.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(file, delimiter=delimiter)
                
                for row_num, row in enumerate(reader, 1):
                    try:
                        # Flexible column mapping - try common column names
                        description = (
                            row.get('description', '') or 
                            row.get('Description', '') or
                            row.get('DESCRIPTION', '') or
                            row.get('memo', '') or
                            row.get('Memo', '') or
                            row.get('details', '') or
                            ''
                        )
                        
                        merchant = (
                            row.get('merchant', '') or
                            row.get('Merchant', '') or
                            row.get('payee', '') or
                            row.get('Payee', '') or
                            ''
                        )
                        
                        amount = (
                            row.get('amount', '') or
                            row.get('Amount', '') or
                            row.get('AMOUNT', '') or
                            '0'
                        )
                        
                        date = (
                            row.get('date', '') or
                            row.get('Date', '') or
                            row.get('DATE', '') or
                            row.get('transaction_date', '') or
                            ''
                        )
                        
                        if not description and not merchant:
                            print(f"Warning: Row {row_num} has no description or merchant, skipping")
                            continue
                        
                        category = self.categorize_transaction(description, merchant)
                        
                        transaction = {
                            'date': date,
                            'description': description,
                            'merchant': merchant,
                            'amount': amount,
                            'category': category,
                            'original_row': row_num
                        }
                        
                        transactions.append(transaction)
                        
                    except Exception as e:
                        print(f"Error processing row {row_num}: {e}")
                        continue
                        
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file not found: {filepath}")
        except Exception as e:
            raise Exception(f"Error reading CSV file: {e}")
        
        return transactions
    
    def generate_report(self, transactions: List[Dict]) -> None:
        """Generate and print categorization report."""
        if not transactions:
            print("No transactions to categorize.")
            return
        
        # Category summary
        category_counts = {}
        category_amounts = {}
        
        for transaction in transactions:
            category = transaction['category']
            category_counts[category] = category_counts.get(category, 0) + 1
            
            try:
                amount = float(str(transaction['amount']).replace('$', '').replace(',', ''))
                category_amounts[category] = category_amounts.get(category, 0) + abs(amount)
            except (ValueError, TypeError):
                pass