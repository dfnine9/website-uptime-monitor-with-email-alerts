```python
"""
Bank Statement Transaction Categorizer

This module parses CSV bank statements and automatically categorizes transactions
using rule-based logic. It reads CSV files containing transaction data and applies
predefined rules to classify each transaction into categories like groceries,
restaurants, utilities, etc.

Features:
- CSV parsing with pandas
- Rule-based transaction categorization
- Error handling for file operations
- Summary statistics output
- Extensible categorization rules

Usage: python script.py
"""

import pandas as pd
import re
import sys
from typing import Dict, List, Optional
import io

def create_sample_data() -> str:
    """Create sample CSV data for demonstration purposes."""
    sample_data = """Date,Description,Amount,Type
2024-01-15,"WALMART SUPERCENTER #1234",-85.67,Debit
2024-01-14,"SHELL GAS STATION",-45.23,Debit
2024-01-13,"SALARY DEPOSIT",3500.00,Credit
2024-01-12,"NETFLIX.COM",-15.99,Debit
2024-01-11,"STARBUCKS #5678",-6.75,Debit
2024-01-10,"ELECTRIC COMPANY",-125.45,Debit
2024-01-09,"AMAZON.COM PURCHASE",-67.89,Debit
2024-01-08,"ATM WITHDRAWAL",-100.00,Debit
2024-01-07,"RESTAURANT ABC",-45.30,Debit
2024-01-06,"PHARMACY CVS",-23.45,Debit"""
    return sample_data

class TransactionCategorizer:
    """Rule-based transaction categorization engine."""
    
    def __init__(self):
        self.categories = {
            'Groceries': [
                r'walmart', r'target', r'kroger', r'safeway', r'whole foods',
                r'trader joe', r'costco', r'grocery', r'supermarket'
            ],
            'Gas': [
                r'shell', r'exxon', r'chevron', r'bp', r'mobil', r'gas station',
                r'fuel', r'gasoline'
            ],
            'Restaurants': [
                r'restaurant', r'mcdonalds', r'burger king', r'subway',
                r'starbucks', r'dunkin', r'pizza', r'cafe', r'bistro'
            ],
            'Utilities': [
                r'electric', r'water', r'gas company', r'utility', r'power',
                r'internet', r'cable', r'phone'
            ],
            'Entertainment': [
                r'netflix', r'spotify', r'movie', r'theater', r'cinema',
                r'gaming', r'steam', r'xbox'
            ],
            'Healthcare': [
                r'pharmacy', r'cvs', r'walgreens', r'hospital', r'clinic',
                r'medical', r'doctor', r'dentist'
            ],
            'Shopping': [
                r'amazon', r'ebay', r'store', r'shop', r'mall', r'retail'
            ],
            'ATM/Cash': [
                r'atm', r'cash withdrawal', r'cash advance'
            ],
            'Income': [
                r'salary', r'payroll', r'deposit', r'income', r'wage'
            ],
            'Transfer': [
                r'transfer', r'venmo', r'paypal', r'zelle'
            ]
        }
    
    def categorize_transaction(self, description: str, amount: float) -> str:
        """
        Categorize a transaction based on description and amount.
        
        Args:
            description: Transaction description
            amount: Transaction amount (positive for credits, negative for debits)
            
        Returns:
            Category string
        """
        description_lower = description.lower()
        
        # Income transactions (positive amounts)
        if amount > 0:
            for pattern in self.categories['Income']:
                if re.search(pattern, description_lower):
                    return 'Income'
            return 'Other Income'
        
        # Expense transactions (negative amounts)
        for category, patterns in self.categories.items():
            if category == 'Income':  # Skip income patterns for expenses
                continue
                
            for pattern in patterns:
                if re.search(pattern, description_lower):
                    return category
        
        return 'Other'

def load_csv_data(file_path: Optional[str] = None) -> pd.DataFrame:
    """
    Load CSV data from file or create sample data.
    
    Args:
        file_path: Path to CSV file (optional)
        
    Returns:
        DataFrame with transaction data
    """
    try:
        if file_path:
            df = pd.read_csv(file_path)
            print(f"Loaded {len(df)} transactions from {file_path}")
        else:
            # Use sample data if no file provided
            sample_csv = create_sample_data()
            df = pd.read_csv(io.StringIO(sample_csv))
            print("Using sample transaction data")
        
        return df
        
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found. Using sample data instead.")
        sample_csv = create_sample_data()
        return pd.read_csv(io.StringIO(sample_csv))
    
    except Exception as e:
        print(f"Error loading CSV: {e}")
        raise

def validate_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate and clean the dataframe.
    
    Args:
        df: Raw transaction dataframe
        
    Returns:
        Cleaned dataframe
    """
    required_columns = ['Date', 'Description', 'Amount']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    
    # Clean data
    df = df.copy()
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
    df['Description'] = df['Description'].astype(str).str.strip()
    
    # Remove rows with invalid data
    initial_count = len(df)
    df = df.dropna(subset=['Date', 'Amount', 'Description'])
    
    if len(df) < initial_count:
        print(f"Warning: Removed {initial_count - len(df)} rows with invalid data")
    
    return df

def categorize_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add category column to transactions dataframe.
    
    Args:
        df: Transaction dataframe
        
    Returns:
        Dataframe with added Category column
    """
    categorizer = TransactionCategorizer()
    
    df = df.copy()
    df['Category'] = df.apply(
        lambda row: categorizer.categorize_transaction(
            row['Description'], 
            row['Amount']
        ), 
        axis=1
    )
    
    return df

def generate_summary_report(df: pd.DataFrame) -> None:
    """
    Generate and print summary statistics.
    
    Args:
        df: Categorized transactions dataframe
    """
    print("\n" + "="*60)
    print("TRANSACTION CATEGORIZATION SUMMARY")
    print("="*60)
    
    # Overall statistics
    total_transactions = len(df)
    total_expenses = df[df['Amount'] < 0]['Amount'].sum()
    total_income = df[df['Amount'] > 0]['Amount'].sum()
    
    print(f"Total Transactions: {total_transactions}")
    print(f"Total Income: ${total_income:,.2f}")
    print(f"Total Expenses: ${abs(total_expenses):,.2f}")
    print(f"Net Amount: ${total_income + total_expenses:,.2f}")
    
    # Category breakdown
    print("\n" + "-"*40)
    print("CATEGORY BREAKDOWN")
    print("-"*40)
    
    category_summary = df.groupby