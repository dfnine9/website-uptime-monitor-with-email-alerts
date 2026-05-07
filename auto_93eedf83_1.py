```python
"""
Transaction Categorization Engine

This module provides an automated transaction classification system that uses
keyword matching and regex patterns to categorize financial transactions.
It analyzes merchant names and transaction amounts to classify transactions
into predefined categories such as groceries, gas, restaurants, utilities, etc.

The engine uses a rule-based approach with:
- Keyword matching for merchant names
- Regex patterns for specific merchant formats
- Amount-based rules for certain categories
- Fallback classification for unmatched transactions

Categories supported:
- Groceries, Gas, Restaurants, Utilities, Healthcare, Shopping,
- Entertainment, Travel, Banking, Education, Insurance, Other

Usage:
    python script.py
"""

import re
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Transaction:
    """Represents a financial transaction."""
    date: str
    merchant: str
    amount: float
    description: str = ""
    category: str = "Other"
    confidence: float = 0.0


class TransactionCategorizer:
    """Automated transaction categorization engine using keyword and regex matching."""
    
    def __init__(self):
        self.categories = self._initialize_categories()
        self.patterns = self._initialize_patterns()
    
    def _initialize_categories(self) -> Dict[str, Dict[str, List[str]]]:
        """Initialize category definitions with keywords and patterns."""
        return {
            "Groceries": {
                "keywords": [
                    "walmart", "target", "kroger", "safeway", "publix", "whole foods",
                    "trader joe", "costco", "sam's club", "aldi", "food lion",
                    "stop shop", "giant", "wegmans", "harris teeter", "albertsons",
                    "grocery", "market", "supermarket", "food", "fresh"
                ],
                "patterns": [
                    r".*grocery.*", r".*market.*", r".*food.*"
                ]
            },
            "Gas": {
                "keywords": [
                    "shell", "exxon", "bp", "chevron", "mobil", "texaco",
                    "citgo", "sunoco", "marathon", "speedway", "wawa",
                    "sheetz", "gas", "fuel", "petroleum", "station"
                ],
                "patterns": [
                    r".*gas.*", r".*fuel.*", r".*station.*", r"\d{4}\s*gas"
                ]
            },
            "Restaurants": {
                "keywords": [
                    "mcdonald", "burger king", "subway", "starbucks", "dunkin",
                    "taco bell", "kfc", "pizza hut", "domino", "papa john",
                    "chipotle", "panera", "chick-fil-a", "wendy", "arby",
                    "restaurant", "cafe", "diner", "bistro", "grill", "bar"
                ],
                "patterns": [
                    r".*restaurant.*", r".*cafe.*", r".*pizza.*", r".*coffee.*"
                ]
            },
            "Utilities": {
                "keywords": [
                    "electric", "electricity", "power", "gas company", "water",
                    "sewer", "internet", "cable", "phone", "wireless", "verizon",
                    "att", "comcast", "spectrum", "utility", "energy", "pg&e"
                ],
                "patterns": [
                    r".*electric.*", r".*utility.*", r".*power.*", r".*energy.*"
                ]
            },
            "Healthcare": {
                "keywords": [
                    "hospital", "clinic", "doctor", "physician", "medical",
                    "pharmacy", "cvs", "walgreens", "rite aid", "dentist",
                    "dental", "vision", "optometry", "health", "urgent care"
                ],
                "patterns": [
                    r".*medical.*", r".*health.*", r".*pharmacy.*", r".*dental.*"
                ]
            },
            "Shopping": {
                "keywords": [
                    "amazon", "ebay", "best buy", "home depot", "lowe", "macy",
                    "nordstrom", "tj maxx", "marshall", "ross", "department",
                    "store", "retail", "shopping", "mall"
                ],
                "patterns": [
                    r".*store.*", r".*retail.*", r".*shopping.*"
                ]
            },
            "Entertainment": {
                "keywords": [
                    "netflix", "spotify", "hulu", "disney", "theater", "cinema",
                    "movie", "concert", "ticket", "entertainment", "gaming",
                    "steam", "playstation", "xbox", "apple music"
                ],
                "patterns": [
                    r".*entertainment.*", r".*theater.*", r".*ticket.*"
                ]
            },
            "Travel": {
                "keywords": [
                    "airline", "hotel", "motel", "airbnb", "uber", "lyft",
                    "taxi", "rental", "airport", "travel", "booking",
                    "expedia", "hotels.com", "delta", "american airlines"
                ],
                "patterns": [
                    r".*travel.*", r".*hotel.*", r".*airline.*", r".*airport.*"
                ]
            },
            "Banking": {
                "keywords": [
                    "bank", "atm", "fee", "interest", "transfer", "deposit",
                    "withdrawal", "overdraft", "maintenance", "service charge"
                ],
                "patterns": [
                    r".*bank.*", r".*atm.*", r".*fee.*", r".*transfer.*"
                ]
            },
            "Education": {
                "keywords": [
                    "school", "college", "university", "tuition", "education",
                    "student", "learning", "course", "training", "academy"
                ],
                "patterns": [
                    r".*school.*", r".*education.*", r".*university.*"
                ]
            },
            "Insurance": {
                "keywords": [
                    "insurance", "premium", "policy", "coverage", "auto insurance",
                    "health insurance", "life insurance", "geico", "state farm",
                    "progressive", "allstate"
                ],
                "patterns": [
                    r".*insurance.*", r".*premium.*", r".*policy.*"
                ]
            }
        }
    
    def _initialize_patterns(self) -> List[Tuple[str, str, float]]:
        """Initialize special regex patterns with categories and confidence scores."""
        return [
            (r"^ATM\s+", "Banking", 0.9),
            (r"INTEREST\s+", "Banking", 0.95),
            (r"OVERDRAFT\s+", "Banking", 0.95),
            (r"CHECK\s+\d+", "Banking", 0.8),
            (r"PAYPAL\s+", "Shopping", 0.7),
            (r"SQ\s+\*", "Restaurants", 0.8),  # Square payments often restaurants
            (r"TST\s+\*", "Restaurants", 0.7),  # Toast POS system
            (r"AMZN\s+", "Shopping", 0.9),
            (r"UBER\s+", "Travel", 0.9),
            (r"LYFT\s+", "Travel", 0.9),
        ]
    
    def categorize_transaction(self, transaction: Transaction) -> Transaction:
        """Categorize a single transaction and return it with category and confidence."""
        try:
            merchant_lower = transaction.merchant.lower()
            description_lower = transaction.description.lower()
            combined_text = f"{merchant_lower} {description_lower}"
            
            best_category = "Other"
            best_confidence = 0.0
            
            # Check special patterns first
            for pattern, category, confidence in self.patterns:
                if re.search(pattern, transaction.merchant, re.IGNORECASE):
                    if confidence > best_confidence:
                        best_category = category
                        best_confidence = confidence