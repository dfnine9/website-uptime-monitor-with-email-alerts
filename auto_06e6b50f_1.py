```python
"""
Transaction Categorization Module

This module provides automatic categorization of financial transactions using:
1. Keyword matching with predefined category dictionaries
2. Machine learning clustering for uncategorized transactions using basic similarity metrics

Features:
- Rule-based categorization using keyword dictionaries
- Simple clustering algorithm for unknown transactions
- Text preprocessing and similarity calculation
- Comprehensive error handling
- Self-contained implementation with minimal dependencies

Usage:
    python script.py

The script will demonstrate categorization on sample transaction data.
"""

import json
import re
import math
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Set, Optional
import sys


class TransactionCategorizer:
    """
    A transaction categorization system that combines rule-based keyword matching
    with simple clustering for uncategorized transactions.
    """
    
    def __init__(self):
        """Initialize the categorizer with predefined category keywords."""
        self.category_keywords = {
            'groceries': {
                'walmart', 'kroger', 'safeway', 'whole foods', 'trader joe', 'costco',
                'grocery', 'supermarket', 'food mart', 'market', 'produce', 'fresh'
            },
            'utilities': {
                'electric', 'gas', 'water', 'internet', 'phone', 'cable', 'utility',
                'power company', 'telecom', 'verizon', 'att', 'comcast', 'spectrum'
            },
            'entertainment': {
                'netflix', 'spotify', 'hulu', 'disney', 'movie', 'theater', 'cinema',
                'concert', 'tickets', 'entertainment', 'streaming', 'games', 'xbox'
            },
            'restaurants': {
                'restaurant', 'cafe', 'coffee', 'starbucks', 'mcdonald', 'burger',
                'pizza', 'dining', 'takeout', 'delivery', 'food', 'bar', 'grill'
            },
            'transportation': {
                'gas station', 'shell', 'exxon', 'chevron', 'uber', 'lyft', 'taxi',
                'bus', 'train', 'metro', 'parking', 'toll', 'automotive', 'repair'
            },
            'healthcare': {
                'pharmacy', 'cvs', 'walgreens', 'hospital', 'clinic', 'doctor',
                'medical', 'health', 'dentist', 'insurance', 'copay'
            },
            'shopping': {
                'amazon', 'target', 'best buy', 'store', 'retail', 'clothing',
                'shoes', 'department', 'mall', 'online', 'purchase'
            }
        }
        
        self.clustered_categories = {}
        
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess transaction description text for better matching.
        
        Args:
            text: Raw transaction description
            
        Returns:
            Cleaned and normalized text
        """
        try:
            if not text:
                return ""
            
            # Convert to lowercase
            text = text.lower()
            
            # Remove special characters and extra spaces
            text = re.sub(r'[^\w\s]', ' ', text)
            text = re.sub(r'\s+', ' ', text)
            
            # Remove common transaction prefixes/suffixes
            text = re.sub(r'\b(debit|credit|card|purchase|payment|pos|atm)\b', '', text)
            
            return text.strip()
            
        except Exception as e:
            print(f"Error preprocessing text '{text}': {e}")
            return str(text).lower() if text else ""
    
    def categorize_by_keywords(self, description: str) -> Optional[str]:
        """
        Categorize transaction using keyword matching.
        
        Args:
            description: Transaction description
            
        Returns:
            Category name if match found, None otherwise
        """
        try:
            processed_desc = self.preprocess_text(description)
            
            for category, keywords in self.category_keywords.items():
                for keyword in keywords:
                    if keyword in processed_desc:
                        return category
                        
            return None
            
        except Exception as e:
            print(f"Error in keyword categorization for '{description}': {e}")
            return None
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts using Jaccard similarity.
        
        Args:
            text1, text2: Texts to compare
            
        Returns:
            Similarity score between 0 and 1
        """
        try:
            # Tokenize texts
            tokens1 = set(text1.split())
            tokens2 = set(text2.split())
            
            if not tokens1 and not tokens2:
                return 1.0
            if not tokens1 or not tokens2:
                return 0.0
            
            # Calculate Jaccard similarity
            intersection = tokens1.intersection(tokens2)
            union = tokens1.union(tokens2)
            
            return len(intersection) / len(union)
            
        except Exception as e:
            print(f"Error calculating similarity: {e}")
            return 0.0
    
    def cluster_transactions(self, uncategorized: List[Dict], threshold: float = 0.3) -> Dict[str, List[Dict]]:
        """
        Cluster uncategorized transactions using simple similarity-based clustering.
        
        Args:
            uncategorized: List of uncategorized transactions
            threshold: Similarity threshold for clustering
            
        Returns:
            Dictionary mapping cluster names to transaction lists
        """
        try:
            if not uncategorized:
                return {}
            
            clusters = {}
            cluster_counter = 0
            
            for transaction in uncategorized:
                description = self.preprocess_text(transaction['description'])
                assigned = False
                
                # Try to assign to existing cluster
                for cluster_name, cluster_transactions in clusters.items():
                    # Calculate similarity to cluster centroid (first transaction)
                    centroid_desc = self.preprocess_text(cluster_transactions[0]['description'])
                    similarity = self.calculate_similarity(description, centroid_desc)
                    
                    if similarity >= threshold:
                        clusters[cluster_name].append(transaction)
                        assigned = True
                        break
                
                # Create new cluster if no match found
                if not assigned:
                    cluster_name = f"cluster_{cluster_counter}"
                    clusters[cluster_name] = [transaction]
                    cluster_counter += 1
            
            return clusters
            
        except Exception as e:
            print(f"Error in clustering: {e}")
            return {}
    
    def suggest_category_names(self, cluster_transactions: List[Dict]) -> str:
        """
        Suggest a category name based on common words in cluster transactions.
        
        Args:
            cluster_transactions: List of transactions in the cluster
            
        Returns:
            Suggested category name
        """
        try:
            # Extract all words from transaction descriptions
            all_words = []
            for transaction in cluster_transactions:
                words = self.preprocess_text(transaction['description']).split()
                all_words.extend(words)
            
            if not all_words:
                return "unknown"
            
            # Find most common meaningful words
            word_counts = Counter(all_words)
            # Filter out very short words and common terms
            meaningful_words = [
                word for word, count in word_counts.most_common(5)
                if len(word) > 2 and count > 1
            ]
            
            if meaningful_words:
                return meaningful_words[0]
            else:
                return "misc"
                
        except Exception as e:
            print(f"Error suggesting category name: {e}")
            return "unknown"
    
    def categorize_transactions(self, transactions: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Categorize all transactions using both keyword matching and clustering.
        
        Args:
            transactions: List of transaction dictionaries with 'description' and 'amount' keys
            
        Returns: