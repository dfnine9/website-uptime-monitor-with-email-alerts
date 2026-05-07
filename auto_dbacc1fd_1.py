```python
#!/usr/bin/env python3
"""
Transaction Categorization System with Fuzzy Matching and Manual Overrides

This module provides enhanced transaction categorization using fuzzy string matching
for merchant name normalization. It handles edge cases for uncategorized transactions
and includes manual override functionality for improved accuracy.

Features:
- Fuzzy string matching for merchant names using Levenshtein distance
- Merchant name normalization and cleaning
- Manual override system with persistent storage
- Edge case handling for uncategorized transactions
- Self-contained implementation with minimal dependencies

Usage: python script.py
"""

import re
import json
import os
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from difflib import SequenceMatcher
import sqlite3
import hashlib


@dataclass
class Transaction:
    """Represents a financial transaction."""
    id: str
    merchant: str
    amount: float
    date: str
    description: str
    category: Optional[str] = None
    confidence: float = 0.0


class FuzzyMatcher:
    """Handles fuzzy string matching for merchant names."""
    
    @staticmethod
    def similarity(a: str, b: str) -> float:
        """Calculate similarity between two strings using SequenceMatcher."""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()
    
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
    def normalized_similarity(s1: str, s2: str) -> float:
        """Calculate normalized similarity score (0-1)."""
        max_len = max(len(s1), len(s2))
        if max_len == 0:
            return 1.0
        distance = FuzzyMatcher.levenshtein_distance(s1, s2)
        return 1 - (distance / max_len)


class MerchantNormalizer:
    """Normalizes merchant names for better matching."""
    
    # Common merchant suffixes and prefixes to remove
    NOISE_PATTERNS = [
        r'\b(inc|llc|ltd|corp|corporation|company|co)\b',
        r'\b(store|shop|market|center|centre)\b',
        r'\b(the|a|an)\b',
        r'[#*\-_]+',
        r'\b\d+\b',  # Remove standalone numbers
    ]
    
    # Common merchant name mappings
    KNOWN_MAPPINGS = {
        'amzn': 'amazon',
        'wmt': 'walmart',
        'tgt': 'target',
        'cvs': 'cvs pharmacy',
        'walgreens': 'walgreens pharmacy',
        'mcdonalds': 'mcdonald\'s',
        'starbucks': 'starbucks coffee',
    }
    
    @classmethod
    def normalize(cls, merchant_name: str) -> str:
        """Normalize merchant name for better matching."""
        if not merchant_name:
            return ""
        
        # Convert to lowercase and strip
        normalized = merchant_name.lower().strip()
        
        # Remove common noise patterns
        for pattern in cls.NOISE_PATTERNS:
            normalized = re.sub(pattern, '', normalized, flags=re.IGNORECASE)
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        # Apply known mappings
        for abbrev, full_name in cls.KNOWN_MAPPINGS.items():
            if abbrev in normalized:
                normalized = normalized.replace(abbrev, full_name)
        
        return normalized
    
    @classmethod
    def extract_key_terms(cls, merchant_name: str) -> List[str]:
        """Extract key terms from merchant name."""
        normalized = cls.normalize(merchant_name)
        # Split and filter out short words
        terms = [word for word in normalized.split() if len(word) > 2]
        return terms


class CategoryDatabase:
    """Manages category mappings and manual overrides."""
    
    def __init__(self, db_path: str = "categories.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for storing categories and overrides."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS merchant_categories (
                        merchant_normalized TEXT PRIMARY KEY,
                        category TEXT NOT NULL,
                        confidence REAL DEFAULT 1.0,
                        is_manual_override BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS transaction_overrides (
                        transaction_hash TEXT PRIMARY KEY,
                        category TEXT NOT NULL,
                        reason TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Insert default categories if empty
                cursor = conn.execute("SELECT COUNT(*) FROM merchant_categories")
                if cursor.fetchone()[0] == 0:
                    self._insert_default_categories(conn)
                    
        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")
    
    def _insert_default_categories(self, conn):
        """Insert default merchant categories."""
        default_categories = [
            ('amazon', 'Shopping', 0.9),
            ('walmart', 'Groceries', 0.9),
            ('target', 'Shopping', 0.9),
            ('cvs pharmacy', 'Healthcare', 0.9),
            ('walgreens pharmacy', 'Healthcare', 0.9),
            ('mcdonald\'s', 'Dining', 0.9),
            ('starbucks coffee', 'Dining', 0.9),
            ('shell', 'Gas', 0.9),
            ('exxon', 'Gas', 0.9),
            ('bp', 'Gas', 0.9),
            ('netflix', 'Entertainment', 0.9),
            ('spotify', 'Entertainment', 0.9),
            ('uber', 'Transportation', 0.9),
            ('lyft', 'Transportation', 0.9),
        ]
        
        conn.executemany(
            "INSERT INTO merchant_categories (merchant_normalized, category, confidence) VALUES (?, ?, ?)",
            default_categories
        )
    
    def get_category(self, merchant_normalized: str) -> Optional[Tuple[str, float]]:
        """Get category for normalized merchant name."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT category, confidence FROM merchant_categories WHERE merchant_normalized = ?",
                    (merchant_normalized,)
                )
                result = cursor.fetchone()
                return (result[0], result[1]) if result else None
        except sqlite3.Error as e:
            print(f"Database query error: {e}")
            return None
    
    def add_manual_override(self, merchant_normalized: str, category: str, reason: str = ""):
        """Add manual override for merchant category."""
        try:
            with sqlite3.connect(self