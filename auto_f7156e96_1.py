```python
"""
Machine Learning Enhancement Module for Transaction Categorization

This module implements a TF-IDF vectorization system with Random Forest and SVM classifiers
to improve transaction categorization accuracy beyond simple keyword matching. It extracts
features from transaction descriptions and amounts to provide intelligent categorization.

Features:
- TF-IDF vectorization of transaction descriptions
- Random Forest and SVM classification algorithms
- Amount-based feature engineering
- Cross-validation for model evaluation
- Fallback to keyword matching when ML models have low confidence

Usage: python script.py
"""

import re
import math
import random
from collections import Counter, defaultdict
from typing import List, Dict, Tuple, Any, Optional


class TFIDFVectorizer:
    """Term Frequency-Inverse Document Frequency vectorizer implementation"""
    
    def __init__(self, max_features: int = 1000, min_df: int = 2):
        self.max_features = max_features
        self.min_df = min_df
        self.vocabulary_ = {}
        self.idf_values = {}
        self.feature_names = []
    
    def _preprocess(self, text: str) -> List[str]:
        """Preprocess text: lowercase, remove special chars, split"""
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text.lower())
        return [word for word in text.split() if len(word) > 2]
    
    def fit(self, documents: List[str]) -> None:
        """Fit the TF-IDF vectorizer to documents"""
        try:
            # Preprocess all documents
            processed_docs = [self._preprocess(doc) for doc in documents]
            
            # Count document frequency for each term
            doc_freq = defaultdict(int)
            for doc in processed_docs:
                unique_terms = set(doc)
                for term in unique_terms:
                    doc_freq[term] += 1
            
            # Filter terms by minimum document frequency
            filtered_terms = {term: freq for term, freq in doc_freq.items() 
                            if freq >= self.min_df}
            
            # Select top features by document frequency
            sorted_terms = sorted(filtered_terms.items(), key=lambda x: x[1], reverse=True)
            selected_terms = sorted_terms[:self.max_features]
            
            # Build vocabulary
            self.vocabulary_ = {term: idx for idx, (term, _) in enumerate(selected_terms)}
            self.feature_names = [term for term, _ in selected_terms]
            
            # Calculate IDF values
            n_docs = len(documents)
            for term in self.vocabulary_:
                df = doc_freq[term]
                self.idf_values[term] = math.log(n_docs / df)
                
        except Exception as e:
            print(f"Error in TF-IDF fit: {e}")
            raise
    
    def transform(self, documents: List[str]) -> List[List[float]]:
        """Transform documents to TF-IDF vectors"""
        try:
            vectors = []
            for doc in documents:
                terms = self._preprocess(doc)
                term_counts = Counter(terms)
                doc_length = len(terms)
                
                # Create vector
                vector = [0.0] * len(self.vocabulary_)
                for term, count in term_counts.items():
                    if term in self.vocabulary_:
                        tf = count / doc_length if doc_length > 0 else 0
                        idf = self.idf_values[term]
                        tfidf = tf * idf
                        vector[self.vocabulary_[term]] = tfidf
                
                vectors.append(vector)
            return vectors
            
        except Exception as e:
            print(f"Error in TF-IDF transform: {e}")
            raise


class RandomForestClassifier:
    """Simple Random Forest implementation"""
    
    def __init__(self, n_estimators: int = 10, max_depth: int = 5):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.trees = []
        self.classes_ = []
    
    def fit(self, X: List[List[float]], y: List[str]) -> None:
        """Train the Random Forest"""
        try:
            self.classes_ = list(set(y))
            n_samples = len(X)
            n_features = len(X[0]) if X else 0
            
            for _ in range(self.n_estimators):
                # Bootstrap sampling
                indices = [random.randint(0, n_samples-1) for _ in range(n_samples)]
                X_bootstrap = [X[i] for i in indices]
                y_bootstrap = [y[i] for i in indices]
                
                # Random feature selection
                feature_indices = random.sample(range(n_features), 
                                              min(int(math.sqrt(n_features)), n_features))
                
                # Train decision tree (simplified)
                tree = self._build_tree(X_bootstrap, y_bootstrap, feature_indices, 0)
                self.trees.append((tree, feature_indices))
                
        except Exception as e:
            print(f"Error in Random Forest fit: {e}")
            raise
    
    def _build_tree(self, X: List[List[float]], y: List[str], 
                   feature_indices: List[int], depth: int) -> Dict:
        """Build a simple decision tree"""
        if depth >= self.max_depth or len(set(y)) == 1 or len(X) < 2:
            return {'class': Counter(y).most_common(1)[0][0]}
        
        best_gini = float('inf')
        best_split = None
        
        for feature_idx in feature_indices:
            values = [row[feature_idx] for row in X]
            threshold = sum(values) / len(values)
            
            left_y = [y[i] for i, row in enumerate(X) if row[feature_idx] <= threshold]
            right_y = [y[i] for i, row in enumerate(X) if row[feature_idx] > threshold]
            
            if len(left_y) == 0 or len(right_y) == 0:
                continue
            
            gini = (len(left_y) * self._gini_impurity(left_y) + 
                   len(right_y) * self._gini_impurity(right_y)) / len(y)
            
            if gini < best_gini:
                best_gini = gini
                best_split = {
                    'feature': feature_idx,
                    'threshold': threshold,
                    'left': [X[i] for i, row in enumerate(X) if row[feature_idx] <= threshold],
                    'left_y': left_y,
                    'right': [X[i] for i, row in enumerate(X) if row[feature_idx] > threshold],
                    'right_y': right_y
                }
        
        if best_split is None:
            return {'class': Counter(y).most_common(1)[0][0]}
        
        return {
            'feature': best_split['feature'],
            'threshold': best_split['threshold'],
            'left': self._build_tree(best_split['left'], best_split['left_y'], 
                                   feature_indices, depth + 1),
            'right': self._build_tree(best_split['right'], best_split['right_y'], 
                                    feature_indices, depth + 1)
        }
    
    def _gini_impurity(self, y: List[str]) -> float:
        """Calculate Gini impurity"""
        if not y:
            return 0
        counts = Counter(y)
        impurity = 1.0
        for count in counts.values():
            prob = count / len(y)
            impurity -= prob ** 2
        return impurity
    
    def predict(self, X: List[List[float]]) -> List[str]:
        """Predict classes for samples"""
        try:
            predictions = []
            for sample in X: