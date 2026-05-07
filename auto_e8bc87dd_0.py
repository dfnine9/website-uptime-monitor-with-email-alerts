```python
#!/usr/bin/env python3
"""
Bank Transaction Categorization Dataset Generator

This script reads bank transaction CSV files and creates a training dataset
for transaction categorization. It processes transaction descriptions and amounts,
then assigns sample category labels based on common patterns.

Categories include: groceries, gas, restaurants, utilities, shopping, entertainment,
healthcare, banking, travel, and other.

Usage: python script.py

The script looks for CSV files in the current directory with columns containing
transaction descriptions and amounts. It outputs a training dataset to stdout.
"""

import csv
import os
import re
import sys
from typing import Dict, List, Tuple, Optional
import json


class TransactionCategorizer:
    """Categorizes bank transactions based on description patterns."""
    
    def __init__(self):
        # Define category patterns (regex patterns mapped to categories)
        self.category_patterns = {
            'groceries': [
                r'\b(walmart|target|kroger|safeway|whole foods|trader joe|costco|sam\'s club)\b',
                r'\b(grocery|supermarket|food market|market)\b',
                r'\b(publix|wegmans|harris teeter|food lion)\b'
            ],
            'gas': [
                r'\b(shell|exxon|mobil|bp|chevron|texaco|marathon|sunoco)\b',
                r'\b(gas station|fuel|gasoline)\b',
                r'\b(circle k|wawa|speedway|7-eleven).*fuel\b'
            ],
            'restaurants': [
                r'\b(mcdonald|burger king|kfc|taco bell|subway|pizza hut|domino)\b',
                r'\b(starbucks|dunkin|coffee)\b',
                r'\b(restaurant|cafe|diner|bistro|grill)\b',
                r'\b(chipotle|panera|olive garden|applebee|chili)\b'
            ],
            'utilities': [
                r'\b(electric|electricity|power company|pge|duke energy)\b',
                r'\b(water|sewer|gas bill|utility)\b',
                r'\b(internet|cable|phone|wireless|verizon|at&t|comcast)\b',
                r'\b(trash|garbage|waste management)\b'
            ],
            'shopping': [
                r'\b(amazon|ebay|etsy)\b',
                r'\b(clothing|apparel|fashion)\b',
                r'\b(home depot|lowe\'s|hardware)\b',
                r'\b(best buy|electronics|computer)\b'
            ],
            'entertainment': [
                r'\b(netflix|hulu|spotify|apple music|disney)\b',
                r'\b(movie|theater|cinema|tickets)\b',
                r'\b(game|gaming|steam|xbox|playstation)\b',
                r'\b(concert|show|event)\b'
            ],
            'healthcare': [
                r'\b(pharmacy|cvs|walgreens|rite aid)\b',
                r'\b(doctor|hospital|medical|clinic)\b',
                r'\b(dental|dentist|vision|optometry)\b',
                r'\b(insurance|health)\b'
            ],
            'banking': [
                r'\b(atm|withdrawal|deposit|transfer)\b',
                r'\b(bank|credit union|fee)\b',
                r'\b(interest|dividend|investment)\b'
            ],
            'travel': [
                r'\b(hotel|motel|inn|resort)\b',
                r'\b(airline|airport|flight|uber|lyft|taxi)\b',
                r'\b(rental car|hertz|enterprise|avis)\b',
                r'\b(gas station).*travel\b'
            ]
        }
    
    def categorize_transaction(self, description: str) -> str:
        """Categorize a transaction based on its description."""
        description_lower = description.lower()
        
        for category, patterns in self.category_patterns.items():
            for pattern in patterns:
                if re.search(pattern, description_lower):
                    return category
        
        return 'other'


class BankTransactionProcessor:
    """Processes bank transaction CSV files and generates training data."""
    
    def __init__(self):
        self.categorizer = TransactionCategorizer()
        self.training_data = []
    
    def detect_csv_structure(self, filepath: str) -> Optional[Dict[str, int]]:
        """Detect the structure of a CSV file and find relevant columns."""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                # Read first few lines to detect structure
                sample_lines = [file.readline() for _ in range(3)]
                
            # Try to parse header
            reader = csv.reader(sample_lines)
            header = next(reader)
            
            column_mapping = {}
            
            # Look for description column
            for i, col in enumerate(header):
                col_lower = col.lower()
                if any(keyword in col_lower for keyword in ['description', 'memo', 'detail', 'merchant', 'payee']):
                    column_mapping['description'] = i
                    break
            
            # Look for amount column
            for i, col in enumerate(header):
                col_lower = col.lower()
                if any(keyword in col_lower for keyword in ['amount', 'debit', 'credit', 'transaction']):
                    column_mapping['amount'] = i
                    break
            
            return column_mapping if len(column_mapping) >= 2 else None
            
        except Exception as e:
            print(f"Error detecting CSV structure for {filepath}: {e}", file=sys.stderr)
            return None
    
    def process_csv_file(self, filepath: str) -> List[Tuple[str, float, str]]:
        """Process a single CSV file and extract transactions."""
        transactions = []
        
        try:
            column_mapping = self.detect_csv_structure(filepath)
            if not column_mapping:
                print(f"Could not detect CSV structure for {filepath}", file=sys.stderr)
                return transactions
            
            with open(filepath, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                header = next(reader)  # Skip header
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        if len(row) <= max(column_mapping.values()):
                            continue
                        
                        description = row[column_mapping['description']].strip()
                        amount_str = row[column_mapping['amount']].strip()
                        
                        # Clean and parse amount
                        amount_str = re.sub(r'[,$]', '', amount_str)
                        amount = float(amount_str)
                        
                        # Skip very small amounts (likely fees)
                        if abs(amount) < 0.01:
                            continue
                        
                        # Categorize transaction
                        category = self.categorizer.categorize_transaction(description)
                        
                        transactions.append((description, amount, category))
                        
                    except (ValueError, IndexError) as e:
                        print(f"Error processing row {row_num} in {filepath}: {e}", file=sys.stderr)
                        continue
        
        except Exception as e:
            print(f"Error processing file {filepath}: {e}", file=sys.stderr)
        
        return transactions
    
    def find_csv_files(self, directory: str = '.') -> List[str]:
        """Find all CSV files in the given directory."""
        csv_files = []
        try:
            for filename in os.listdir(directory):
                if filename.lower().endswith('.csv'):
                    csv_files.append(os.path.join(directory, filename))
        except Exception as e:
            print(f"Error finding CSV files: {e}", file=sys.stderr)
        
        return csv_files
    
    def generate_training_dataset(self, directory: str = '.') -> None:
        """Generate training dataset from all CSV files in directory."""
        csv_files = self.find_csv_files(directory)
        
        if not csv_files:
            print("No CSV files found in current directory", file=sys.