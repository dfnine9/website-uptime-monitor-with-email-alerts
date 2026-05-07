```python
#!/usr/bin/env python3
"""
Bank Statement Transaction Classifier

This module parses CSV bank statements and automatically categorizes transactions
using regex pattern matching. It creates a default categories mapping file on
first run and applies intelligent classification to common expense types.

Features:
- Parses CSV bank statements with flexible column detection
- Creates default category mappings with regex patterns
- Classifies transactions into categories (groceries, gas, restaurants, utilities, etc.)
- Self-contained with minimal dependencies
- Comprehensive error handling

Usage: python script.py
"""

import csv
import json
import re
import os
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime


class TransactionClassifier:
    """Classifies bank transactions into predefined categories using regex patterns."""
    
    def __init__(self, categories_file: str = "categories.json"):
        self.categories_file = categories_file
        self.categories = self._load_or_create_categories()
        
    def _create_default_categories(self) -> Dict[str, Any]:
        """Create default category mappings with regex patterns."""
        return {
            "groceries": {
                "patterns": [
                    r"(?i)(walmart|target|safeway|kroger|publix|whole foods|trader joe|costco|sam's club)",
                    r"(?i)(grocery|market|food|supermarket)",
                    r"(?i)(fresh|organic|produce)"
                ],
                "keywords": ["grocery", "supermarket", "food store", "market"]
            },
            "gas": {
                "patterns": [
                    r"(?i)(shell|exxon|chevron|bp|mobil|sunoco|citgo|marathon|arco)",
                    r"(?i)(gas|fuel|petroleum|station)",
                    r"(?i)\b\d{4}\s*(gas|fuel)\b"
                ],
                "keywords": ["gas station", "fuel", "petroleum"]
            },
            "restaurants": {
                "patterns": [
                    r"(?i)(mcdonald|burger king|subway|starbucks|dunkin|kfc|pizza hut|domino)",
                    r"(?i)(restaurant|cafe|bistro|diner|grill|bar)",
                    r"(?i)(food|dining|eatery)"
                ],
                "keywords": ["restaurant", "cafe", "fast food", "dining"]
            },
            "utilities": {
                "patterns": [
                    r"(?i)(electric|electricity|power|utility)",
                    r"(?i)(gas company|water|sewer|trash|waste)",
                    r"(?i)(comcast|verizon|att|spectrum|internet|cable|phone)"
                ],
                "keywords": ["electric", "water", "gas bill", "internet", "cable"]
            },
            "shopping": {
                "patterns": [
                    r"(?i)(amazon|ebay|walmart|target|best buy|home depot|lowes)",
                    r"(?i)(store|shop|retail|purchase)",
                    r"(?i)(mall|center|plaza)"
                ],
                "keywords": ["store", "shopping", "retail", "purchase"]
            },
            "healthcare": {
                "patterns": [
                    r"(?i)(doctor|medical|hospital|clinic|pharmacy|cvs|walgreens)",
                    r"(?i)(health|dental|vision|prescription)",
                    r"(?i)(md|dr\.|physician)"
                ],
                "keywords": ["medical", "doctor", "pharmacy", "hospital"]
            },
            "transportation": {
                "patterns": [
                    r"(?i)(uber|lyft|taxi|bus|train|metro|transit)",
                    r"(?i)(parking|toll|bridge)",
                    r"(?i)(airline|flight|airport)"
                ],
                "keywords": ["transportation", "parking", "toll", "taxi"]
            },
            "entertainment": {
                "patterns": [
                    r"(?i)(netflix|spotify|hulu|disney|amazon prime|youtube)",
                    r"(?i)(movie|theater|cinema|concert|show)",
                    r"(?i)(game|entertainment|fun)"
                ],
                "keywords": ["entertainment", "streaming", "movie", "concert"]
            },
            "banking": {
                "patterns": [
                    r"(?i)(bank|atm|fee|charge|interest|transfer)",
                    r"(?i)(overdraft|maintenance|service charge)",
                    r"(?i)(withdrawal|deposit|check)"
                ],
                "keywords": ["bank fee", "atm", "service charge", "overdraft"]
            },
            "uncategorized": {
                "patterns": [],
                "keywords": []
            }
        }
    
    def _load_or_create_categories(self) -> Dict[str, Any]:
        """Load categories from file or create default ones."""
        try:
            if os.path.exists(self.categories_file):
                with open(self.categories_file, 'r') as f:
                    categories = json.load(f)
                    print(f"Loaded categories from {self.categories_file}")
                    return categories
            else:
                categories = self._create_default_categories()
                self._save_categories(categories)
                print(f"Created default categories file: {self.categories_file}")
                return categories
        except Exception as e:
            print(f"Error loading categories: {e}")
            print("Using default categories...")
            return self._create_default_categories()
    
    def _save_categories(self, categories: Dict[str, Any]) -> None:
        """Save categories to JSON file."""
        try:
            with open(self.categories_file, 'w') as f:
                json.dump(categories, f, indent=2)
        except Exception as e:
            print(f"Error saving categories: {e}")
    
    def classify_transaction(self, description: str, amount: float = 0) -> str:
        """Classify a transaction based on description and amount."""
        description = description.strip()
        
        # Check each category's patterns
        for category, config in self.categories.items():
            if category == "uncategorized":
                continue
                
            patterns = config.get("patterns", [])
            for pattern in patterns:
                try:
                    if re.search(pattern, description):
                        return category
                except re.error as e:
                    print(f"Invalid regex pattern '{pattern}': {e}")
                    continue
        
        return "uncategorized"


class CSVParser:
    """Parses CSV bank statements with flexible column detection."""
    
    def __init__(self):
        self.common_date_columns = ["date", "transaction date", "posted date", "trans date"]
        self.common_desc_columns = ["description", "desc", "transaction", "memo", "details"]
        self.common_amount_columns = ["amount", "debit", "credit", "transaction amount"]
    
    def _detect_columns(self, headers: List[str]) -> Dict[str, Optional[str]]:
        """Detect relevant columns from CSV headers."""
        headers_lower = [h.lower().strip() for h in headers]
        detected = {"date": None, "description": None, "amount": None}
        
        # Find date column
        for col in self.common_date_columns:
            if col in headers_lower:
                detected["date"] = headers[headers_lower.index(col)]
                break
        
        # Find description column
        for col in self.common_desc_columns:
            if col in headers_lower:
                detected["description"] = headers[headers_lower.index(col)]
                break
        
        # Find amount column
        for col in self.common_amount_columns:
            if col in headers_lower:
                detected["amount"] = headers[headers_lower.index(col)]
                break
        
        return detected
    
    def _parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float, handling various formats."""
        if not amount_str:
            return 0.0
        
        # Remove currency symbols and extra spaces
        clean_amount = re.sub(r'[^\d\.\-\+]', '', str(amount_str))
        
        try:
            return float(clean_amount) if clean_amount else 0.0