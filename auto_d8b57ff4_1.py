```python
#!/usr/bin/env python3
"""
Transaction Categorization Engine

A self-contained machine learning system for automatically classifying financial transactions
into expense categories based on merchant names, amounts, and description patterns.

Uses rule-based pattern matching with fuzzy string similarity for merchant identification
and amount-based heuristics for category refinement. Categories include:
- Groceries, Utilities, Entertainment, Transportation, Healthcare, Shopping, 
  Dining, Gas/Fuel, Insurance, and Miscellaneous

The engine processes transaction data and outputs categorized results with confidence scores.
No external ML libraries required - implements custom similarity algorithms.
"""

import re
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class Transaction:
    """Represents a financial transaction with categorization metadata."""
    merchant: str
    amount: float
    description: str
    category: str = "Miscellaneous"
    confidence: float = 0.0

class TransactionCategorizer:
    """Machine learning-inspired categorization engine for financial transactions."""
    
    def __init__(self):
        self.categories = {
            "Groceries": {
                "keywords": ["grocery", "market", "food", "supermarket", "kroger", "walmart", "target", 
                           "safeway", "whole foods", "trader joe", "costco", "sam's club", "aldi"],
                "patterns": [r"\b(grocery|market|food)\b", r"\b(kroger|walmart|target)\b"],
                "amount_range": (5.0, 300.0)
            },
            "Utilities": {
                "keywords": ["electric", "gas", "water", "internet", "phone", "cable", "utility",
                           "comcast", "verizon", "att", "power", "energy", "duke energy"],
                "patterns": [r"\b(electric|utility|power)\b", r"\b(comcast|verizon)\b"],
                "amount_range": (20.0, 400.0)
            },
            "Entertainment": {
                "keywords": ["netflix", "spotify", "movie", "theater", "cinema", "entertainment",
                           "disney", "hulu", "amazon prime", "apple music", "concert", "show"],
                "patterns": [r"\b(netflix|spotify|movie)\b", r"\b(theater|cinema)\b"],
                "amount_range": (5.0, 200.0)
            },
            "Transportation": {
                "keywords": ["uber", "lyft", "taxi", "bus", "train", "metro", "parking",
                           "transport", "airline", "flight", "car rental", "hertz", "avis"],
                "patterns": [r"\b(uber|lyft|taxi)\b", r"\b(airline|flight)\b"],
                "amount_range": (3.0, 1000.0)
            },
            "Healthcare": {
                "keywords": ["pharmacy", "medical", "doctor", "hospital", "clinic", "cvs",
                           "walgreens", "health", "dental", "vision", "prescription"],
                "patterns": [r"\b(pharmacy|medical|doctor)\b", r"\b(cvs|walgreens)\b"],
                "amount_range": (10.0, 500.0)
            },
            "Shopping": {
                "keywords": ["amazon", "ebay", "store", "shop", "retail", "mall", "clothing",
                           "best buy", "home depot", "lowes", "macys", "nordstrom"],
                "patterns": [r"\b(amazon|store|shop)\b", r"\b(best buy|home depot)\b"],
                "amount_range": (10.0, 1000.0)
            },
            "Dining": {
                "keywords": ["restaurant", "cafe", "coffee", "starbucks", "mcdonald", "pizza",
                           "dining", "bar", "pub", "bistro", "diner", "fast food"],
                "patterns": [r"\b(restaurant|cafe|coffee)\b", r"\b(starbucks|mcdonald)\b"],
                "amount_range": (5.0, 150.0)
            },
            "Gas/Fuel": {
                "keywords": ["gas", "fuel", "shell", "exxon", "bp", "chevron", "mobil",
                           "station", "petroleum", "pump"],
                "patterns": [r"\b(gas|fuel|shell)\b", r"\b(exxon|chevron)\b"],
                "amount_range": (10.0, 150.0)
            },
            "Insurance": {
                "keywords": ["insurance", "policy", "premium", "allstate", "geico", "progressive",
                           "state farm", "coverage", "claim"],
                "patterns": [r"\b(insurance|premium)\b", r"\b(allstate|geico)\b"],
                "amount_range": (50.0, 500.0)
            }
        }
        
        # Pre-compile regex patterns for performance
        self._compiled_patterns = {}
        for category, data in self.categories.items():
            self._compiled_patterns[category] = [
                re.compile(pattern, re.IGNORECASE) for pattern in data["patterns"]
            ]
    
    def _fuzzy_match(self, text1: str, text2: str) -> float:
        """Calculate fuzzy string similarity using character-based matching."""
        try:
            text1, text2 = text1.lower().strip(), text2.lower().strip()
            if not text1 or not text2:
                return 0.0
            
            # Exact match
            if text1 == text2:
                return 1.0
            
            # Substring match
            if text1 in text2 or text2 in text1:
                return 0.8
            
            # Character overlap ratio
            set1, set2 = set(text1), set(text2)
            intersection = len(set1 & set2)
            union = len(set1 | set2)
            
            if union == 0:
                return 0.0
            
            return intersection / union
            
        except Exception:
            return 0.0
    
    def _keyword_score(self, text: str, keywords: List[str]) -> float:
        """Calculate keyword matching score for given text."""
        try:
            text_lower = text.lower()
            matches = 0
            total_keywords = len(keywords)
            
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    matches += 1
                else:
                    # Fuzzy match for partial keywords
                    for word in text_lower.split():
                        if self._fuzzy_match(word, keyword) > 0.7:
                            matches += 0.5
                            break
            
            return matches / total_keywords if total_keywords > 0 else 0.0
            
        except Exception:
            return 0.0
    
    def _pattern_score(self, text: str, patterns: List) -> float:
        """Calculate regex pattern matching score."""
        try:
            matches = 0
            for pattern in patterns:
                if pattern.search(text):
                    matches += 1
            
            return matches / len(patterns) if patterns else 0.0
            
        except Exception:
            return 0.0
    
    def _amount_score(self, amount: float, amount_range: Tuple[float, float]) -> float:
        """Calculate amount-based confidence score."""
        try:
            min_amount, max_amount = amount_range
            if min_amount <= amount <= max_amount:
                return 1.0
            elif amount < min_amount:
                return max(0.0, 1.0 - (min_amount - amount) / min_amount)
            else:
                return max(0.0, 1.0 - (amount - max_amount) / max_amount)
                
        except Exception:
            return 0.0
    
    def categorize_transaction(self, transaction: Transaction) -> Transaction:
        """Categorize a single transaction using ML-inspired scoring."""
        try:
            combined_text = f"{transaction.merchant} {transaction.description}"
            best_category = "Miscellaneous"
            best_score =