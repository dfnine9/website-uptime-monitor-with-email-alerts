"""
Bank Statement Transaction Categorizer

This module parses CSV bank statements using pandas, validates required columns
(date, description, amount), and categorizes transactions using keyword matching.

Categories include: groceries, gas, restaurants, utilities, entertainment, and other.

Usage: python script.py

The script expects a CSV file named 'bank_statement.csv' in the same directory
with columns: date, description, amount (case-insensitive matching).
"""

import pandas as pd
import sys
import os
from datetime import datetime


class BankStatementParser:
    def __init__(self):
        self.categories = {
            'groceries': ['grocery', 'supermarket', 'walmart', 'target', 'costco', 
                         'safeway', 'kroger', 'trader joe', 'whole foods', 'food mart'],
            'gas': ['gas', 'fuel', 'shell', 'chevron', 'exxon', 'bp', 'mobil', 
                   'arco', 'texaco', 'station'],
            'restaurants': ['restaurant', 'cafe', 'pizza', 'burger', 'starbucks', 
                           'mcdonald', 'subway', 'taco bell', 'dining', 'food delivery',
                           'doordash', 'ubereats', 'grubhub'],
            'utilities': ['electric', 'water', 'gas bill', 'internet', 'phone', 
                         'cable', 'utility', 'power', 'energy'],
            'entertainment': ['movie', 'theater', 'netflix', 'spotify', 'gaming', 
                             'concert', 'tickets', 'entertainment', 'streaming']
        }
        
    def validate_columns(self, df):
        """Validate that required columns exist in the dataframe."""
        required_columns = ['date', 'description', 'amount']
        
        # Convert column names to lowercase for case-insensitive matching
        df.columns = df.columns.str.lower().str.strip()
        
        missing_columns = []
        for col in required_columns:
            if col not in df.columns:
                missing_columns.append(col)
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        return df[required_columns]
    
    def clean_data(self, df):
        """Clean and validate the data."""
        try:
            # Convert date column to datetime
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            
            # Remove rows with invalid dates
            df = df.dropna(subset=['date'])
            
            # Convert amount to numeric, removing any currency symbols
            df['amount'] = df['amount'].astype(str).str.replace('[$,]', '', regex=True)
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            
            # Remove rows with invalid amounts
            df = df.dropna(subset=['amount'])
            
            # Clean description column
            df['description'] = df['description'].astype(str).str.strip()
            
            return df
            
        except Exception as e:
            raise ValueError(f"Error cleaning data: {e}")
    
    def categorize_transaction(self, description):
        """Categorize a transaction based on description keywords."""
        description_lower = description.lower()
        
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category
        
        return 'other'
    
    def parse_statement(self, filename='bank_statement.csv'):
        """Parse the bank statement CSV file."""
        try:
            # Read the CSV file
            df = pd.read_csv(filename)
            print(f"✓ Successfully loaded {len(df)} transactions from {filename}")
            
            # Validate required columns
            df = self.validate_columns(df)
            print("✓ Required columns validated")
            
            # Clean the data
            df = self.clean_data(df)
            print(f"✓ Data cleaned, {len(df)} valid transactions remaining")
            
            # Categorize transactions
            df['category'] = df['description'].apply(self.categorize_transaction)
            print("✓ Transactions categorized")
            
            return df
            
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file '{filename}' not found in current directory")
        except Exception as e:
            raise Exception(f"Error parsing statement: {e}")
    
    def generate_summary(self, df):
        """Generate a summary of transactions by category."""
        summary = df.groupby('category').agg({
            'amount': ['count', 'sum', 'mean']
        }).round(2)
        
        summary.columns = ['Transaction Count', 'Total Amount', 'Average Amount']
        
        return summary.sort_values('Total Amount', ascending=False)
    
    def print_results(self, df):
        """Print the results to stdout."""
        print("\n" + "="*60)
        print("BANK STATEMENT ANALYSIS RESULTS")
        print("="*60)
        
        # Basic statistics
        print(f"\nOVERVIEW:")
        print(f"Total transactions: {len(df)}")
        print(f"Date range: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}")
        print(f"Total amount: ${df['amount'].sum():,.2f}")
        print(f"Average transaction: ${df['amount'].mean():.2f}")
        
        # Category summary
        print(f"\nCATEGORY BREAKDOWN:")
        summary = self.generate_summary(df)
        print(summary.to_string())
        
        # Sample transactions by category
        print(f"\nSAMPLE TRANSACTIONS BY CATEGORY:")
        for category in df['category'].unique():
            category_df = df[df['category'] == category]
            print(f"\n{category.upper()}:")
            sample_size = min(3, len(category_df))
            sample = category_df.head(sample_size)[['date', 'description', 'amount']]
            for _, row in sample.iterrows():
                print(f"  {row['date'].strftime('%Y-%m-%d')} | ${row['amount']:>8.2f} | {row['description'][:50]}")
        
        print("\n" + "="*60)


def main():
    """Main function to run the bank statement parser."""
    parser = BankStatementParser()
    
    try:
        # Parse the bank statement
        transactions_df = parser.parse_statement()
        
        # Print results
        parser.print_results(transactions_df)
        
    except Exception as e:
        print(f"ERROR: {e}")
        print("\nTo use this script:")
        print("1. Place your CSV file named 'bank_statement.csv' in the same directory")
        print("2. Ensure it has columns: date, description, amount")
        print("3. Run: python script.py")
        sys.exit(1)


if __name__ == "__main__":
    main()