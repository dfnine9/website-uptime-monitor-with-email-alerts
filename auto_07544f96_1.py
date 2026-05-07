```python
"""
Transaction Categorization Engine

This module provides a comprehensive transaction categorization system that:
1. Applies regex-based rules to categorize transaction descriptions
2. Handles edge cases for uncategorized transactions with fuzzy matching
3. Populates an SQLite database with categorized expense data
4. Provides reporting and analysis capabilities

The system uses predefined regex patterns to match common transaction types
and falls back to keyword-based categorization for edge cases.
"""

import sqlite3
import re
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TransactionCategorizationEngine:
    def __init__(self, db_path: str = "transactions.db"):
        """Initialize the categorization engine with database connection."""
        self.db_path = db_path
        self.conn = None
        self.setup_database()
        self.load_categorization_rules()
        
    def setup_database(self):
        """Create and setup the SQLite database with required tables."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()
            
            # Create transactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    description TEXT NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT,
                    subcategory TEXT,
                    confidence_score REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create categories table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    parent_category TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create categorization_rules table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categorization_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern TEXT NOT NULL,
                    category TEXT NOT NULL,
                    subcategory TEXT,
                    priority INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self.conn.commit()
            logger.info("Database setup completed successfully")
            
        except sqlite3.Error as e:
            logger.error(f"Database setup failed: {e}")
            raise
    
    def load_categorization_rules(self):
        """Load predefined categorization rules into the system."""
        self.rules = {
            'Food & Dining': [
                (r'(?i)(restaurant|cafe|coffee|starbucks|mcdonald|burger|pizza|subway|food|dining)', 'Restaurant'),
                (r'(?i)(grocery|supermarket|walmart|target|kroger|safeway|whole foods)', 'Groceries'),
                (r'(?i)(bar|pub|brewery|wine|liquor)', 'Alcohol'),
                (r'(?i)(doordash|ubereats|grubhub|delivery)', 'Food Delivery'),
            ],
            'Transportation': [
                (r'(?i)(gas|fuel|shell|exxon|bp|chevron|mobil)', 'Gas'),
                (r'(?i)(uber|lyft|taxi|ride)', 'Rideshare'),
                (r'(?i)(parking|meter|garage)', 'Parking'),
                (r'(?i)(auto|car|mechanic|repair|tire|oil change)', 'Auto Maintenance'),
                (r'(?i)(public transport|metro|bus|train|subway)', 'Public Transit'),
            ],
            'Shopping': [
                (r'(?i)(amazon|ebay|online|purchase)', 'Online Shopping'),
                (r'(?i)(clothing|apparel|shoes|fashion)', 'Clothing'),
                (r'(?i)(electronics|best buy|apple|computer)', 'Electronics'),
                (r'(?i)(home depot|lowes|hardware|tools)', 'Home Improvement'),
            ],
            'Bills & Utilities': [
                (r'(?i)(electric|electricity|power|utility)', 'Electricity'),
                (r'(?i)(gas company|natural gas)', 'Gas Utility'),
                (r'(?i)(water|sewer|waste)', 'Water/Sewer'),
                (r'(?i)(internet|cable|tv|phone|telecom|verizon|att)', 'Telecom'),
                (r'(?i)(insurance|policy)', 'Insurance'),
            ],
            'Healthcare': [
                (r'(?i)(doctor|medical|clinic|hospital|pharmacy)', 'Medical'),
                (r'(?i)(dentist|dental)', 'Dental'),
                (r'(?i)(prescription|medicine|drug)', 'Pharmacy'),
            ],
            'Entertainment': [
                (r'(?i)(movie|cinema|theater|netflix|streaming)', 'Entertainment'),
                (r'(?i)(gym|fitness|yoga|sport)', 'Fitness'),
                (r'(?i)(game|gaming|xbox|playstation)', 'Gaming'),
            ],
            'Financial': [
                (r'(?i)(bank|atm|fee|charge|interest)', 'Banking Fees'),
                (r'(?i)(transfer|payment|paypal|venmo)', 'Transfer'),
                (r'(?i)(credit card|loan|mortgage)', 'Loan Payment'),
            ]
        }
        
        # Insert rules into database
        try:
            cursor = self.conn.cursor()
            for category, patterns in self.rules.items():
                for pattern, subcategory in patterns:
                    cursor.execute("""
                        INSERT OR IGNORE INTO categorization_rules 
                        (pattern, category, subcategory) VALUES (?, ?, ?)
                    """, (pattern, category, subcategory))
            self.conn.commit()
            logger.info("Categorization rules loaded successfully")
        except sqlite3.Error as e:
            logger.error(f"Failed to load categorization rules: {e}")
    
    def categorize_transaction(self, description: str) -> Tuple[str, str, float]:
        """
        Categorize a transaction based on its description.
        
        Returns:
            Tuple of (category, subcategory, confidence_score)
        """
        description = description.strip()
        
        # Try regex patterns first
        for category, patterns in self.rules.items():
            for pattern, subcategory in patterns:
                if re.search(pattern, description):
                    confidence = 0.9  # High confidence for regex matches
                    return category, subcategory, confidence
        
        # Fallback to keyword matching for edge cases
        category, subcategory, confidence = self._fuzzy_categorize(description)
        
        return category, subcategory, confidence
    
    def _fuzzy_categorize(self, description: str) -> Tuple[str, str, float]:
        """
        Handle edge cases with fuzzy keyword matching.
        """
        description_lower = description.lower()
        
        # Common keywords that might not be caught by regex
        keyword_mappings = {
            'misc': ('Miscellaneous', 'Other', 0.3),
            'check': ('Financial', 'Check Payment', 0.5),
            'withdrawal': ('Financial', 'ATM Withdrawal', 0.7),
            'deposit': ('Income', 'Deposit', 0.8),
            'refund': ('Financial', 'Refund', 0.7),
            'fee': ('Financial', 'Banking Fees', 0.8),
            'subscription': ('Bills & Utilities', 'Subscription', 0.6),
            'membership': ('Bills & Utilities', 'Membership', 0.6),
        }
        
        # Check for keyword matches
        for keyword, (category, subcategory, confidence) in keyword_mappings.items():
            if keyword in description_lower:
                return category, subcategory, confidence
        
        # If no match found, categorize as uncategorized
        return 'Uncategorized', 'Unknown',