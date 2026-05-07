```python
#!/usr/bin/env python3
"""
Transaction Categorization Engine

A rule-based system that automatically categorizes financial transactions into 
expense categories using keyword matching and merchant name patterns.

The engine analyzes transaction descriptions and merchant names to classify 
transactions into predefined categories such as groceries, utilities, 
entertainment, dining, transportation, and more.

Features:
- Keyword-based pattern matching
- Merchant name recognition
- Fallback categorization for unmatched transactions
- Case-insensitive matching
- Configurable category rules

Usage: python script.py
"""

import re
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Transaction:
    """Represents a financial transaction"""
    id: str
    description: str
    merchant: str
    amount: float
    category: Optional[str] = None


class TransactionCategorizer:
    """Rule-based transaction categorization engine"""
    
    def __init__(self):
        """Initialize the categorizer with predefined rules"""
        self.category_rules = {
            'groceries': {
                'keywords': ['grocery', 'supermarket', 'food', 'market', 'organic'],
                'merchants': ['walmart', 'kroger', 'safeway', 'whole foods', 'trader joe',
                            'publix', 'giant', 'stop shop', 'wegmans', 'aldi', 'costco',
                            'sam club', 'target', 'fresh market']
            },
            'utilities': {
                'keywords': ['electric', 'gas', 'water', 'sewer', 'internet', 'cable',
                           'phone', 'wireless', 'utility', 'power', 'energy'],
                'merchants': ['pge', 'edison', 'verizon', 'att', 'comcast', 'xfinity',
                            'spectrum', 'cox', 'tmobile', 'sprint', 'duke energy']
            },
            'entertainment': {
                'keywords': ['movie', 'cinema', 'theater', 'netflix', 'spotify', 'game',
                           'amusement', 'concert', 'show', 'streaming', 'music'],
                'merchants': ['netflix', 'spotify', 'hulu', 'disney', 'amazon prime',
                            'amc', 'regal', 'apple music', 'xbox', 'playstation',
                            'steam', 'ticketmaster']
            },
            'dining': {
                'keywords': ['restaurant', 'cafe', 'coffee', 'pizza', 'burger', 'bar',
                           'grill', 'bistro', 'diner', 'fast food', 'takeout'],
                'merchants': ['mcdonald', 'burger king', 'subway', 'starbucks', 'dunkin',
                            'pizza hut', 'domino', 'kfc', 'taco bell', 'wendy',
                            'chipotle', 'panera']
            },
            'transportation': {
                'keywords': ['gas', 'fuel', 'uber', 'lyft', 'taxi', 'metro', 'bus',
                           'train', 'parking', 'toll', 'automotive', 'car wash'],
                'merchants': ['shell', 'exxon', 'bp', 'chevron', 'mobil', 'uber',
                            'lyft', 'metro', 'bart', 'mta', 'parking']
            },
            'shopping': {
                'keywords': ['department store', 'retail', 'clothing', 'fashion',
                           'electronics', 'home goods', 'furniture'],
                'merchants': ['amazon', 'ebay', 'macy', 'nordstrom', 'best buy',
                            'home depot', 'lowe', 'ikea', 'bed bath', 'tjmaxx']
            },
            'healthcare': {
                'keywords': ['pharmacy', 'medical', 'doctor', 'dental', 'hospital',
                           'clinic', 'health', 'medicine', 'prescription'],
                'merchants': ['cvs', 'walgreens', 'rite aid', 'kaiser', 'blue cross',
                            'anthem', 'aetna', 'cigna']
            },
            'financial': {
                'keywords': ['bank', 'atm', 'fee', 'interest', 'loan', 'credit',
                           'insurance', 'investment', 'transfer'],
                'merchants': ['chase', 'wells fargo', 'bank america', 'citi',
                            'discover', 'capital one', 'american express']
            }
        }
        
        # Compile regex patterns for efficiency
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for each category"""
        self.compiled_patterns = {}
        
        for category, rules in self.category_rules.items():
            # Combine keywords and merchants into single pattern
            all_terms = rules['keywords'] + rules['merchants']
            pattern = '|'.join(re.escape(term) for term in all_terms)
            self.compiled_patterns[category] = re.compile(pattern, re.IGNORECASE)
    
    def categorize_transaction(self, transaction: Transaction) -> str:
        """
        Categorize a single transaction based on description and merchant
        
        Args:
            transaction: Transaction object to categorize
            
        Returns:
            str: Category name or 'other' if no match found
        """
        try:
            # Combine description and merchant for matching
            text_to_match = f"{transaction.description} {transaction.merchant}".lower()
            
            # Score each category
            category_scores = {}
            
            for category, pattern in self.compiled_patterns.items():
                matches = pattern.findall(text_to_match)
                if matches:
                    # Score based on number of matches and specificity
                    category_scores[category] = len(matches)
            
            # Return category with highest score, or 'other' if no matches
            if category_scores:
                best_category = max(category_scores.keys(), 
                                  key=lambda k: category_scores[k])
                return best_category
            else:
                return 'other'
                
        except Exception as e:
            print(f"Error categorizing transaction {transaction.id}: {e}")
            return 'other'
    
    def categorize_batch(self, transactions: List[Transaction]) -> List[Transaction]:
        """
        Categorize a batch of transactions
        
        Args:
            transactions: List of Transaction objects
            
        Returns:
            List[Transaction]: Transactions with categories assigned
        """
        categorized = []
        
        for transaction in transactions:
            try:
                category = self.categorize_transaction(transaction)
                transaction.category = category
                categorized.append(transaction)
            except Exception as e:
                print(f"Error processing transaction {transaction.id}: {e}")
                transaction.category = 'other'
                categorized.append(transaction)
        
        return categorized
    
    def get_category_summary(self, transactions: List[Transaction]) -> Dict[str, int]:
        """
        Generate summary of transactions by category
        
        Args:
            transactions: List of categorized transactions
            
        Returns:
            Dict[str, int]: Count of transactions per category
        """
        summary = {}
        for transaction in transactions:
            category = transaction.category or 'other'
            summary[category] = summary.get(category, 0) + 1
        
        return summary


def create_sample_transactions() -> List[Transaction]:
    """Create sample transactions for testing"""
    sample_data = [
        ("txn_001", "WALMART SUPERCENTER #1234", "WALMART", -89.45),
        ("txn_002", "PG&E ELECTRIC BILL", "PGE", -156.78),
        ("txn_003", "NETFLIX.COM", "NETFLIX", -15.99),
        ("txn_004", "STARBUCKS COFFEE #567", "STARBUCKS", -5.67),
        ("txn_005", "SHELL GAS STATION", "SHELL", -42