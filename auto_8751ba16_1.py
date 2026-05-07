```python
"""
Expense Categorization Engine

This module provides a keyword-based categorization engine for expense transactions
with fuzzy string matching capabilities for merchant name recognition. It categorizes
expenses into predefined categories: groceries, restaurants, gas, utilities, and 
entertainment based on merchant names and transaction descriptions.

The engine uses:
- Predefined keyword rules for each expense category
- Fuzzy string matching using difflib for merchant name recognition
- Configurable similarity thresholds for matching accuracy
- Comprehensive error handling for robust operation

Usage:
    python script.py
"""

import re
import difflib
from typing import Dict, List, Tuple, Optional
import json


class ExpenseCategorizer:
    """
    A keyword-based expense categorization engine with fuzzy string matching.
    """
    
    def __init__(self, similarity_threshold: float = 0.6):
        """
        Initialize the categorizer with predefined rules and similarity threshold.
        
        Args:
            similarity_threshold: Minimum similarity score for fuzzy matching (0.0-1.0)
        """
        self.similarity_threshold = similarity_threshold
        self.category_keywords = self._initialize_category_rules()
        self.known_merchants = self._initialize_known_merchants()
    
    def _initialize_category_rules(self) -> Dict[str, List[str]]:
        """Initialize predefined keyword rules for each expense category."""
        return {
            "groceries": [
                "grocery", "supermarket", "market", "food", "kroger", "walmart", "safeway",
                "whole foods", "trader joe", "costco", "sam's club", "target", "aldi",
                "publix", "wegmans", "harris teeter", "giant", "stop shop", "iga",
                "fresh market", "organic", "produce", "deli", "bakery"
            ],
            "restaurants": [
                "restaurant", "cafe", "coffee", "pizza", "burger", "starbucks", "mcdonald",
                "subway", "kfc", "taco bell", "domino", "papa john", "chipotle", "panera",
                "dunkin", "wendy", "arby", "chick-fil-a", "in-n-out", "five guys",
                "applebee", "olive garden", "red lobster", "outback", "chili", "diner",
                "bistro", "grill", "bar", "pub", "takeout", "delivery", "doordash",
                "uber eats", "grubhub", "postmates"
            ],
            "gas": [
                "gas", "fuel", "gasoline", "petrol", "shell", "exxon", "mobil", "bp",
                "chevron", "texaco", "citgo", "marathon", "speedway", "wawa", "sheetz",
                "circle k", "7-eleven", "valero", "phillips 66", "sunoco", "gulf",
                "station", "pump"
            ],
            "utilities": [
                "electric", "electricity", "gas utility", "water", "sewer", "internet",
                "cable", "phone", "wireless", "verizon", "at&t", "t-mobile", "sprint",
                "comcast", "xfinity", "spectrum", "cox", "optimum", "directv", "dish",
                "utility", "bill payment", "municipal", "city services", "waste management",
                "garbage", "recycling", "heating", "cooling", "hvac"
            ],
            "entertainment": [
                "movie", "theater", "cinema", "netflix", "hulu", "disney", "amazon prime",
                "spotify", "apple music", "youtube", "gaming", "xbox", "playstation",
                "nintendo", "steam", "concert", "ticket", "amusement", "park", "zoo",
                "museum", "sports", "gym", "fitness", "subscription", "streaming",
                "entertainment", "recreation", "hobby", "books", "magazine", "newspaper"
            ]
        }
    
    def _initialize_known_merchants(self) -> Dict[str, str]:
        """Initialize known merchant mappings to categories."""
        return {
            # Groceries
            "kroger": "groceries", "walmart": "groceries", "target": "groceries",
            "safeway": "groceries", "whole foods": "groceries", "trader joes": "groceries",
            "costco": "groceries", "sams club": "groceries", "aldi": "groceries",
            
            # Restaurants
            "mcdonalds": "restaurants", "starbucks": "restaurants", "subway": "restaurants",
            "pizza hut": "restaurants", "dominos": "restaurants", "kfc": "restaurants",
            "taco bell": "restaurants", "chipotle": "restaurants", "panera": "restaurants",
            
            # Gas
            "shell": "gas", "exxon": "gas", "bp": "gas", "chevron": "gas",
            "mobil": "gas", "texaco": "gas", "marathon": "gas", "speedway": "gas",
            
            # Utilities
            "verizon": "utilities", "att": "utilities", "comcast": "utilities",
            "xfinity": "utilities", "spectrum": "utilities", "cox communications": "utilities",
            
            # Entertainment
            "netflix": "entertainment", "spotify": "entertainment", "amazon prime": "entertainment",
            "disney plus": "entertainment", "hulu": "entertainment", "apple music": "entertainment"
        }
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text for better matching."""
        if not text:
            return ""
        
        # Convert to lowercase and remove special characters
        cleaned = re.sub(r'[^a-zA-Z0-9\s]', ' ', text.lower())
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned
    
    def _fuzzy_match_merchant(self, merchant_name: str) -> Optional[str]:
        """
        Use fuzzy string matching to find the best matching known merchant.
        
        Args:
            merchant_name: The merchant name to match
            
        Returns:
            Category if a good match is found, None otherwise
        """
        try:
            cleaned_merchant = self._clean_text(merchant_name)
            best_match = None
            best_score = 0.0
            
            for known_merchant, category in self.known_merchants.items():
                # Use difflib for fuzzy matching
                similarity = difflib.SequenceMatcher(
                    None, cleaned_merchant, known_merchant
                ).ratio()
                
                if similarity > best_score and similarity >= self.similarity_threshold:
                    best_score = similarity
                    best_match = category
            
            return best_match
        except Exception as e:
            print(f"Error in fuzzy matching: {e}")
            return None
    
    def _keyword_match_category(self, text: str) -> Optional[str]:
        """
        Match text against category keywords.
        
        Args:
            text: Text to categorize
            
        Returns:
            Best matching category or None
        """
        try:
            cleaned_text = self._clean_text(text)
            category_scores = {}
            
            for category, keywords in self.category_keywords.items():
                score = 0
                for keyword in keywords:
                    # Count keyword occurrences with partial matching
                    if keyword in cleaned_text:
                        score += 1
                    # Bonus for exact word matches
                    if f" {keyword} " in f" {cleaned_text} ":
                        score += 1
                
                if score > 0:
                    category_scores[category] = score
            
            # Return category with highest score
            if category_scores:
                return max(category_scores, key=category_scores.get)
            
            return None
        except Exception as e:
            print(f"Error in keyword matching: {e}")
            return None
    
    def categorize_expense(self, merchant_name: str, description: str = "") -> Tuple[str, float]:
        """
        Categorize an expense based on merchant name and description.
        
        Args:
            merchant_name: Name of the merchant
            description: Transaction description (optional)