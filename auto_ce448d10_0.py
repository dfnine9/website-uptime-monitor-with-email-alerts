```python
"""
Bank Transaction Analyzer

A self-contained Python script that parses bank CSV files, categorizes transactions
using keyword matching and simple ML classification, and calculates spending totals
by category with comprehensive data validation and error handling.

Features:
- Automatic CSV format detection and parsing
- Keyword-based transaction categorization
- Simple ML classification using TF-IDF and Naive Bayes
- Spending analysis with category totals
- Robust error handling and data validation
- No external dependencies beyond standard library

Usage: python script.py [csv_file_path]
If no file is provided, uses sample data for demonstration.
"""

import csv
import re
import sys
import os
from collections import defaultdict, Counter
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import math


class TransactionClassifier:
    """Simple ML classifier for transaction categorization using TF-IDF and Naive Bayes."""
    
    def __init__(self):
        self.category_words = defaultdict(Counter)
        self.category_counts = Counter()
        self.vocabulary = set()
        self.trained = False
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization of transaction description."""
        text = text.lower()
        # Remove special characters and split
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        return [word for word in words if len(word) > 2]
    
    def _calculate_tf_idf(self, words: List[str], category: str) -> Dict[str, float]:
        """Calculate TF-IDF scores for words in a category."""
        tf_idf = {}
        total_words = sum(self.category_words[category].values())
        total_docs = sum(self.category_counts.values())
        
        for word in words:
            if word in self.vocabulary:
                tf = self.category_words[category][word] / total_words
                df = sum(1 for cat in self.category_words if word in self.category_words[cat])
                idf = math.log(len(self.category_words) / df) if df > 0 else 0
                tf_idf[word] = tf * idf
        
        return tf_idf
    
    def train(self, descriptions: List[str], categories: List[str]):
        """Train the classifier with labeled data."""
        for desc, category in zip(descriptions, categories):
            words = self._tokenize(desc)
            self.vocabulary.update(words)
            self.category_counts[category] += 1
            
            for word in words:
                self.category_words[category][word] += 1
        
        self.trained = True
    
    def predict(self, description: str) -> str:
        """Predict category for a transaction description."""
        if not self.trained:
            return "Uncategorized"
        
        words = self._tokenize(description)
        best_category = "Uncategorized"
        best_score = float('-inf')
        
        for category in self.category_words:
            score = math.log(self.category_counts[category] / sum(self.category_counts.values()))
            
            for word in words:
                if word in self.category_words[category]:
                    tf = self.category_words[category][word] / sum(self.category_words[category].values())
                    df = sum(1 for cat in self.category_words if word in self.category_words[cat])
                    idf = math.log(len(self.category_words) / df) if df > 0 else 0
                    score += math.log(tf * idf + 1e-10)  # Add small value to avoid log(0)
            
            if score > best_score:
                best_score = score
                best_category = category
        
        return best_category


class BankTransactionParser:
    """Main class for parsing and analyzing bank transactions."""
    
    def __init__(self):
        self.transactions = []
        self.classifier = TransactionClassifier()
        
        # Keyword-based categorization rules
        self.category_keywords = {
            "Food & Dining": [
                "restaurant", "cafe", "coffee", "pizza", "burger", "food", "dining",
                "mcdonalds", "subway", "starbucks", "dominos", "kitchen", "grill"
            ],
            "Shopping": [
                "amazon", "walmart", "target", "store", "shop", "mall", "retail",
                "clothing", "fashion", "electronics", "purchase"
            ],
            "Transportation": [
                "gas", "fuel", "uber", "lyft", "taxi", "parking", "metro", "bus",
                "airline", "flight", "car", "vehicle", "transportation"
            ],
            "Bills & Utilities": [
                "electric", "water", "gas bill", "internet", "phone", "utility",
                "insurance", "rent", "mortgage", "loan", "payment"
            ],
            "Healthcare": [
                "pharmacy", "doctor", "hospital", "medical", "health", "clinic",
                "prescription", "dental", "vision"
            ],
            "Entertainment": [
                "movie", "theater", "netflix", "spotify", "game", "entertainment",
                "concert", "show", "park", "recreation"
            ],
            "ATM/Cash": [
                "atm", "cash", "withdrawal", "deposit"
            ]
        }
    
    def detect_csv_format(self, file_path: str) -> Optional[Dict[str, int]]:
        """Detect the CSV format by examining headers."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                sample = file.read(1024)
                file.seek(0)
                
                # Try different delimiters
                for delimiter in [',', ';', '\t']:
                    try:
                        reader = csv.reader(file, delimiter=delimiter)
                        headers = next(reader)
                        file.seek(0)
                        
                        # Map common header variations to standard names
                        header_map = {}
                        for i, header in enumerate(headers):
                            header_lower = header.lower().strip()
                            
                            if any(date_word in header_lower for date_word in ['date', 'transaction date', 'posted']):
                                header_map['date'] = i
                            elif any(desc_word in header_lower for desc_word in ['description', 'memo', 'detail', 'merchant']):
                                header_map['description'] = i
                            elif any(amt_word in header_lower for amt_word in ['amount', 'debit', 'credit', 'transaction amount']):
                                header_map['amount'] = i
                        
                        if len(header_map) >= 3:  # Need at least date, description, amount
                            return header_map
                    
                    except Exception:
                        continue
            
            return None
            
        except Exception as e:
            print(f"Error detecting CSV format: {e}")
            return None
    
    def parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float, handling various formats."""
        try:
            # Remove currency symbols and whitespace
            clean_amount = re.sub(r'[^\d\-\.\,]', '', str(amount_str))
            
            # Handle negative amounts in parentheses
            if '(' in str(amount_str) and ')' in str(amount_str):
                clean_amount = '-' + clean_amount.replace('(', '').replace(')', '')
            
            # Handle comma as thousand separator vs decimal separator
            if clean_amount.count('.') == 1 and clean_amount.count(',') >= 1:
                # Comma is thousand separator
                clean_amount = clean_amount.replace(',', '')
            elif clean_amount.count(',') == 1 and clean_amount.count('.') == 0:
                # Comma might be decimal separator
                clean_amount = clean_amount.replace(',', '.')
            
            return float(clean_amount)
        
        except (ValueError, TypeError):
            return 0.0
    
    def parse_date(self, date_str