```python
#!/usr/bin/env python3
"""
Bank CSV Transaction Categorizer

This module parses bank CSV exports and categorizes transactions based on keyword matching.
It reads transaction data, applies predefined categorization rules, and outputs the results
to a new CSV file with category assignments.

Features:
- Flexible CSV parsing with automatic delimiter detection
- Keyword-based transaction categorization
- Error handling for file operations and data processing
- Summary statistics output
- Self-contained with minimal dependencies

Usage:
    python script.py
    
The script will prompt for input CSV file path and create an output file with categorized transactions.
"""

import csv
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any

def detect_csv_dialect(file_path: str, sample_size: int = 1024) -> csv.Dialect:
    """Detect CSV dialect (delimiter, quoting) from file sample."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            sample = f.read(sample_size)
            sniffer = csv.Sniffer()
            return sniffer.sniff(sample)
    except Exception:
        # Fallback to comma-separated
        class DefaultDialect(csv.excel):
            delimiter = ','
        return DefaultDialect()

def get_categorization_rules() -> Dict[str, List[str]]:
    """Return keyword-based categorization rules."""
    return {
        'Food': [
            'restaurant', 'cafe', 'pizza', 'burger', 'coffee', 'starbucks', 'mcdonalds',
            'subway', 'grocery', 'supermarket', 'food', 'dining', 'lunch', 'dinner',
            'takeaway', 'delivery', 'uber eats', 'doordash', 'grubhub'
        ],
        'Transport': [
            'gas', 'fuel', 'uber', 'lyft', 'taxi', 'bus', 'train', 'metro', 'parking',
            'toll', 'car wash', 'auto', 'vehicle', 'transport', 'airline', 'flight',
            'rental car', 'bike share'
        ],
        'Utilities': [
            'electric', 'electricity', 'water', 'gas bill', 'internet', 'phone',
            'mobile', 'cable', 'utility', 'power', 'heating', 'cooling', 'sewage',
            'trash', 'recycling'
        ],
        'Entertainment': [
            'movie', 'cinema', 'netflix', 'spotify', 'gaming', 'concert', 'theater',
            'entertainment', 'streaming', 'youtube', 'hulu', 'disney', 'amazon prime',
            'music', 'books', 'magazine'
        ],
        'Shopping': [
            'amazon', 'walmart', 'target', 'store', 'shop', 'retail', 'clothing',
            'shoes', 'electronics', 'home depot', 'costco', 'mall', 'online'
        ],
        'Healthcare': [
            'hospital', 'doctor', 'pharmacy', 'medical', 'dental', 'health',
            'insurance', 'prescription', 'clinic', 'cvs', 'walgreens'
        ],
        'Banking': [
            'atm', 'fee', 'transfer', 'withdrawal', 'deposit', 'interest',
            'overdraft', 'maintenance', 'service charge'
        ],
        'Income': [
            'salary', 'payroll', 'wages', 'bonus', 'refund', 'dividend',
            'interest income', 'cashback', 'rebate'
        ]
    }

def categorize_transaction(description: str, amount: float, rules: Dict[str, List[str]]) -> str:
    """Categorize a transaction based on description and amount."""
    description_lower = description.lower()
    
    # Check for income (positive amounts or specific keywords)
    if amount > 0:
        income_keywords = rules.get('Income', [])
        if any(keyword in description_lower for keyword in income_keywords):
            return 'Income'
    
    # Check each category
    for category, keywords in rules.items():
        if category == 'Income':  # Already handled above
            continue
        if any(keyword in description_lower for keyword in keywords):
            return category
    
    return 'Other'

def parse_amount(amount_str: str) -> float:
    """Parse amount string to float, handling various formats."""
    try:
        # Remove currency symbols, commas, and extra whitespace
        cleaned = re.sub(r'[^\d.-]', '', str(amount_str))
        return float(cleaned) if cleaned else 0.0
    except (ValueError, TypeError):
        return 0.0

def process_csv_file(input_path: str, output_path: str) -> Tuple[int, Dict[str, int]]:
    """Process CSV file and categorize transactions."""
    rules = get_categorization_rules()
    category_counts = {}
    processed_count = 0
    
    try:
        # Detect CSV format
        dialect = detect_csv_dialect(input_path)
        
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile, dialect=dialect)
            
            # Try to identify common column names
            fieldnames = reader.fieldnames
            if not fieldnames:
                raise ValueError("No column headers found in CSV file")
            
            # Map common column variations
            description_col = None
            amount_col = None
            date_col = None
            
            for field in fieldnames:
                field_lower = field.lower()
                if any(term in field_lower for term in ['description', 'memo', 'details', 'transaction']):
                    description_col = field
                elif any(term in field_lower for term in ['amount', 'value', 'sum']):
                    amount_col = field
                elif any(term in field_lower for term in ['date', 'time']):
                    date_col = field
            
            if not description_col or not amount_col:
                print(f"Available columns: {', '.join(fieldnames)}")
                description_col = input(f"Enter description column name (or press Enter for '{fieldnames[0]}'): ").strip()
                if not description_col:
                    description_col = fieldnames[0]
                
                amount_col = input(f"Enter amount column name (or press Enter for '{fieldnames[1] if len(fieldnames) > 1 else fieldnames[0]}'): ").strip()
                if not amount_col:
                    amount_col = fieldnames[1] if len(fieldnames) > 1 else fieldnames[0]
            
            # Prepare output
            output_fieldnames = list(fieldnames) + ['Category']
            
            with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=output_fieldnames)
                writer.writeheader()
                
                for row in reader:
                    try:
                        description = row.get(description_col, '')
                        amount = parse_amount(row.get(amount_col, '0'))
                        
                        category = categorize_transaction(description, amount, rules)
                        category_counts[category] = category_counts.get(category, 0) + 1
                        
                        # Add category to row
                        row['Category'] = category
                        writer.writerow(row)
                        processed_count += 1
                        
                    except Exception as e:
                        print(f"Warning: Error processing row {processed_count + 1}: {e}")
                        continue
        
        return processed_count, category_counts
        
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_path}")
    except PermissionError:
        raise PermissionError(f"Permission denied accessing files")
    except Exception as e:
        raise Exception(f"Error processing CSV: {e}")

def main():
    """Main function to run the transaction categorizer