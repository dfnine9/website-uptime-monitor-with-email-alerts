```python
#!/usr/bin/env python3
"""
Financial Transaction Categorization CLI

A command-line tool that processes CSV files containing financial transactions,
categorizes them using pattern matching, and generates visual reports with
summary statistics.

Features:
- Automatic transaction categorization based on description patterns
- Visual pie chart generation for category distribution
- Summary statistics output
- Configurable input/output directories
- Error handling for file operations and data processing

Usage:
    python script.py [csv_file_path] [--output-dir OUTPUT_DIR]

Requirements:
    - CSV file with columns: date, description, amount
    - Python 3.6+ with standard library
"""

import argparse
import csv
import json
import os
import sys
from collections import defaultdict, Counter
from datetime import datetime
from pathlib import Path
import re


class TransactionCategorizer:
    """Categorizes financial transactions based on description patterns."""
    
    def __init__(self):
        self.category_patterns = {
            'Food & Dining': [
                r'restaurant', r'cafe', r'pizza', r'burger', r'starbucks',
                r'mcdonalds', r'subway', r'food', r'dining', r'grocery'
            ],
            'Transportation': [
                r'gas', r'fuel', r'uber', r'lyft', r'taxi', r'parking',
                r'metro', r'bus', r'train', r'airline', r'flight'
            ],
            'Shopping': [
                r'amazon', r'walmart', r'target', r'mall', r'store',
                r'shop', r'retail', r'purchase', r'buy'
            ],
            'Bills & Utilities': [
                r'electric', r'water', r'gas bill', r'phone', r'internet',
                r'cable', r'insurance', r'mortgage', r'rent'
            ],
            'Healthcare': [
                r'medical', r'doctor', r'hospital', r'pharmacy', r'dental',
                r'health', r'clinic', r'prescription'
            ],
            'Entertainment': [
                r'movie', r'theater', r'netflix', r'spotify', r'game',
                r'entertainment', r'concert', r'show'
            ],
            'ATM & Banking': [
                r'atm', r'bank', r'withdrawal', r'deposit', r'transfer',
                r'fee', r'charge'
            ]
        }
    
    def categorize(self, description):
        """Categorize a transaction based on its description."""
        description_lower = description.lower()
        
        for category, patterns in self.category_patterns.items():
            for pattern in patterns:
                if re.search(pattern, description_lower):
                    return category
        
        return 'Other'


class ReportGenerator:
    """Generates visual reports and summary statistics."""
    
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_pie_chart_data(self, category_totals):
        """Generate data structure for pie chart visualization."""
        total = sum(abs(amount) for amount in category_totals.values())
        
        chart_data = {
            'labels': list(category_totals.keys()),
            'values': [abs(amount) for amount in category_totals.values()],
            'percentages': [
                round((abs(amount) / total) * 100, 1) if total > 0 else 0
                for amount in category_totals.values()
            ]
        }
        
        # Save chart data as JSON for potential visualization
        chart_file = self.output_dir / 'category_chart_data.json'
        with open(chart_file, 'w') as f:
            json.dump(chart_data, f, indent=2)
        
        return chart_data
    
    def generate_summary_stats(self, transactions, category_totals):
        """Generate comprehensive summary statistics."""
        amounts = [float(t['amount']) for t in transactions]
        
        stats = {
            'total_transactions': len(transactions),
            'total_amount': sum(amounts),
            'average_transaction': sum(amounts) / len(amounts) if amounts else 0,
            'largest_expense': min(amounts) if amounts else 0,
            'largest_income': max(amounts) if amounts else 0,
            'category_breakdown': {
                category: {
                    'total': total,
                    'percentage': round((abs(total) / sum(abs(v) for v in category_totals.values())) * 100, 1)
                    if sum(abs(v) for v in category_totals.values()) > 0 else 0
                }
                for category, total in category_totals.items()
            },
            'date_range': self._get_date_range(transactions)
        }
        
        # Save summary stats
        stats_file = self.output_dir / 'summary_statistics.json'
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
        
        return stats
    
    def _get_date_range(self, transactions):
        """Extract date range from transactions."""
        try:
            dates = [datetime.strptime(t['date'], '%Y-%m-%d') for t in transactions]
            return {
                'start_date': min(dates).strftime('%Y-%m-%d'),
                'end_date': max(dates).strftime('%Y-%m-%d')
            }
        except (ValueError, KeyError):
            return {'start_date': 'Unknown', 'end_date': 'Unknown'}


def load_csv_data(file_path):
    """Load and validate CSV transaction data."""
    transactions = []
    
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
            # Detect delimiter
            sample = csvfile.read(1024)
            csvfile.seek(0)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
            reader = csv.DictReader(csvfile, delimiter=delimiter)
            
            # Normalize column names
            fieldnames = [field.lower().strip() for field in reader.fieldnames]
            
            for row in reader:
                # Normalize keys
                normalized_row = {k.lower().strip(): v.strip() for k, v in row.items()}
                
                # Validate required fields
                if not all(field in normalized_row for field in ['date', 'description', 'amount']):
                    raise ValueError("CSV must contain 'date', 'description', and 'amount' columns")
                
                # Validate and convert amount
                try:
                    amount = float(normalized_row['amount'])
                except ValueError:
                    raise ValueError(f"Invalid amount value: {normalized_row['amount']}")
                
                transactions.append({
                    'date': normalized_row['date'],
                    'description': normalized_row['description'],
                    'amount': amount
                })
    
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file not found: {file_path}")
    except Exception as e:
        raise Exception(f"Error reading CSV file: {str(e)}")
    
    if not transactions:
        raise ValueError("No valid transactions found in CSV file")
    
    return transactions


def process_transactions(transactions):
    """Process transactions through categorization pipeline."""
    categorizer = TransactionCategorizer()
    category_totals = defaultdict(float)
    
    for transaction in transactions:
        category = categorizer.categorize(transaction['description'])
        transaction['category'] = category
        category_totals[category] += transaction['amount']
    
    return transactions, dict(category_totals)


def print_console_report(stats, chart_data):
    """Print formatted report to console."""
    print("\n" + "="*60)
    print("TRANSACTION CATEGORIZATION REPORT")
    print("="*60)
    
    print(f"\nSUMMARY STATISTICS:")
    print(f"  Total Transactions: {stats['total_transactions']:,}")
    print