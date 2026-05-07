```python
#!/usr/bin/env python3
"""
Expense Categorization System

This module implements a hybrid expense categorization system that assigns
expenses to predefined categories (food, transportation, entertainment, etc.)
based on merchant names and purchase descriptions. It uses both keyword 
matching and a simple ML-like scoring system for classification.

The system processes expense data and outputs categorized results with
confidence scores. It's designed to be self-contained with minimal
external dependencies.

Usage: python script.py
"""

import re
import json
import sys
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class Expense:
    """Represents a single expense entry."""
    merchant: str
    description: str
    amount: float
    
    def __str__(self) -> str:
        return f"${self.amount:.2f} at {self.merchant} - {self.description}"


@dataclass
class CategoryMatch:
    """Represents a category match with confidence score."""
    category: str
    confidence: float
    matched_keywords: List[str]


class ExpenseCategorizationSystem:
    """Main categorization system using keyword matching and ML-like scoring."""
    
    def __init__(self):
        self.categories = {
            'food': {
                'keywords': [
                    'restaurant', 'cafe', 'coffee', 'pizza', 'burger', 'taco', 'sushi',
                    'grocery', 'market', 'supermarket', 'deli', 'bakery', 'food',
                    'dining', 'lunch', 'dinner', 'breakfast', 'meal', 'snack',
                    'mcdonalds', 'starbucks', 'subway', 'chipotle', 'dominos',
                    'whole foods', 'safeway', 'kroger', 'trader joes'
                ],
                'patterns': [r'.*food.*', r'.*eat.*', r'.*kitchen.*', r'.*cook.*']
            },
            'transportation': {
                'keywords': [
                    'gas', 'fuel', 'uber', 'lyft', 'taxi', 'bus', 'train', 'metro',
                    'parking', 'toll', 'car', 'auto', 'repair', 'mechanic',
                    'insurance', 'registration', 'license', 'transport', 'flight',
                    'airline', 'airport', 'rental', 'shell', 'chevron', 'bp',
                    'exxon', 'mobil', 'arco'
                ],
                'patterns': [r'.*gas.*station.*', r'.*auto.*', r'.*transport.*']
            },
            'entertainment': {
                'keywords': [
                    'movie', 'cinema', 'theater', 'netflix', 'spotify', 'gaming',
                    'concert', 'show', 'ticket', 'amusement', 'park', 'zoo',
                    'museum', 'entertainment', 'recreation', 'hobby', 'sports',
                    'gym', 'fitness', 'club', 'bar', 'pub', 'nightlife'
                ],
                'patterns': [r'.*entertainment.*', r'.*fun.*', r'.*play.*']
            },
            'shopping': {
                'keywords': [
                    'amazon', 'walmart', 'target', 'costco', 'mall', 'store',
                    'retail', 'clothing', 'shoes', 'electronics', 'books',
                    'home', 'garden', 'depot', 'best buy', 'apple store',
                    'pharmacy', 'cvs', 'walgreens'
                ],
                'patterns': [r'.*shop.*', r'.*store.*', r'.*retail.*']
            },
            'utilities': {
                'keywords': [
                    'electric', 'electricity', 'gas bill', 'water', 'sewer',
                    'internet', 'phone', 'cable', 'utility', 'power', 'energy',
                    'comcast', 'verizon', 'att', 'tmobile'
                ],
                'patterns': [r'.*utility.*', r'.*bill.*', r'.*service.*']
            },
            'healthcare': {
                'keywords': [
                    'doctor', 'hospital', 'clinic', 'pharmacy', 'medical',
                    'dental', 'vision', 'health', 'medicine', 'prescription',
                    'insurance', 'copay', 'deductible'
                ],
                'patterns': [r'.*medical.*', r'.*health.*', r'.*dr\..*']
            },
            'other': {
                'keywords': ['misc', 'miscellaneous', 'other', 'unknown'],
                'patterns': [r'.*']
            }
        }
        
    def preprocess_text(self, text: str) -> str:
        """Clean and normalize text for matching."""
        try:
            return re.sub(r'[^\w\s]', ' ', text.lower()).strip()
        except Exception as e:
            print(f"Error preprocessing text '{text}': {e}", file=sys.stderr)
            return text.lower()
    
    def calculate_keyword_score(self, text: str, keywords: List[str]) -> Tuple[float, List[str]]:
        """Calculate matching score based on keyword presence."""
        try:
            normalized_text = self.preprocess_text(text)
            matched_keywords = []
            score = 0.0
            
            for keyword in keywords:
                if keyword.lower() in normalized_text:
                    matched_keywords.append(keyword)
                    # Weight longer keywords more heavily
                    score += len(keyword.split()) * 1.5
            
            return score, matched_keywords
        except Exception as e:
            print(f"Error calculating keyword score: {e}", file=sys.stderr)
            return 0.0, []
    
    def calculate_pattern_score(self, text: str, patterns: List[str]) -> float:
        """Calculate matching score based on regex patterns."""
        try:
            normalized_text = self.preprocess_text(text)
            score = 0.0
            
            for pattern in patterns:
                if re.search(pattern, normalized_text, re.IGNORECASE):
                    score += 1.0
            
            return score
        except Exception as e:
            print(f"Error calculating pattern score: {e}", file=sys.stderr)
            return 0.0
    
    def categorize_expense(self, expense: Expense) -> CategoryMatch:
        """Categorize a single expense using hybrid approach."""
        try:
            combined_text = f"{expense.merchant} {expense.description}"
            best_match = CategoryMatch("other", 0.0, [])
            
            for category, config in self.categories.items():
                # Calculate keyword score
                keyword_score, matched_keywords = self.calculate_keyword_score(
                    combined_text, config['keywords']
                )
                
                # Calculate pattern score
                pattern_score = self.calculate_pattern_score(
                    combined_text, config['patterns']
                )
                
                # Combine scores with weights
                total_score = (keyword_score * 0.8) + (pattern_score * 0.2)
                
                # Normalize by text length to avoid bias toward longer descriptions
                text_length = len(combined_text.split())
                normalized_score = total_score / max(text_length, 1)
                
                if normalized_score > best_match.confidence:
                    best_match = CategoryMatch(category, normalized_score, matched_keywords)
            
            return best_match
            
        except Exception as e:
            print(f"Error categorizing expense {expense}: {e}", file=sys.stderr)
            return CategoryMatch("other", 0.0, [])
    
    def process_expenses(self, expenses: List[Expense]) -> Dict[str, List[Tuple[Expense, CategoryMatch]]]:
        """Process multiple expenses and return categorized results."""
        try:
            categorized = defaultdict(list)
            
            for expense in expenses:
                match = self.categorize_expense(expense)
                categorized[match.