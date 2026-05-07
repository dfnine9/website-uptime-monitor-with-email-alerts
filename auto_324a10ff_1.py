```python
#!/usr/bin/env python3
"""
AI-Powered Expense Categorization Module

This module loads transaction JSON data and uses AI (Claude API) to automatically
categorize expenses into predefined categories like groceries, dining, transportation,
utilities, etc. The categorized data is then saved back to the JSON files with
confidence scores.

Usage: python script.py

Requirements:
- Standard Python libraries (json, os, glob)
- httpx for HTTP requests
- anthropic for Claude API integration

The script processes all JSON files in the current directory that contain transaction
data and updates them with AI-generated categories and confidence scores.
"""

import json
import os
import glob
from typing import Dict, List, Any, Tuple
import sys

try:
    import httpx
    import anthropic
except ImportError as e:
    print(f"Error: Missing required package - {e}")
    print("Install with: pip install httpx anthropic")
    sys.exit(1)

# Predefined expense categories
EXPENSE_CATEGORIES = [
    "groceries",
    "dining", 
    "transportation",
    "utilities",
    "entertainment",
    "healthcare",
    "shopping",
    "gas",
    "insurance",
    "rent_mortgage",
    "education",
    "business",
    "travel",
    "subscriptions",
    "other"
]

class ExpenseCategorizer:
    """AI-powered expense categorization using Claude API"""
    
    def __init__(self, api_key: str = None):
        """Initialize the categorizer with Claude API key"""
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.categories = EXPENSE_CATEGORIES
    
    def categorize_transaction(self, description: str, amount: float = None) -> Tuple[str, float]:
        """
        Categorize a single transaction using AI
        
        Args:
            description: Transaction description
            amount: Transaction amount (optional)
            
        Returns:
            Tuple of (category, confidence_score)
        """
        try:
            prompt = f"""
            Categorize this expense transaction into one of these categories: {', '.join(self.categories)}
            
            Transaction: {description}
            {f'Amount: ${amount}' if amount else ''}
            
            Respond with only the category name and confidence score (0.0-1.0) in this exact format:
            category: confidence_score
            
            Example: groceries: 0.95
            """
            
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=50,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse response
            content = response.content[0].text.strip()
            if ':' in content:
                category, confidence = content.split(':', 1)
                category = category.strip().lower()
                confidence = float(confidence.strip())
                
                # Validate category
                if category not in self.categories:
                    category = "other"
                    confidence = 0.5
                    
                return category, min(max(confidence, 0.0), 1.0)
            else:
                return "other", 0.5
                
        except Exception as e:
            print(f"Error categorizing transaction '{description}': {e}")
            return "other", 0.0
    
    def process_transactions(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process multiple transactions and add categories
        
        Args:
            transactions: List of transaction dictionaries
            
        Returns:
            Updated transactions with categories and confidence scores
        """
        updated_transactions = []
        
        for i, transaction in enumerate(transactions):
            try:
                # Extract description and amount
                description = transaction.get('description', '') or transaction.get('merchant', '') or transaction.get('name', '')
                amount = transaction.get('amount', 0)
                
                if not description:
                    print(f"Warning: Transaction {i+1} has no description")
                    transaction['category'] = 'other'
                    transaction['confidence_score'] = 0.0
                else:
                    # Get AI categorization
                    category, confidence = self.categorize_transaction(description, amount)
                    transaction['category'] = category
                    transaction['confidence_score'] = confidence
                    
                    print(f"Transaction {i+1}: '{description[:50]}...' -> {category} ({confidence:.2f})")
                
                updated_transactions.append(transaction)
                
            except Exception as e:
                print(f"Error processing transaction {i+1}: {e}")
                transaction['category'] = 'other'
                transaction['confidence_score'] = 0.0
                updated_transactions.append(transaction)
        
        return updated_transactions

def load_json_data(filepath: str) -> Dict[str, Any]:
    """Load JSON data from file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return {}

def save_json_data(filepath: str, data: Dict[str, Any]) -> bool:
    """Save JSON data to file"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving {filepath}: {e}")
        return False

def find_transaction_files() -> List[str]:
    """Find JSON files that likely contain transaction data"""
    json_files = glob.glob("*.json")
    transaction_files = []
    
    for filepath in json_files:
        try:
            data = load_json_data(filepath)
            # Check if file contains transaction-like data
            if isinstance(data, list) and len(data) > 0:
                first_item = data[0]
                if isinstance(first_item, dict) and any(key in first_item for key in ['description', 'merchant', 'amount', 'transaction']):
                    transaction_files.append(filepath)
            elif isinstance(data, dict) and 'transactions' in data:
                transaction_files.append(filepath)
        except:
            continue
    
    return transaction_files

def main():
    """Main execution function"""
    print("AI-Powered Expense Categorization Starting...")
    print("=" * 50)
    
    # Check for API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        print("Set it with: export ANTHROPIC_API_KEY='your_key_here'")
        return
    
    try:
        # Initialize categorizer
        categorizer = ExpenseCategorizer()
        
        # Find transaction files
        transaction_files = find_transaction_files()
        
        if not transaction_files:
            print("No transaction JSON files found in current directory")
            print("Looking for files with transaction-like data structures...")
            return
        
        print(f"Found {len(transaction_files)} transaction files:")
        for file in transaction_files:
            print(f"  - {file}")
        print()
        
        # Process each file
        total_processed = 0
        
        for filepath in transaction_files:
            print(f"Processing {filepath}...")
            
            # Load data
            data = load_json_data(filepath)
            if not data:
                continue
            
            # Extract transactions
            if isinstance(data, list):
                transactions = data
            elif isinstance(data, dict) and 'transactions' in data:
                transactions = data['transactions']
            else:
                print(f"  Warning: Unknown data structure in {filepath}")
                continue
            
            if not transactions:
                print(f"  No transactions found in {filepath}")
                continue
            
            print(f"  Found {len(transactions)}