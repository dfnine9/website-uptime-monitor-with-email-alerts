```python
"""
Financial Transaction Categorizer and Visualizer

A self-contained command-line tool that processes CSV transaction files,
categorizes transactions using AI, and generates visualizations.

Usage: python script.py input.csv output_directory

Features:
- Automatic transaction categorization using Claude AI
- Data visualization with charts
- Error handling and validation
- Self-contained with minimal dependencies
"""

import csv
import json
import os
import sys
import argparse
from datetime import datetime
from collections import defaultdict, Counter
import httpx
import anthropic


class TransactionCategorizer:
    """Categorizes financial transactions using Claude AI"""
    
    def __init__(self, api_key=None):
        self.client = anthropic.Anthropic(api_key=api_key or os.getenv('ANTHROPIC_API_KEY'))
        self.categories = [
            'Food & Dining', 'Shopping', 'Transportation', 'Bills & Utilities',
            'Healthcare', 'Entertainment', 'Travel', 'Income', 'Transfer',
            'Investment', 'Other'
        ]
    
    def categorize_transaction(self, description, amount):
        """Categorize a single transaction"""
        try:
            prompt = f"""
            Categorize this financial transaction into one of these categories:
            {', '.join(self.categories)}
            
            Transaction: {description}
            Amount: ${amount}
            
            Return only the category name, nothing else.
            """
            
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=20,
                messages=[{"role": "user", "content": prompt}]
            )
            
            category = response.content[0].text.strip()
            return category if category in self.categories else 'Other'
            
        except Exception as e:
            print(f"Error categorizing transaction: {e}")
            return 'Other'


class TransactionVisualizer:
    """Creates visualizations from transaction data"""
    
    def __init__(self):
        self.chart_symbols = {
            'bar': '█',
            'partial': ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']
        }
    
    def create_category_chart(self, categories, output_path):
        """Create ASCII bar chart for categories"""
        try:
            category_totals = Counter(categories)
            max_count = max(category_totals.values()) if category_totals else 1
            
            chart_lines = []
            chart_lines.append("Transaction Categories Distribution")
            chart_lines.append("=" * 40)
            
            for category, count in category_totals.most_common():
                bar_length = int((count / max_count) * 30)
                bar = '█' * bar_length
                chart_lines.append(f"{category:<20} {bar} ({count})")
            
            chart_content = '\n'.join(chart_lines)
            
            with open(output_path, 'w') as f:
                f.write(chart_content)
                
            return chart_content
            
        except Exception as e:
            print(f"Error creating category chart: {e}")
            return None
    
    def create_monthly_chart(self, transactions, output_path):
        """Create ASCII chart for monthly spending"""
        try:
            monthly_totals = defaultdict(float)
            
            for transaction in transactions:
                try:
                    date = datetime.strptime(transaction['date'], '%Y-%m-%d')
                    month_key = date.strftime('%Y-%m')
                    amount = abs(float(transaction['amount']))
                    monthly_totals[month_key] += amount
                except (ValueError, KeyError):
                    continue
            
            if not monthly_totals:
                return None
            
            max_amount = max(monthly_totals.values())
            
            chart_lines = []
            chart_lines.append("Monthly Spending Trends")
            chart_lines.append("=" * 40)
            
            for month in sorted(monthly_totals.keys()):
                amount = monthly_totals[month]
                bar_length = int((amount / max_amount) * 30)
                bar = '█' * bar_length
                chart_lines.append(f"{month:<10} {bar} ${amount:,.2f}")
            
            chart_content = '\n'.join(chart_lines)
            
            with open(output_path, 'w') as f:
                f.write(chart_content)
                
            return chart_content
            
        except Exception as e:
            print(f"Error creating monthly chart: {e}")
            return None


class TransactionProcessor:
    """Main processor for transaction files"""
    
    def __init__(self, api_key=None):
        self.categorizer = TransactionCategorizer(api_key)
        self.visualizer = TransactionVisualizer()
    
    def read_csv(self, file_path):
        """Read and validate CSV file"""
        transactions = []
        
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                # Try to detect delimiter
                sample = csvfile.read(1024)
                csvfile.seek(0)
                
                delimiter = ',' if sample.count(',') > sample.count(';') else ';'
                
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                
                for row_num, row in enumerate(reader, 1):
                    # Normalize column names
                    normalized_row = {}
                    for key, value in row.items():
                        key_lower = key.lower().strip()
                        if 'date' in key_lower:
                            normalized_row['date'] = value.strip()
                        elif 'description' in key_lower or 'desc' in key_lower:
                            normalized_row['description'] = value.strip()
                        elif 'amount' in key_lower:
                            normalized_row['amount'] = value.strip()
                        else:
                            normalized_row[key] = value.strip()
                    
                    # Validate required fields
                    if not all(k in normalized_row for k in ['date', 'description', 'amount']):
                        print(f"Warning: Row {row_num} missing required fields, skipping")
                        continue
                    
                    transactions.append(normalized_row)
            
            return transactions
            
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found")
            return None
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return None
    
    def process_transactions(self, transactions):
        """Process and categorize transactions"""
        categorized_transactions = []
        categories = []
        
        print(f"Processing {len(transactions)} transactions...")
        
        for i, transaction in enumerate(transactions, 1):
            try:
                # Get category
                category = self.categorizer.categorize_transaction(
                    transaction['description'], 
                    transaction['amount']
                )
                
                # Create new transaction record
                categorized_transaction = transaction.copy()
                categorized_transaction['category'] = category
                categorized_transactions.append(categorized_transaction)
                categories.append(category)
                
                if i % 10 == 0:
                    print(f"Processed {i}/{len(transactions)} transactions")
                    
            except Exception as e:
                print(f"Error processing transaction {i}: {e}")
                continue
        
        return categorized_transactions, categories
    
    def save_categorized_data(self, transactions, output_path):
        """Save categorized transactions to CSV"""
        try:
            fieldnames = ['date', 'description', 'amount', 'category']
            
            # Add any additional fields from original data
            if transactions:
                additional_fields = [k for k in transactions[0].keys() if k not in fieldnames]
                fieldnames.extend(additional_fields)
            
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(