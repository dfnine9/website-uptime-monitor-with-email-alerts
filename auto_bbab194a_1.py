```python
"""
Transaction Categorization System with Fuzzy Matching and Machine Learning

This module provides a comprehensive transaction categorization system that:
1. Applies rule-based categorization to financial transaction data
2. Implements fuzzy string matching for merchant name recognition
3. Uses machine learning to predict categories based on amount ranges and spending patterns
4. Learns and adapts from transaction history to improve accuracy over time

The system is designed to be self-contained and requires only standard library
modules plus httpx and anthropic for potential external integrations.
"""

import json
import re
import math
import statistics
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class Transaction:
    """Represents a financial transaction with categorization metadata."""
    id: str
    amount: float
    merchant: str
    description: str
    date: str
    category: Optional[str] = None
    confidence: float = 0.0


class FuzzyMatcher:
    """Implements fuzzy string matching using edit distance algorithms."""
    
    @staticmethod
    def levenshtein_distance(s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings."""
        if len(s1) < len(s2):
            return FuzzyMatcher.levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    @staticmethod
    def similarity_ratio(s1: str, s2: str) -> float:
        """Calculate similarity ratio between two strings (0-1)."""
        s1, s2 = s1.lower().strip(), s2.lower().strip()
        if not s1 or not s2:
            return 0.0
        
        distance = FuzzyMatcher.levenshtein_distance(s1, s2)
        max_len = max(len(s1), len(s2))
        return 1 - (distance / max_len)
    
    @staticmethod
    def fuzzy_match(query: str, candidates: List[str], threshold: float = 0.6) -> List[Tuple[str, float]]:
        """Find fuzzy matches for query string in candidates list."""
        matches = []
        for candidate in candidates:
            ratio = FuzzyMatcher.similarity_ratio(query, candidate)
            if ratio >= threshold:
                matches.append((candidate, ratio))
        
        return sorted(matches, key=lambda x: x[1], reverse=True)


class CategoryPredictor:
    """Machine learning-based category predictor using spending patterns."""
    
    def __init__(self):
        self.amount_patterns = defaultdict(list)  # category -> [amounts]
        self.merchant_categories = defaultdict(Counter)  # merchant -> category counts
        self.temporal_patterns = defaultdict(lambda: defaultdict(int))  # category -> {hour: count}
        self.trained = False
    
    def train(self, transactions: List[Transaction]) -> None:
        """Train the predictor on historical transaction data."""
        try:
            for txn in transactions:
                if not txn.category:
                    continue
                
                # Amount patterns
                self.amount_patterns[txn.category].append(txn.amount)
                
                # Merchant patterns
                merchant_clean = self._clean_merchant_name(txn.merchant)
                self.merchant_categories[merchant_clean][txn.category] += 1
                
                # Temporal patterns
                try:
                    hour = datetime.fromisoformat(txn.date.replace('Z', '+00:00')).hour
                    self.temporal_patterns[txn.category][hour] += 1
                except (ValueError, AttributeError):
                    pass
            
            self.trained = True
            print(f"Training completed on {len(transactions)} transactions")
            
        except Exception as e:
            print(f"Error during training: {e}")
    
    def _clean_merchant_name(self, merchant: str) -> str:
        """Clean and normalize merchant name for matching."""
        # Remove common prefixes/suffixes and normalize
        cleaned = re.sub(r'[^\w\s]', '', merchant.lower())
        cleaned = re.sub(r'\b(inc|llc|corp|ltd|co)\b', '', cleaned)
        return cleaned.strip()
    
    def _calculate_amount_probability(self, amount: float, category: str) -> float:
        """Calculate probability of amount belonging to category."""
        if category not in self.amount_patterns or not self.amount_patterns[category]:
            return 0.0
        
        amounts = self.amount_patterns[category]
        if len(amounts) < 2:
            return 0.5
        
        try:
            mean_amt = statistics.mean(amounts)
            std_amt = statistics.stdev(amounts) if len(amounts) > 1 else 1.0
            
            # Gaussian probability
            if std_amt == 0:
                return 1.0 if amount == mean_amt else 0.0
            
            z_score = abs(amount - mean_amt) / std_amt
            return math.exp(-0.5 * z_score * z_score)
            
        except (statistics.StatisticsError, ZeroDivisionError):
            return 0.0
    
    def predict(self, transaction: Transaction) -> Tuple[str, float]:
        """Predict category for a transaction."""
        if not self.trained:
            return "UNKNOWN", 0.0
        
        try:
            category_scores = defaultdict(float)
            merchant_clean = self._clean_merchant_name(transaction.merchant)
            
            # Merchant-based scoring
            if merchant_clean in self.merchant_categories:
                total_merchant_txns = sum(self.merchant_categories[merchant_clean].values())
                for category, count in self.merchant_categories[merchant_clean].items():
                    category_scores[category] += (count / total_merchant_txns) * 0.6
            
            # Amount-based scoring
            for category in self.amount_patterns:
                amount_prob = self._calculate_amount_probability(transaction.amount, category)
                category_scores[category] += amount_prob * 0.3
            
            # Temporal scoring (if date available)
            try:
                hour = datetime.fromisoformat(transaction.date.replace('Z', '+00:00')).hour
                for category, hour_counts in self.temporal_patterns.items():
                    if hour in hour_counts:
                        total_category_txns = sum(hour_counts.values())
                        if total_category_txns > 0:
                            category_scores[category] += (hour_counts[hour] / total_category_txns) * 0.1
            except (ValueError, AttributeError):
                pass
            
            if not category_scores:
                return "UNKNOWN", 0.0
            
            best_category = max(category_scores, key=category_scores.get)
            confidence = min(category_scores[best_category], 1.0)
            
            return best_category, confidence
            
        except Exception as e:
            print(f"Error in prediction: {e}")
            return "UNKNOWN", 0.0


class TransactionCategorizer:
    """Main transaction categorization system."""
    
    def __init__(self):
        self.fuzzy_matcher = FuzzyMatcher()
        self.predictor = CategoryPredictor()
        
        # Rule-based categorization patterns
        self.category_rules = {
            'GROCERIES': [
                'walmart