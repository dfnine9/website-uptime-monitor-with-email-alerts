```python
#!/usr/bin/env python3
"""
Transaction Categorization Engine

A rule-based categorization system that matches transaction descriptions against
predefined patterns to automatically assign spending categories. The engine uses
regular expressions to identify merchants and transaction types, categorizing
them into common spending categories like grocery stores, gas stations,
restaurants, and utilities.

Features:
- Pattern-based matching using regular expressions
- Support for multiple categories: groceries, gas, restaurants, utilities, shopping, etc.
- Case-insensitive matching
- Fallback to 'Other' category for unmatched transactions
- Extensible pattern system for easy category additions

Usage:
    python script.py

The script includes sample transaction data and will output categorized results
to stdout showing the original description and assigned category.
"""

import re
from typing import Dict, List, Tuple


class TransactionCategorizer:
    """Rule-based transaction categorization engine."""
    
    def __init__(self):
        """Initialize the categorizer with predefined patterns."""
        self.category_patterns = {
            'Groceries': [
                r'\b(walmart|target|kroger|safeway|publix|whole foods|trader joe|costco|sam\'s club)\b',
                r'\b(grocery|supermarket|market|food store)\b',
                r'\b(aldi|wegmans|harris teeter|giant eagle|meijer)\b'
            ],
            'Gas': [
                r'\b(shell|exxon|bp|chevron|mobil|texaco|sunoco|marathon)\b',
                r'\b(gas|gasoline|fuel|petrol)\b',
                r'\b(circle k|wawa|sheetz|speedway|7-eleven)\b'
            ],
            'Restaurants': [
                r'\b(restaurant|cafe|diner|bistro|grill)\b',
                r'\b(mcdonald|burger king|wendy|taco bell|kfc|subway|pizza)\b',
                r'\b(starbucks|dunkin|coffee|chipotle|panera)\b',
                r'\b(domino|papa john|little caesar)\b'
            ],
            'Utilities': [
                r'\b(electric|electricity|power|energy)\b',
                r'\b(gas company|water|sewer|trash|garbage)\b',
                r'\b(utility|utilities|pge|con edison|duke energy)\b',
                r'\b(internet|cable|phone|wireless|verizon|at&t|comcast)\b'
            ],
            'Shopping': [
                r'\b(amazon|ebay|best buy|home depot|lowes)\b',
                r'\b(mall|department store|retail)\b',
                r'\b(macy|nordstrom|kohls|tj maxx|marshall)\b'
            ],
            'Entertainment': [
                r'\b(movie|cinema|theater|netflix|spotify|hulu)\b',
                r'\b(gym|fitness|recreation|entertainment)\b',
                r'\b(amc|regal|spotify|apple music)\b'
            ],
            'Transportation': [
                r'\b(uber|lyft|taxi|bus|train|metro|subway)\b',
                r'\b(parking|toll|airport|airline)\b',
                r'\b(rental car|hertz|enterprise|budget)\b'
            ],
            'Healthcare': [
                r'\b(doctor|hospital|pharmacy|medical|dental)\b',
                r'\b(cvs|walgreens|rite aid|urgent care)\b',
                r'\b(clinic|health|medicine|prescription)\b'
            ]
        }
        
        # Compile patterns for better performance
        self.compiled_patterns = {}
        for category, patterns in self.category_patterns.items():
            self.compiled_patterns[category] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]
    
    def categorize_transaction(self, description: str) -> str:
        """
        Categorize a transaction based on its description.
        
        Args:
            description (str): Transaction description to categorize
            
        Returns:
            str: Category name or 'Other' if no match found
        """
        try:
            if not description or not isinstance(description, str):
                return 'Other'
            
            # Clean the description
            cleaned_description = description.strip()
            
            # Check each category's patterns
            for category, patterns in self.compiled_patterns.items():
                for pattern in patterns:
                    if pattern.search(cleaned_description):
                        return category
            
            return 'Other'
            
        except Exception as e:
            print(f"Error categorizing transaction '{description}': {e}")
            return 'Other'
    
    def categorize_batch(self, transactions: List[str]) -> List[Tuple[str, str]]:
        """
        Categorize multiple transactions.
        
        Args:
            transactions (List[str]): List of transaction descriptions
            
        Returns:
            List[Tuple[str, str]]: List of (description, category) tuples
        """
        results = []
        for transaction in transactions:
            try:
                category = self.categorize_transaction(transaction)
                results.append((transaction, category))
            except Exception as e:
                print(f"Error processing transaction '{transaction}': {e}")
                results.append((transaction, 'Other'))
        
        return results
    
    def add_category_pattern(self, category: str, pattern: str):
        """
        Add a new pattern to an existing category or create a new category.
        
        Args:
            category (str): Category name
            pattern (str): Regular expression pattern
        """
        try:
            if category not in self.compiled_patterns:
                self.compiled_patterns[category] = []
            
            compiled_pattern = re.compile(pattern, re.IGNORECASE)
            self.compiled_patterns[category].append(compiled_pattern)
            
        except re.error as e:
            print(f"Invalid regex pattern '{pattern}': {e}")
        except Exception as e:
            print(f"Error adding pattern: {e}")


def main():
    """Main function to demonstrate the transaction categorization engine."""
    try:
        # Initialize the categorizer
        categorizer = TransactionCategorizer()
        
        # Sample transaction data
        sample_transactions = [
            "WALMART SUPERCENTER #1234",
            "SHELL OIL 12345678",
            "MCDONALD'S #5678",
            "ELECTRIC COMPANY BILL",
            "STARBUCKS STORE 9876",
            "AMAZON.COM AMZN.COM/BILL",
            "KROGER FUEL CENTER",
            "UBER TRIP 123ABC",
            "CVS PHARMACY #1111",
            "NETFLIX.COM",
            "PGE PACIFIC GAS ELECTRIC",
            "TARGET STORE T-1234",
            "CHIPOTLE MEXICAN GRILL",
            "VERIZON WIRELESS",
            "COSTCO WHOLESALE #456",
            "BP GAS STATION",
            "WHOLE FOODS MARKET",
            "AMC THEATRES",
            "UNKNOWN MERCHANT 123",
            "GROCERY OUTLET",
            "EXXONMOBIL",
            "PANERA BREAD",
            "COMCAST CABLE",
            "HOME DEPOT #789"
        ]
        
        print("Transaction Categorization Engine")
        print("=" * 50)
        print()
        
        # Categorize transactions
        results = categorizer.categorize_batch(sample_transactions)
        
        # Display results
        category_counts = {}
        for description, category in results:
            print(f"Transaction: {description:<35} → Category: {category}")
            category_counts[category] = category_counts.get(category, 0) + 1
        
        print()
        print("Category Summary")
        print("-" * 30)
        for category, count in sorted(category_counts.items()):
            print(f"{category}: {count} transactions")
        
        print()
        print("Total transactions processed:", len(results))
        
        # Demonstrate adding a custom pattern
        print()
        print("Adding custom pattern for 'Banking' category...")
        categorizer.add_category_pattern('Banking', r'\b(