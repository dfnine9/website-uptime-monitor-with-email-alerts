[ACTION:RESEARCH]

```python
"""
Transaction Categorization Engine

A self-contained Python script that categorizes financial transactions using regex patterns.
Matches transaction descriptions to predefined categories and subcategories, handles edge cases
for uncategorized transactions, and outputs structured expense data.

Usage: python script.py

Dependencies: Standard library only (re, json, datetime)
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class TransactionCategorizer:
    """Categorizes financial transactions using regex pattern matching."""
    
    def __init__(self):
        self.categories = {
            "FOOD_DINING": {
                "patterns": [
                    r"(?i)(restaurant|cafe|coffee|starbucks|mcdonalds|burger|pizza|subway|taco|diner)",
                    r"(?i)(food|dining|eat|meal|lunch|dinner|breakfast)",
                    r"(?i)(doordash|ubereats|grubhub|postmates|delivery)"
                ],
                "subcategories": {
                    "fast_food": [r"(?i)(mcdonalds|burger|pizza|subway|taco|kfc|wendys)"],
                    "coffee": [r"(?i)(starbucks|coffee|cafe|dunkin)"],
                    "delivery": [r"(?i)(doordash|ubereats|grubhub|postmates|delivery)"],
                    "restaurant": [r"(?i)(restaurant|diner|bistro|grill)"]
                }
            },
            "TRANSPORTATION": {
                "patterns": [
                    r"(?i)(gas|gasoline|fuel|shell|chevron|bp|exxon|mobil)",
                    r"(?i)(uber|lyft|taxi|cab|transport|metro|bus|train)",
                    r"(?i)(parking|toll|bridge|highway)"
                ],
                "subcategories": {
                    "fuel": [r"(?i)(gas|gasoline|fuel|shell|chevron|bp|exxon|mobil)"],
                    "rideshare": [r"(?i)(uber|lyft|taxi|cab)"],
                    "public_transport": [r"(?i)(metro|bus|train|transit)"],
                    "parking": [r"(?i)(parking|toll|bridge)"]
                }
            },
            "SHOPPING": {
                "patterns": [
                    r"(?i)(amazon|walmart|target|costco|store|shop|retail)",
                    r"(?i)(clothes|clothing|fashion|apparel)",
                    r"(?i)(grocery|supermarket|market|kroger|safeway)"
                ],
                "subcategories": {
                    "online": [r"(?i)(amazon|ebay|online|web)"],
                    "grocery": [r"(?i)(grocery|supermarket|market|kroger|safeway)"],
                    "clothing": [r"(?i)(clothes|clothing|fashion|apparel|nike|adidas)"],
                    "general": [r"(?i)(walmart|target|costco|store)"]
                }
            },
            "UTILITIES": {
                "patterns": [
                    r"(?i)(electric|electricity|power|pge|con\s*ed)",
                    r"(?i)(water|sewer|utility|municipal)",
                    r"(?i)(internet|cable|phone|wireless|verizon|att|comcast)"
                ],
                "subcategories": {
                    "electricity": [r"(?i)(electric|electricity|power|pge|con\s*ed)"],
                    "water": [r"(?i)(water|sewer)"],
                    "internet_phone": [r"(?i)(internet|cable|phone|wireless|verizon|att|comcast)"]
                }
            },
            "HEALTHCARE": {
                "patterns": [
                    r"(?i)(doctor|medical|hospital|clinic|pharmacy|cvs|walgreens)",
                    r"(?i)(dental|dentist|vision|optometry)",
                    r"(?i)(insurance|health|copay)"
                ],
                "subcategories": {
                    "pharmacy": [r"(?i)(pharmacy|cvs|walgreens|rite\s*aid)"],
                    "medical": [r"(?i)(doctor|medical|hospital|clinic)"],
                    "dental": [r"(?i)(dental|dentist)"],
                    "insurance": [r"(?i)(insurance|copay)"]
                }
            },
            "ENTERTAINMENT": {
                "patterns": [
                    r"(?i)(netflix|spotify|hulu|disney|streaming|subscription)",
                    r"(?i)(movie|cinema|theater|theatre|ticket)",
                    r"(?i)(game|gaming|steam|xbox|playstation)"
                ],
                "subcategories": {
                    "streaming": [r"(?i)(netflix|spotify|hulu|disney|streaming|subscription)"],
                    "movies": [r"(?i)(movie|cinema|theater|theatre|ticket)"],
                    "gaming": [r"(?i)(game|gaming|steam|xbox|playstation)"]
                }
            }
        }
        
    def _match_patterns(self, description: str, patterns: List[str]) -> bool:
        """Check if description matches any pattern in the list."""
        for pattern in patterns:
            if re.search(pattern, description):
                return True
        return False
    
    def _find_subcategory(self, description: str, subcategories: Dict[str, List[str]]) -> Optional[str]:
        """Find the most specific subcategory that matches the description."""
        for subcat_name, patterns in subcategories.items():
            if self._match_patterns(description, patterns):
                return subcat_name
        return None
    
    def categorize_transaction(self, description: str, amount: float) -> Dict:
        """
        Categorize a single transaction.
        
        Args:
            description: Transaction description
            amount: Transaction amount
            
        Returns:
            Dict containing category, subcategory, and confidence
        """
        description = description.strip()
        
        # Handle edge cases
        if not description:
            return {
                "category": "UNCATEGORIZED",
                "subcategory": "empty_description",
                "confidence": 0.0,
                "amount": amount
            }
            
        if len(description) < 3:
            return {
                "category": "UNCATEGORIZED", 
                "subcategory": "insufficient_data",
                "confidence": 0.0,
                "amount": amount
            }
        
        # Try to match against each category
        for category_name, category_data in self.categories.items():
            if self._match_patterns(description, category_data["patterns"]):
                subcategory = self._find_subcategory(description, category_data["subcategories"])
                
                return {
                    "category": category_name,
                    "subcategory": subcategory or "general",
                    "confidence": 0.9 if subcategory else 0.7,
                    "amount": amount
                }
        
        # Handle uncategorized transactions
        # Check for common patterns that might indicate specific types
        if re.search(r"(?i)(refund|credit|return)", description):
            return {
                "category": "UNCATEGORIZED",
                "subcategory": "refund_credit",
                "confidence": 0.6,
                "amount": amount
            }
        
        if re.search(r"(?i)(fee|charge|penalty)", description):
            return {
                "category": "UNCATEGORIZED", 
                "subcategory": "fees_charges",
                "confidence": 0.6,
                "amount": amount
            }
            
        if re.search(r"(?i)(transfer|deposit|withdrawal)", description):
            return {
                "category": "UNCATEGORIZED",
                "subcategory": "transfers",
                "confidence": 0.6,
                "amount": amount
            }
        
        return {
            "category": "UNCATEGORIZED",
            "subcategory": "unknown",
            "confidence": 0.0,
            "amount": amount
        }


def main():
    """Main function to demonstrate the categor