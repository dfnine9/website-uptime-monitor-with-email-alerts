```python
"""
Bank Transaction Parser and Categorizer

A self-contained Python script that processes bank CSV files to clean transaction data
and categorize expenses using keyword-based mapping. Handles various date formats,
removes special characters from amounts, and standardizes transaction data for analysis.

Features:
- Parses CSV files with flexible column detection
- Cleans and standardizes date formats (MM/DD/YYYY, YYYY-MM-DD, DD/MM/YYYY)
- Removes special characters from amount fields and converts to float
- Categorizes transactions using keyword matching for common expense types
- Provides detailed output with original and cleaned data comparison

Usage: python script.py
"""

import csv
import re
import sys
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import io

class BankTransactionParser:
    def __init__(self):
        self.category_keywords = {
            'groceries': ['grocery', 'supermarket', 'walmart', 'target', 'kroger', 'safeway', 
                         'whole foods', 'trader joe', 'costco', 'sam\'s club', 'food lion',
                         'publix', 'wegmans', 'aldi', 'fresh market'],
            'gas': ['shell', 'exxon', 'bp', 'chevron', 'mobil', 'gas station', 'fuel',
                   'marathon', 'citgo', 'valero', 'sunoco', 'speedway'],
            'restaurants': ['restaurant', 'cafe', 'pizza', 'subway', 'mcdonald', 'burger',
                           'starbucks', 'dunkin', 'taco bell', 'kfc', 'wendy', 'chick-fil-a',
                           'domino', 'chipotle', 'panera', 'dining', 'food delivery'],
            'utilities': ['electric', 'gas bill', 'water', 'internet', 'phone', 'cable',
                         'verizon', 'at&t', 'comcast', 'spectrum', 'utility', 'power company'],
            'entertainment': ['movie', 'theater', 'netflix', 'spotify', 'amazon prime',
                             'disney', 'hulu', 'youtube', 'gaming', 'concert', 'tickets'],
            'shopping': ['amazon', 'ebay', 'online', 'department store', 'mall', 'retail',
                        'clothing', 'shoes', 'electronics', 'home depot', 'lowes'],
            'healthcare': ['doctor', 'hospital', 'pharmacy', 'medical', 'dental', 'vision',
                          'cvs', 'walgreens', 'rite aid', 'clinic', 'health'],
            'transportation': ['uber', 'lyft', 'taxi', 'bus', 'train', 'subway', 'parking',
                              'toll', 'car payment', 'insurance'],
            'banking': ['bank', 'atm', 'fee', 'interest', 'transfer', 'deposit', 'withdrawal',
                       'overdraft', 'maintenance'],
            'miscellaneous': []
        }
    
    def clean_amount(self, amount_str: str) -> float:
        """Clean amount string and convert to float"""
        try:
            # Remove currency symbols, commas, and extra spaces
            cleaned = re.sub(r'[$,\s]', '', str(amount_str))
            # Handle parentheses for negative amounts
            if '(' in cleaned and ')' in cleaned:
                cleaned = '-' + cleaned.replace('(', '').replace(')', '')
            return float(cleaned)
        except (ValueError, TypeError):
            return 0.0
    
    def parse_date(self, date_str: str) -> Optional[str]:
        """Parse various date formats and return standardized YYYY-MM-DD format"""
        if not date_str:
            return None
            
        date_formats = [
            '%m/%d/%Y', '%m/%d/%y',  # MM/DD/YYYY, MM/DD/YY
            '%Y-%m-%d',              # YYYY-MM-DD
            '%d/%m/%Y', '%d/%m/%y',  # DD/MM/YYYY, DD/MM/YY
            '%m-%d-%Y', '%m-%d-%y',  # MM-DD-YYYY, MM-DD-YY
            '%Y/%m/%d',              # YYYY/MM/DD
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(str(date_str).strip(), fmt)
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        return None
    
    def categorize_transaction(self, description: str) -> str:
        """Categorize transaction based on description keywords"""
        description_lower = description.lower()
        
        for category, keywords in self.category_keywords.items():
            if category == 'miscellaneous':
                continue
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'miscellaneous'
    
    def detect_csv_structure(self, csv_content: str) -> Dict[str, int]:
        """Detect CSV column structure"""
        lines = csv_content.strip().split('\n')
        if not lines:
            raise ValueError("Empty CSV content")
        
        header = lines[0].lower()
        columns = [col.strip().strip('"') for col in header.split(',')]
        
        column_mapping = {}
        
        # Common column name patterns
        date_patterns = ['date', 'transaction date', 'posted date']
        description_patterns = ['description', 'memo', 'details', 'transaction']
        amount_patterns = ['amount', 'debit', 'credit', 'transaction amount']
        
        for i, col in enumerate(columns):
            if any(pattern in col for pattern in date_patterns):
                column_mapping['date'] = i
            elif any(pattern in col for pattern in description_patterns):
                column_mapping['description'] = i
            elif any(pattern in col for pattern in amount_patterns):
                column_mapping['amount'] = i
        
        return column_mapping
    
    def process_csv_content(self, csv_content: str) -> List[Dict]:
        """Process CSV content and return cleaned transactions"""
        try:
            column_mapping = self.detect_csv_structure(csv_content)
            
            if not all(key in column_mapping for key in ['date', 'description', 'amount']):
                raise ValueError("Required columns (date, description, amount) not found")
            
            transactions = []
            csv_reader = csv.reader(io.StringIO(csv_content))
            
            # Skip header
            next(csv_reader)
            
            for row_num, row in enumerate(csv_reader, start=2):
                if len(row) <= max(column_mapping.values()):
                    continue
                
                try:
                    original_date = row[column_mapping['date']]
                    original_description = row[column_mapping['description']]
                    original_amount = row[column_mapping['amount']]
                    
                    cleaned_date = self.parse_date(original_date)
                    cleaned_description = original_description.strip()
                    cleaned_amount = self.clean_amount(original_amount)
                    category = self.categorize_transaction(cleaned_description)
                    
                    transaction = {
                        'row_number': row_num,
                        'original_date': original_date,
                        'cleaned_date': cleaned_date,
                        'original_description': original_description,
                        'cleaned_description': cleaned_description,
                        'original_amount': original_amount,
                        'cleaned_amount': cleaned_amount,
                        'category': category
                    }
                    
                    transactions.append(transaction)
                    
                except Exception as e:
                    print(f"Warning: Error processing row {row_num}: {e}")
                    continue
            
            return transactions
            
        except Exception as e:
            raise ValueError(f"Error processing CSV: {e}")

def create_sample_csv() -> str:
    """Create sample CSV