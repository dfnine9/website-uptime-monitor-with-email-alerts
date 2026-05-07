```python
#!/usr/bin/env python3
"""
Bank Statement Transaction Categorizer

This module reads CSV bank statement files and categorizes transactions based on
merchant names and descriptions using regex patterns. It supports common categories
like groceries, restaurants, gas stations, utilities, and more.

The script processes CSV files with columns for transaction descriptions/merchants
and assigns appropriate categories based on predefined regex patterns.

Usage: python script.py
"""

import csv
import re
import sys
from typing import Dict, List, Tuple, Optional
from pathlib import Path


class TransactionCategorizer:
    """Categorizes bank transactions based on merchant names and descriptions."""
    
    def __init__(self):
        """Initialize the categorizer with predefined regex patterns."""
        self.category_patterns = {
            'Groceries': [
                r'\b(walmart|target|kroger|safeway|publix|whole foods|trader joe|costco|sam\'s club)\b',
                r'\b(grocery|market|supermarket|food mart|fresh market)\b',
                r'\b(aldi|wegmans|giant eagle|harris teeter|food lion|piggly wiggly)\b',
                r'\b(king soopers|smith\'s|ralphs|vons|albertsons)\b'
            ],
            'Restaurants': [
                r'\b(mcdonald|burger king|subway|starbucks|dunkin|kfc|taco bell|pizza hut)\b',
                r'\b(domino|papa john|chipotle|panera|chick-fil-a|wendy|arby)\b',
                r'\b(restaurant|cafe|diner|bistro|grill|bar & grill|eatery)\b',
                r'\b(food truck|fast food|takeout|delivery)\b'
            ],
            'Gas Stations': [
                r'\b(shell|exxon|bp|chevron|texaco|mobil|sunoco|speedway)\b',
                r'\b(wawa|sheetz|7-eleven|circle k|quick trip|casey\'s)\b',
                r'\b(gas station|fuel|petroleum|truck stop)\b',
                r'\b(pilot|flying j|love\'s|ta travel)\b'
            ],
            'Utilities': [
                r'\b(electric|electricity|power|energy|utility)\b',
                r'\b(gas company|water|sewer|trash|garbage|waste)\b',
                r'\b(internet|cable|phone|telecom|verizon|at&t|comcast)\b',
                r'\b(duke energy|pge|con edison|national grid)\b'
            ],
            'Banking/Finance': [
                r'\b(bank|atm|fee|interest|transfer|deposit)\b',
                r'\b(credit card|loan|mortgage|insurance)\b',
                r'\b(wells fargo|chase|bank of america|citibank|usaa)\b',
                r'\b(paypal|venmo|zelle|cash app)\b'
            ],
            'Shopping/Retail': [
                r'\b(amazon|ebay|best buy|home depot|lowes|kohls)\b',
                r'\b(macy|nordstrom|tj maxx|marshall|ross|old navy)\b',
                r'\b(store|retail|shop|mall|outlet|department)\b',
                r'\b(cvs|walgreens|rite aid|pharmacy)\b'
            ],
            'Healthcare': [
                r'\b(doctor|medical|hospital|clinic|pharmacy|dentist)\b',
                r'\b(urgent care|emergency|health|wellness)\b',
                r'\b(cvs pharmacy|walgreens pharmacy|rite aid)\b',
                r'\b(lab|radiology|imaging|therapy)\b'
            ],
            'Transportation': [
                r'\b(uber|lyft|taxi|cab|bus|train|metro|subway)\b',
                r'\b(parking|toll|bridge|airport|airline)\b',
                r'\b(car rental|hertz|enterprise|avis|budget)\b',
                r'\b(auto|automotive|mechanic|repair|tire)\b'
            ],
            'Entertainment': [
                r'\b(netflix|hulu|disney|spotify|apple music|amazon prime)\b',
                r'\b(movie|theater|cinema|concert|show|event)\b',
                r'\b(gym|fitness|sports|recreation|park)\b',
                r'\b(game|gaming|entertainment|hobby)\b'
            ],
            'Other': []  # Fallback category
        }
        
        # Compile regex patterns for better performance
        self.compiled_patterns = {}
        for category, patterns in self.category_patterns.items():
            self.compiled_patterns[category] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]
    
    def categorize_transaction(self, description: str) -> str:
        """
        Categorize a transaction based on its description.
        
        Args:
            description: Transaction description or merchant name
            
        Returns:
            Category name as string
        """
        if not description:
            return 'Other'
        
        description = description.strip().lower()
        
        # Check each category's patterns
        for category, patterns in self.compiled_patterns.items():
            if category == 'Other':
                continue
            
            for pattern in patterns:
                if pattern.search(description):
                    return category
        
        return 'Other'
    
    def process_csv_file(self, file_path: str) -> List[Dict]:
        """
        Process a CSV file and categorize all transactions.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            List of dictionaries with transaction data and categories
        """
        results = []
        
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                # Try to detect the CSV format
                sample = csvfile.read(1024)
                csvfile.seek(0)
                
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                
                # Common column names for transaction descriptions
                description_columns = [
                    'description', 'merchant', 'payee', 'transaction_description',
                    'desc', 'merchant_name', 'transaction_type', 'details'
                ]
                
                # Find the description column
                desc_column = None
                for col in reader.fieldnames:
                    if col.lower() in description_columns:
                        desc_column = col
                        break
                
                if not desc_column:
                    # Use first column if no standard description column found
                    desc_column = reader.fieldnames[0] if reader.fieldnames else None
                
                if not desc_column:
                    raise ValueError("Could not identify description column in CSV")
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        description = row.get(desc_column, '')
                        category = self.categorize_transaction(description)
                        
                        result = {
                            'row_number': row_num,
                            'description': description,
                            'category': category,
                            'original_data': row
                        }
                        results.append(result)
                        
                    except Exception as e:
                        print(f"Warning: Error processing row {row_num}: {e}", file=sys.stderr)
                        continue
                        
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file not found: {file_path}")
        except csv.Error as e:
            raise csv.Error(f"Error reading CSV file: {e}")
        except Exception as e:
            raise Exception(f"Unexpected error processing file: {e}")
        
        return results
    
    def generate_summary(self, results: List[Dict]) -> Dict[str, int]:
        """
        Generate a summary of categorized transactions.
        
        Args:
            results: List of categorized transactions
            
        Returns:
            Dictionary with category counts
        """
        summary = {}
        for result in results:
            category = result['category']
            summary[category