```python
#!/usr/bin/env python3
"""
Transaction Categorizer and Analyzer

This module reads CSV files containing financial transactions, categorizes them using
keyword matching, and calculates total spending by category. It processes transaction
data with columns for date, description, and amount, applying predefined category
rules to classify each transaction.

Features:
- CSV file parsing with flexible column detection
- Keyword-based transaction categorization
- Spending analysis and reporting
- Error handling for file operations and data processing
- Self-contained operation using only standard library

Usage:
    python script.py

The script looks for CSV files in the current directory with transaction data.
Expected CSV format: Date, Description, Amount (headers flexible)
"""

import csv
import os
import sys
from typing import Dict, List, Tuple, Optional
import re


class TransactionCategorizer:
    """Categorizes financial transactions based on keyword matching."""
    
    def __init__(self):
        """Initialize categorizer with predefined category keywords."""
        self.categories = {
            'Groceries': [
                'grocery', 'supermarket', 'walmart', 'target', 'kroger', 
                'safeway', 'whole foods', 'trader joe', 'costco', 'food'
            ],
            'Restaurants': [
                'restaurant', 'cafe', 'coffee', 'starbucks', 'mcdonald',
                'burger', 'pizza', 'dining', 'bar', 'pub', 'bistro'
            ],
            'Gas & Transportation': [
                'gas', 'fuel', 'exxon', 'shell', 'bp', 'chevron', 'uber',
                'lyft', 'taxi', 'metro', 'bus', 'train', 'parking'
            ],
            'Shopping': [
                'amazon', 'ebay', 'mall', 'store', 'shop', 'retail',
                'clothing', 'best buy', 'home depot', 'lowes'
            ],
            'Bills & Utilities': [
                'electric', 'gas bill', 'water', 'internet', 'phone',
                'cable', 'insurance', 'mortgage', 'rent', 'utility'
            ],
            'Healthcare': [
                'pharmacy', 'doctor', 'hospital', 'medical', 'dental',
                'vision', 'clinic', 'cvs', 'walgreens', 'health'
            ],
            'Entertainment': [
                'movie', 'theater', 'netflix', 'spotify', 'game',
                'entertainment', 'concert', 'music', 'streaming'
            ],
            'Other': []  # Default category
        }
    
    def categorize_transaction(self, description: str) -> str:
        """
        Categorize a transaction based on its description.
        
        Args:
            description: Transaction description string
            
        Returns:
            Category name as string
        """
        if not description:
            return 'Other'
        
        description_lower = description.lower()
        
        for category, keywords in self.categories.items():
            if category == 'Other':
                continue
            
            for keyword in keywords:
                if keyword.lower() in description_lower:
                    return category
        
        return 'Other'


class TransactionAnalyzer:
    """Analyzes transaction data and generates spending reports."""
    
    def __init__(self):
        """Initialize analyzer with categorizer."""
        self.categorizer = TransactionCategorizer()
        self.transactions = []
        self.category_totals = {}
    
    def read_csv_file(self, filepath: str) -> bool:
        """
        Read and parse CSV transaction file.
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filepath, 'r', newline='', encoding='utf-8') as file:
                # Detect delimiter
                sample = file.read(1024)
                file.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(file, delimiter=delimiter)
                
                # Flexible column name matching
                headers = reader.fieldnames
                if not headers:
                    print(f"Error: No headers found in {filepath}")
                    return False
                
                date_col = self._find_column(headers, ['date', 'transaction_date', 'dt'])
                desc_col = self._find_column(headers, ['description', 'desc', 'memo', 'transaction'])
                amount_col = self._find_column(headers, ['amount', 'value', 'total', 'cost', 'price'])
                
                if not all([date_col, desc_col, amount_col]):
                    print(f"Error: Required columns not found in {filepath}")
                    print(f"Available columns: {headers}")
                    return False
                
                transactions_count = 0
                for row in reader:
                    try:
                        amount_str = str(row[amount_col]).strip()
                        # Clean amount string (remove currency symbols, commas)
                        amount_cleaned = re.sub(r'[$,\s]', '', amount_str)
                        # Handle negative amounts in parentheses
                        if amount_cleaned.startswith('(') and amount_cleaned.endswith(')'):
                            amount_cleaned = '-' + amount_cleaned[1:-1]
                        
                        amount = float(amount_cleaned)
                        description = str(row[desc_col]).strip()
                        date = str(row[date_col]).strip()
                        
                        category = self.categorizer.categorize_transaction(description)
                        
                        self.transactions.append({
                            'date': date,
                            'description': description,
                            'amount': amount,
                            'category': category
                        })
                        
                        transactions_count += 1
                        
                    except (ValueError, KeyError) as e:
                        print(f"Warning: Skipping invalid row in {filepath}: {e}")
                        continue
                
                print(f"Successfully loaded {transactions_count} transactions from {filepath}")
                return True
                
        except FileNotFoundError:
            print(f"Error: File {filepath} not found")
            return False
        except PermissionError:
            print(f"Error: Permission denied accessing {filepath}")
            return False
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return False
    
    def _find_column(self, headers: List[str], possible_names: List[str]) -> Optional[str]:
        """Find column name from possible variations."""
        headers_lower = [h.lower() for h in headers]
        for name in possible_names:
            for i, header in enumerate(headers_lower):
                if name in header:
                    return headers[i]
        return None
    
    def calculate_category_totals(self) -> Dict[str, float]:
        """
        Calculate total spending by category.
        
        Returns:
            Dictionary mapping category names to total amounts
        """
        self.category_totals = {}
        
        for transaction in self.transactions:
            category = transaction['category']
            amount = abs(transaction['amount'])  # Use absolute value for spending analysis
            
            if category in self.category_totals:
                self.category_totals[category] += amount
            else:
                self.category_totals[category] = amount
        
        return self.category_totals
    
    def print_analysis_report(self):
        """Print comprehensive analysis report to stdout."""
        if not self.transactions:
            print("No transactions to analyze.")
            return
        
        print("\n" + "="*60)
        print("TRANSACTION ANALYSIS REPORT")
        print("="*60)
        
        # Summary statistics
        total_transactions = len(self.transactions)
        total_spending = sum(abs(t['amount']) for t in self.transactions)
        
        print(f"\nSummary:")
        print(f"  Total Transactions: {total_transactions:,}")
        print(f"  Total Spending: ${total_spending:,.2f}")
        
        # Category breakdown
        category_totals