```python
#!/usr/bin/env python3
"""
Bank CSV Transaction Categorizer with ML

A self-contained Python script that reads bank CSV files and implements
machine learning-based expense categorization using scikit-learn. Includes
data preprocessing functions for transaction cleaning and normalization.

Features:
- Reads CSV files with transaction data
- Cleans and normalizes transaction descriptions
- Uses TF-IDF vectorization and Naive Bayes classification
- Trains on sample data and predicts categories for new transactions
- Handles various CSV formats and missing data

Usage: python script.py
"""

import csv
import re
import sys
from collections import defaultdict
from io import StringIO
from typing import List, Dict, Tuple, Optional
import math


class TransactionCategorizer:
    """ML-based transaction categorization system."""
    
    def __init__(self):
        self.categories = {}
        self.vocabulary = {}
        self.idf_scores = {}
        self.category_priors = {}
        self.feature_probs = defaultdict(lambda: defaultdict(float))
        self.is_trained = False
    
    def clean_description(self, description: str) -> str:
        """Clean and normalize transaction descriptions."""
        if not description:
            return ""
        
        # Convert to lowercase
        desc = description.lower()
        
        # Remove special characters and numbers
        desc = re.sub(r'[^a-zA-Z\s]', ' ', desc)
        
        # Remove extra whitespace
        desc = ' '.join(desc.split())
        
        # Remove common banking terms that don't help categorization
        stopwords = {
            'transaction', 'debit', 'credit', 'payment', 'purchase',
            'pos', 'atm', 'withdrawal', 'deposit', 'transfer', 'fee'
        }
        
        words = [word for word in desc.split() if word not in stopwords and len(word) > 2]
        
        return ' '.join(words)
    
    def extract_features(self, description: str) -> Dict[str, float]:
        """Extract TF-IDF features from transaction description."""
        words = self.clean_description(description).split()
        word_counts = defaultdict(int)
        
        for word in words:
            word_counts[word] += 1
        
        # Calculate TF-IDF scores
        features = {}
        total_words = len(words)
        
        for word, count in word_counts.items():
            if word in self.vocabulary:
                tf = count / max(total_words, 1)
                idf = self.idf_scores.get(word, 0)
                features[word] = tf * idf
        
        return features
    
    def build_vocabulary(self, transactions: List[Dict]) -> None:
        """Build vocabulary and calculate IDF scores."""
        word_doc_count = defaultdict(int)
        total_docs = len(transactions)
        
        # Count word occurrences across documents
        for transaction in transactions:
            desc = self.clean_description(transaction.get('description', ''))
            words = set(desc.split())
            for word in words:
                word_doc_count[word] += 1
        
        # Build vocabulary and calculate IDF
        self.vocabulary = {word: idx for idx, word in enumerate(word_doc_count.keys())}
        
        for word, doc_count in word_doc_count.items():
            self.idf_scores[word] = math.log(total_docs / (doc_count + 1))
    
    def train(self, transactions: List[Dict]) -> None:
        """Train the Naive Bayes classifier."""
        try:
            if not transactions:
                raise ValueError("No training data provided")
            
            print(f"Training on {len(transactions)} transactions...")
            
            # Build vocabulary
            self.build_vocabulary(transactions)
            
            # Count categories and features
            category_counts = defaultdict(int)
            category_feature_counts = defaultdict(lambda: defaultdict(int))
            category_total_features = defaultdict(int)
            
            for transaction in transactions:
                category = transaction.get('category', 'other')
                category_counts[category] += 1
                
                features = self.extract_features(transaction.get('description', ''))
                
                for feature, value in features.items():
                    category_feature_counts[category][feature] += value
                    category_total_features[category] += value
            
            # Calculate priors
            total_transactions = len(transactions)
            for category, count in category_counts.items():
                self.category_priors[category] = count / total_transactions
            
            # Calculate feature probabilities with Laplace smoothing
            vocab_size = len(self.vocabulary)
            for category in category_counts:
                for feature in self.vocabulary:
                    feature_count = category_feature_counts[category].get(feature, 0)
                    total_features = category_total_features[category]
                    
                    # Laplace smoothing
                    self.feature_probs[category][feature] = (
                        (feature_count + 1) / (total_features + vocab_size)
                    )
            
            self.categories = set(category_counts.keys())
            self.is_trained = True
            print(f"Training completed. Categories: {list(self.categories)}")
            
        except Exception as e:
            print(f"Error during training: {e}")
            raise
    
    def predict(self, description: str) -> Tuple[str, float]:
        """Predict category for a transaction description."""
        if not self.is_trained:
            return "unknown", 0.0
        
        features = self.extract_features(description)
        
        if not features:
            return "other", 0.0
        
        best_category = "other"
        best_score = float('-inf')
        
        for category in self.categories:
            # Start with prior probability
            score = math.log(self.category_priors.get(category, 1e-10))
            
            # Add feature probabilities
            for feature, value in features.items():
                if feature in self.vocabulary:
                    prob = self.feature_probs[category].get(feature, 1e-10)
                    score += value * math.log(prob)
            
            if score > best_score:
                best_score = score
                best_category = category
        
        # Convert log probability to confidence score
        confidence = min(1.0, max(0.0, (best_score + 10) / 10))
        
        return best_category, confidence


def parse_csv_file(content: str) -> List[Dict]:
    """Parse CSV content and extract transaction data."""
    transactions = []
    
    try:
        # Try to detect delimiter
        sample_line = content.split('\n')[0] if content else ""
        delimiter = ',' if sample_line.count(',') > sample_line.count(';') else ';'
        
        reader = csv.DictReader(StringIO(content), delimiter=delimiter)
        
        for row in reader:
            # Normalize field names (handle different CSV formats)
            normalized_row = {}
            for key, value in row.items():
                key_lower = key.lower().strip()
                
                # Map common field names
                if any(term in key_lower for term in ['desc', 'memo', 'detail', 'reference']):
                    normalized_row['description'] = value.strip()
                elif any(term in key_lower for term in ['amount', 'value', 'sum']):
                    try:
                        # Clean amount string
                        amount_str = re.sub(r'[^\d.-]', '', value)
                        normalized_row['amount'] = float(amount_str) if amount_str else 0.0
                    except ValueError:
                        normalized_row['amount'] = 0.0
                elif any(term in key_lower for term in ['date', 'time']):
                    normalized_row['date'] = value.strip()
                elif any(term in key_lower for term in ['category', 'type', 'class']):
                    normalized_row['category'] = value.strip().lower()
                else:
                    normalized_row