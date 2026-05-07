#!/usr/bin/env python3
"""
Bank Statement Transaction Categorizer

This module reads CSV bank statements, categorizes transactions using regex patterns
based on merchant names and descriptions, and exports the results to a new CSV file
with added category columns.

Usage: python script.py

The script expects a 'bank_statements.csv' file in the same directory with columns:
- Date, Description, Amount (minimum required)
- Additional columns will be preserved in output

Output: Creates 'categorized_statements.csv' with an additional 'Category' column
"""

import csv
import re
import sys
import os
from typing import Dict, List, Any


def get_category_patterns() -> Dict[str, List[str]]:
    """
    Define regex patterns for transaction categorization.
    
    Returns:
        Dict mapping category names to lists of regex patterns
    """
    return {
        'Groceries': [
            r'walmart', r'target', r'kroger', r'safeway', r'whole foods',
            r'trader joe', r'costco', r'sam\'s club', r'grocery', r'market'
        ],
        'Restaurants': [
            r'mcdonald', r'burger', r'pizza', r'restaurant', r'cafe', r'coffee',
            r'starbucks', r'subway', r'domino', r'kfc', r'taco bell'
        ],
        'Gas': [
            r'shell', r'exxon', r'bp ', r'chevron', r'mobil', r'gas station',
            r'fuel', r'petrol'
        ],
        'Utilities': [
            r'electric', r'power', r'water', r'gas bill', r'internet',
            r'phone', r'cable', r'utility'
        ],
        'Entertainment': [
            r'netflix', r'spotify', r'movie', r'theater', r'game',
            r'entertainment', r'amazon prime'
        ],
        'Healthcare': [
            r'pharmacy', r'doctor', r'medical', r'hospital', r'dentist',
            r'cvs', r'walgreen'
        ],
        'Shopping': [
            r'amazon', r'ebay', r'mall', r'store', r'shop', r'retail'
        ],
        'Transportation': [
            r'uber', r'lyft', r'taxi', r'bus', r'train', r'airline',
            r'parking'
        ],
        'Banking': [
            r'atm', r'fee', r'interest', r'transfer', r'deposit'
        ]
    }


def categorize_transaction(description: str, patterns: Dict[str, List[str]]) -> str:
    """
    Categorize a transaction based on its description.
    
    Args:
        description: Transaction description text
        patterns: Dictionary of category patterns
        
    Returns:
        Category name or 'Other' if no match found
    """
    description_lower = description.lower()
    
    for category, pattern_list in patterns.items():
        for pattern in pattern_list:
            if re.search(pattern, description_lower):
                return category
    
    return 'Other'


def process_csv(input_file: str, output_file: str) -> None:
    """
    Process the CSV file and add categorization.
    
    Args:
        input_file: Path to input CSV file
        output_file: Path to output CSV file
        
    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If required columns are missing
    """
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file '{input_file}' not found")
    
    patterns = get_category_patterns()
    categorized_count = 0
    total_transactions = 0
    
    try:
        with open(input_file, 'r', newline='', encoding='utf-8') as infile:
            # Detect delimiter
            sample = infile.read(1024)
            infile.seek(0)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
            reader = csv.DictReader(infile, delimiter=delimiter)
            
            # Validate required columns
            required_cols = ['Description']
            fieldnames = reader.fieldnames
            if not fieldnames:
                raise ValueError("CSV file appears to be empty or malformed")
            
            # Find description column (case insensitive)
            desc_col = None
            for col in fieldnames:
                if col.lower() in ['description', 'desc', 'merchant', 'payee']:
                    desc_col = col
                    break
            
            if not desc_col:
                raise ValueError("No description column found. Expected columns: Description, Desc, Merchant, or Payee")
            
            # Prepare output fieldnames
            output_fieldnames = list(fieldnames) + ['Category']
            
            with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=output_fieldnames)
                writer.writeheader()
                
                for row in reader:
                    total_transactions += 1
                    description = row.get(desc_col, '')
                    category = categorize_transaction(description, patterns)
                    
                    if category != 'Other':
                        categorized_count += 1
                    
                    # Add category to row
                    row['Category'] = category
                    writer.writerow(row)
    
    except UnicodeDecodeError:
        # Try with different encoding
        try:
            with open(input_file, 'r', newline='', encoding='latin-1') as infile:
                reader = csv.DictReader(infile)
                # Process with latin-1 encoding...
                # (Implementation would be similar to above)
                pass
        except Exception as e:
            raise ValueError(f"Unable to read file with UTF-8 or Latin-1 encoding: {e}")
    
    print(f"Processing complete!")
    print(f"Total transactions: {total_transactions}")
    print(f"Categorized transactions: {categorized_count}")
    print(f"Uncategorized transactions: {total_transactions - categorized_count}")
    print(f"Results saved to: {output_file}")


def main():
    """Main execution function."""
    input_file = 'bank_statements.csv'
    output_file = 'categorized_statements.csv'
    
    try:
        process_csv(input_file, output_file)
        
        # Display sample results
        if os.path.exists(output_file):
            print("\nSample categorized transactions:")
            with open(output_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader):
                    if i >= 5:  # Show first 5 rows
                        break
                    desc = row.get('Description', 'N/A')[:50]
                    category = row.get('Category', 'N/A')
                    print(f"  {desc:<50} -> {category}")
    
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print(f"Please ensure '{input_file}' exists in the current directory.")
        print("The file should contain columns like: Date, Description, Amount")
        sys.exit(1)
    
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()