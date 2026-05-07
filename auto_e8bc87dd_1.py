```python
"""
Transaction Classification System using TF-IDF and Naive Bayes

This module implements a text classification system for financial transactions using
scikit-learn's TF-IDF vectorization and Multinomial Naive Bayes classifier. It trains
on transaction descriptions to predict spending categories, providing an automated
way to categorize financial transactions based on their textual descriptions.

The system includes sample transaction data, preprocessing, model training, evaluation,
and prediction capabilities for new transaction descriptions.

Dependencies: scikit-learn, numpy, pandas (installable via pip)
Usage: python script.py
"""

import re
import warnings
from collections import defaultdict

# Suppress sklearn warnings for cleaner output
warnings.filterwarnings('ignore')

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
    from sklearn.pipeline import Pipeline
    import numpy as np
    import pandas as pd
except ImportError as e:
    print(f"Error: Required libraries not installed. Please run: pip install scikit-learn numpy pandas")
    print(f"Missing library: {e}")
    exit(1)


class TransactionClassifier:
    """
    A text classifier for categorizing financial transactions based on their descriptions.
    Uses TF-IDF vectorization with Multinomial Naive Bayes for classification.
    """
    
    def __init__(self, max_features=5000, min_df=2, max_df=0.95):
        """
        Initialize the classifier with TF-IDF and Naive Bayes components.
        
        Args:
            max_features (int): Maximum number of features for TF-IDF
            min_df (int): Minimum document frequency for TF-IDF
            max_df (float): Maximum document frequency for TF-IDF
        """
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=max_features,
                min_df=min_df,
                max_df=max_df,
                stop_words='english',
                lowercase=True,
                ngram_range=(1, 2)
            )),
            ('classifier', MultinomialNB(alpha=1.0))
        ])
        self.is_trained = False
    
    def preprocess_text(self, text):
        """
        Preprocess transaction description text.
        
        Args:
            text (str): Raw transaction description
            
        Returns:
            str: Cleaned and preprocessed text
        """
        if not isinstance(text, str):
            return ""
        
        # Remove special characters and numbers (keep letters and spaces)
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        return text.lower()
    
    def train(self, descriptions, categories):
        """
        Train the classifier on transaction descriptions and categories.
        
        Args:
            descriptions (list): List of transaction descriptions
            categories (list): List of corresponding categories
        """
        try:
            # Preprocess descriptions
            processed_descriptions = [self.preprocess_text(desc) for desc in descriptions]
            
            # Train the pipeline
            self.pipeline.fit(processed_descriptions, categories)
            self.is_trained = True
            print("✓ Model training completed successfully")
            
        except Exception as e:
            print(f"Error during training: {e}")
            raise
    
    def predict(self, descriptions):
        """
        Predict categories for new transaction descriptions.
        
        Args:
            descriptions (list): List of transaction descriptions to classify
            
        Returns:
            list: Predicted categories
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        try:
            processed_descriptions = [self.preprocess_text(desc) for desc in descriptions]
            predictions = self.pipeline.predict(processed_descriptions)
            return predictions
        except Exception as e:
            print(f"Error during prediction: {e}")
            raise
    
    def predict_proba(self, descriptions):
        """
        Get prediction probabilities for transaction descriptions.
        
        Args:
            descriptions (list): List of transaction descriptions
            
        Returns:
            numpy.ndarray: Probability matrix
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        try:
            processed_descriptions = [self.preprocess_text(desc) for desc in descriptions]
            probabilities = self.pipeline.predict_proba(processed_descriptions)
            return probabilities
        except Exception as e:
            print(f"Error during probability prediction: {e}")
            raise


def create_sample_data():
    """
    Create sample transaction data for demonstration.
    
    Returns:
        tuple: (descriptions, categories) lists
    """
    sample_transactions = [
        # Groceries
        ("WALMART SUPERCENTER #1234", "Groceries"),
        ("KROGER STORE #567", "Groceries"),
        ("WHOLE FOODS MARKET", "Groceries"),
        ("TARGET STORE T-0123", "Groceries"),
        ("SAFEWAY STORE 1234", "Groceries"),
        ("TRADER JOES #123", "Groceries"),
        ("COSTCO WHOLESALE #456", "Groceries"),
        ("PUBLIX SUPER MARKET", "Groceries"),
        
        # Restaurants
        ("MCDONALDS #12345", "Dining"),
        ("STARBUCKS STORE #789", "Dining"),
        ("PIZZA HUT #456", "Dining"),
        ("SUBWAY SANDWICHES", "Dining"),
        ("OLIVE GARDEN #123", "Dining"),
        ("CHIPOTLE MEXICAN GRILL", "Dining"),
        ("TACO BELL #789", "Dining"),
        ("PANERA BREAD #234", "Dining"),
        
        # Gas Stations
        ("SHELL OIL STATION", "Transportation"),
        ("CHEVRON GAS STATION", "Transportation"),
        ("BP GAS STATION #123", "Transportation"),
        ("EXXON MOBIL STATION", "Transportation"),
        ("MARATHON PETROLEUM", "Transportation"),
        ("TEXACO GAS STATION", "Transportation"),
        ("ARCO GAS STATION", "Transportation"),
        ("SUNOCO GAS STATION", "Transportation"),
        
        # Entertainment
        ("NETFLIX SUBSCRIPTION", "Entertainment"),
        ("SPOTIFY PREMIUM", "Entertainment"),
        ("AMAZON PRIME VIDEO", "Entertainment"),
        ("MOVIE THEATER AMC", "Entertainment"),
        ("STEAM PURCHASE", "Entertainment"),
        ("HULU SUBSCRIPTION", "Entertainment"),
        ("DISNEY PLUS", "Entertainment"),
        ("XBOX LIVE GOLD", "Entertainment"),
        
        # Shopping
        ("AMAZON.COM ORDER", "Shopping"),
        ("EBAY PURCHASE", "Shopping"),
        ("BEST BUY STORE #123", "Shopping"),
        ("HOME DEPOT #456", "Shopping"),
        ("LOWES STORE #789", "Shopping"),
        ("MACY'S DEPARTMENT STORE", "Shopping"),
        ("NORDSTROM STORE", "Shopping"),
        ("TJ MAXX STORE #234", "Shopping"),
        
        # Utilities
        ("ELECTRIC COMPANY BILL", "Utilities"),
        ("GAS COMPANY PAYMENT", "Utilities"),
        ("WATER UTILITY DEPT", "Utilities"),
        ("INTERNET SERVICE PROVIDER", "Utilities"),
        ("PHONE COMPANY BILL", "Utilities"),
        ("CABLE TV PAYMENT", "Utilities"),
        ("WASTE MANAGEMENT", "Utilities"),
        ("CITY UTILITIES PAYMENT", "Utilities"),
        
        # Healthcare
        ("CVS PHARMACY #123", "Healthcare"),
        ("WALGREENS PHARMACY", "Healthcare"),
        ("URGENT CARE CENTER", "Healthcare"),
        ("DENTAL OFFICE PAYMENT", "Healthcare"),
        ("VISION CENTER", "Healthcare"),
        ("HOSPITAL PAYMENT", "Healthcare"),
        ("MEDICAL GROUP", "Healthcare"),
        ("RITE A