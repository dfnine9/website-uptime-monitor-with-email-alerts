```python
"""
Transaction Data Parser and Categorization Module

This module provides functionality to parse CSV transaction data and generate
categorization prompts for OpenAI API calls. It processes financial transaction
records from CSV files and creates structured prompts that can be sent to
OpenAI's API for automatic transaction categorization.

Features:
- CSV parsing with configurable column mapping
- Transaction data validation and cleaning
- OpenAI API prompt generation for categorization
- Error handling for file operations and data processing
- Self-contained implementation with minimal dependencies

Usage:
    python script.py

Dependencies:
    - httpx (for HTTP requests)
    - anthropic (specified in requirements but not used in this implementation)
"""

import csv
import json
import sys
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import httpx


@dataclass
class Transaction:
    """Represents a financial transaction record."""
    date: str
    description: str
    amount: float
    account: str
    transaction_id: Optional[str] = None


class TransactionParser:
    """Handles parsing and processing of transaction data from CSV files."""
    
    def __init__(self, csv_file_path: str):
        self.csv_file_path = csv_file_path
        self.transactions: List[Transaction] = []
        
    def parse_csv(self, column_mapping: Optional[Dict[str, str]] = None) -> List[Transaction]:
        """
        Parse CSV file and extract transaction data.
        
        Args:
            column_mapping: Dictionary mapping CSV columns to transaction fields
                          Default: {'date': 'Date', 'description': 'Description', 
                                   'amount': 'Amount', 'account': 'Account'}
        
        Returns:
            List of Transaction objects
        """
        if column_mapping is None:
            column_mapping = {
                'date': 'Date',
                'description': 'Description', 
                'amount': 'Amount',
                'account': 'Account'
            }
        
        try:
            with open(self.csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        transaction = self._parse_transaction_row(row, column_mapping, row_num)
                        if transaction:
                            self.transactions.append(transaction)
                    except Exception as e:
                        print(f"Error processing row {row_num}: {e}", file=sys.stderr)
                        continue
                        
        except FileNotFoundError:
            print(f"Error: CSV file '{self.csv_file_path}' not found.", file=sys.stderr)
            return []
        except Exception as e:
            print(f"Error reading CSV file: {e}", file=sys.stderr)
            return []
            
        return self.transactions
    
    def _parse_transaction_row(self, row: Dict[str, str], column_mapping: Dict[str, str], row_num: int) -> Optional[Transaction]:
        """Parse a single CSV row into a Transaction object."""
        try:
            # Extract required fields
            date_str = row.get(column_mapping['date'], '').strip()
            description = row.get(column_mapping['description'], '').strip()
            amount_str = row.get(column_mapping['amount'], '').strip()
            account = row.get(column_mapping['account'], '').strip()
            
            # Validate required fields
            if not all([date_str, description, amount_str, account]):
                print(f"Warning: Missing required data in row {row_num}", file=sys.stderr)
                return None
            
            # Parse and validate amount
            try:
                # Remove currency symbols and commas
                clean_amount = amount_str.replace('$', '').replace(',', '').replace('(', '-').replace(')', '')
                amount = float(clean_amount)
            except ValueError:
                print(f"Warning: Invalid amount '{amount_str}' in row {row_num}", file=sys.stderr)
                return None
            
            # Validate date format (basic validation)
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                try:
                    datetime.strptime(date_str, '%m/%d/%Y')
                except ValueError:
                    print(f"Warning: Invalid date format '{date_str}' in row {row_num}", file=sys.stderr)
                    return None
            
            return Transaction(
                date=date_str,
                description=description,
                amount=amount,
                account=account,
                transaction_id=f"txn_{row_num}"
            )
            
        except Exception as e:
            print(f"Error parsing transaction row {row_num}: {e}", file=sys.stderr)
            return None


class CategorizationPromptBuilder:
    """Builds prompts for OpenAI API to categorize transactions."""
    
    def __init__(self):
        self.categories = [
            "Food & Dining",
            "Transportation",
            "Shopping",
            "Entertainment",
            "Bills & Utilities",
            "Healthcare",
            "Travel",
            "Business Services",
            "Banking & Finance",
            "Income",
            "Other"
        ]
    
    def build_categorization_prompt(self, transaction: Transaction) -> Dict[str, Any]:
        """
        Build a categorization prompt for a single transaction.
        
        Args:
            transaction: Transaction object to categorize
            
        Returns:
            Dictionary containing the prompt structure for OpenAI API
        """
        prompt = f"""Please categorize the following financial transaction into one of these categories:
{', '.join(self.categories)}

Transaction Details:
- Date: {transaction.date}
- Description: {transaction.description}
- Amount: ${transaction.amount:.2f}
- Account: {transaction.account}

Based on the description and amount, which category best fits this transaction?
Respond with just the category name from the list above."""

        return {
            "transaction_id": transaction.transaction_id,
            "prompt": prompt,
            "transaction_data": {
                "date": transaction.date,
                "description": transaction.description,
                "amount": transaction.amount,
                "account": transaction.account
            }
        }
    
    def build_batch_categorization_prompt(self, transactions: List[Transaction]) -> Dict[str, Any]:
        """
        Build a batch categorization prompt for multiple transactions.
        
        Args:
            transactions: List of Transaction objects to categorize
            
        Returns:
            Dictionary containing the batch prompt structure
        """
        transaction_list = []
        for i, txn in enumerate(transactions[:10]):  # Limit to 10 for API efficiency
            transaction_list.append(f"{i+1}. {txn.date} | {txn.description} | ${txn.amount:.2f} | {txn.account}")
        
        transactions_text = "\n".join(transaction_list)
        
        prompt = f"""Please categorize the following financial transactions into these categories:
{', '.join(self.categories)}

Transactions:
{transactions_text}

For each transaction, respond with the transaction number and category in this format:
1. Category Name
2. Category Name
etc."""

        return {
            "prompt": prompt,
            "transaction_count": len(transactions[:10]),
            "categories": self.categories
        }


def create_sample_csv():
    """Create a sample CSV file for testing purposes."""
    sample_data = [
        ["Date", "Description", "Amount", "Account"],
        ["2024-01-15", "STARBUCKS COFFEE", "-4.95", "Checking"],
        ["2024-01-16", "UBER RIDE", "-12.50", "Credit Card"],
        ["2024-01-17", "AMAZON PURCHASE", "-89.99", "Credit Card"],
        ["2024-01-18", "SALARY DEPOSIT", "3500.00", "Checking"],
        ["2024-01-19", "NETFLIX SUBSCRIPTION", "-15.99", "Credit Card"],
        ["2024-01-20", "GROCERY STORE", "-156.78", "Checking"]
    ]
    
    try:
        with open('sample_