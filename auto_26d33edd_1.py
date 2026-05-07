```python
"""
Expense Categorization Module

This module provides automatic expense categorization using both keyword matching
and a simple machine learning approach. It classifies expenses into predefined
categories such as food, transport, utilities, entertainment, etc.

The module uses:
1. Keyword-based classification for quick, rule-based categorization
2. A simple Naive Bayes-like approach for learning from patterns
3. Confidence scoring to indicate classification reliability

Usage:
    python script.py

The script will demonstrate categorization with sample expenses and show
how the system learns and improves classifications over time.
"""

import re
import json
import math
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Optional

class ExpenseCategorizer:
    """
    Automatic expense categorization system using keyword matching and ML.
    """
    
    def __init__(self):
        self.categories = {
            'food': ['restaurant', 'grocery', 'coffee', 'pizza', 'burger', 'cafe', 'deli', 
                    'market', 'food', 'lunch', 'dinner', 'breakfast', 'mcdonalds', 'subway',
                    'starbucks', 'dominos', 'supermarket', 'bakery'],
            'transport': ['gas', 'fuel', 'uber', 'lyft', 'taxi', 'bus', 'train', 'metro',
                         'parking', 'toll', 'airline', 'flight', 'car', 'vehicle', 'transit'],
            'utilities': ['electric', 'electricity', 'water', 'gas', 'internet', 'phone',
                         'cable', 'utility', 'power', 'heating', 'cooling', 'wifi'],
            'entertainment': ['movie', 'cinema', 'netflix', 'spotify', 'game', 'concert',
                            'theater', 'club', 'bar', 'music', 'streaming', 'subscription'],
            'shopping': ['amazon', 'target', 'walmart', 'store', 'shop', 'retail', 'clothing',
                        'shoes', 'electronics', 'books', 'gift'],
            'healthcare': ['doctor', 'hospital', 'pharmacy', 'medical', 'dental', 'health',
                          'medicine', 'clinic', 'insurance'],
            'home': ['rent', 'mortgage', 'furniture', 'home', 'house', 'repair', 'maintenance',
                    'cleaning', 'garden', 'hardware'],
            'other': []
        }
        
        # ML components
        self.word_category_counts = defaultdict(lambda: defaultdict(int))
        self.category_counts = defaultdict(int)
        self.total_expenses = 0
        
    def preprocess_text(self, text: str) -> List[str]:
        """
        Preprocess expense description for analysis.
        
        Args:
            text: Raw expense description
            
        Returns:
            List of normalized words
        """
        try:
            # Convert to lowercase and extract words
            text = text.lower()
            # Remove special characters and numbers, keep only letters and spaces
            text = re.sub(r'[^a-z\s]', ' ', text)
            # Split into words and filter out short words
            words = [word.strip() for word in text.split() if len(word.strip()) > 2]
            return words
        except Exception as e:
            print(f"Error preprocessing text '{text}': {e}")
            return []
    
    def keyword_classify(self, description: str) -> Tuple[str, float]:
        """
        Classify expense using keyword matching.
        
        Args:
            description: Expense description
            
        Returns:
            Tuple of (category, confidence_score)
        """
        try:
            words = self.preprocess_text(description)
            category_scores = defaultdict(int)
            
            for word in words:
                for category, keywords in self.categories.items():
                    if category == 'other':
                        continue
                    for keyword in keywords:
                        if keyword in word or word in keyword:
                            category_scores[category] += 1
            
            if not category_scores:
                return 'other', 0.1
            
            best_category = max(category_scores.items(), key=lambda x: x[1])
            confidence = min(best_category[1] / len(words), 1.0)
            
            return best_category[0], confidence
            
        except Exception as e:
            print(f"Error in keyword classification for '{description}': {e}")
            return 'other', 0.0
    
    def ml_classify(self, description: str) -> Tuple[str, float]:
        """
        Classify expense using machine learning approach (Naive Bayes-like).
        
        Args:
            description: Expense description
            
        Returns:
            Tuple of (category, confidence_score)
        """
        try:
            if self.total_expenses == 0:
                return 'other', 0.0
            
            words = self.preprocess_text(description)
            if not words:
                return 'other', 0.0
            
            category_scores = {}
            
            for category in self.categories.keys():
                if self.category_counts[category] == 0:
                    category_scores[category] = 0.0
                    continue
                
                # Calculate log probability to avoid underflow
                log_prob = math.log(self.category_counts[category] / self.total_expenses)
                
                for word in words:
                    word_count = self.word_category_counts[word][category]
                    total_words_in_category = sum(self.word_category_counts[w][category] 
                                                for w in self.word_category_counts.keys())
                    
                    # Laplace smoothing
                    word_prob = (word_count + 1) / (total_words_in_category + len(self.word_category_counts))
                    log_prob += math.log(word_prob)
                
                category_scores[category] = log_prob
            
            if not category_scores:
                return 'other', 0.0
            
            best_category = max(category_scores.items(), key=lambda x: x[1])
            
            # Convert log probability to confidence (0-1)
            max_score = best_category[1]
            min_score = min(category_scores.values())
            
            if max_score == min_score:
                confidence = 0.5
            else:
                confidence = (max_score - min_score) / abs(max_score) if max_score != 0 else 0.5
                confidence = min(max(confidence, 0.1), 0.9)
            
            return best_category[0], confidence
            
        except Exception as e:
            print(f"Error in ML classification for '{description}': {e}")
            return 'other', 0.0
    
    def classify_expense(self, description: str, amount: float = None) -> Dict:
        """
        Classify an expense using both keyword and ML approaches.
        
        Args:
            description: Expense description
            amount: Optional expense amount
            
        Returns:
            Dictionary with classification results
        """
        try:
            keyword_result = self.keyword_classify(description)
            ml_result = self.ml_classify(description)
            
            # Combine results - prefer keyword if high confidence, otherwise use ML
            if keyword_result[1] > 0.7:
                final_category = keyword_result[0]
                final_confidence = keyword_result[1]
                method = 'keyword'
            elif ml_result[1] > keyword_result[1]:
                final_category = ml_result[0]
                final_confidence = ml_result[1]
                method = 'ml'
            else:
                final_category = keyword_result[0]
                final_confidence = keyword_result[1]
                method = 'keyword'
            
            return {
                'category': final_category,
                'confidence': round(final_confidence, 3),
                'method': method,
                'keyword_result': {'category': keyword_result[0], 'confidence': round(