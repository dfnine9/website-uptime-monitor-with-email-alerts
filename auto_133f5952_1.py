```python
"""
Transaction Categorization Engine

A self-contained Python script that classifies financial transactions based on configurable
mapping rules with confidence scoring and manual override capabilities. Handles edge cases
through fuzzy matching and provides an interactive interface for uncertain categorizations.

Features:
- Rule-based transaction categorization with regex patterns
- Confidence scoring for classification certainty
- Manual override system for uncertain transactions
- Edge case handling with fallback mechanisms
- Extensible rule system for custom categories

Usage: python script.py
"""

import re
import json
import sys
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class Transaction:
    """Represents a financial transaction"""
    id: str
    date: str
    description: str
    amount: float
    category: Optional[str] = None
    confidence: Optional[float] = None
    manual_override: bool = False


@dataclass
class CategoryRule:
    """Represents a categorization rule"""
    category: str
    patterns: List[str]
    keywords: List[str]
    amount_range: Optional[Tuple[float, float]] = None
    priority: int = 1


class TransactionCategorizationEngine:
    """Main engine for categorizing transactions"""
    
    def __init__(self):
        self.rules: List[CategoryRule] = []
        self.confidence_threshold = 0.7
        self.manual_overrides: Dict[str, str] = {}
        self._load_default_rules()
    
    def _load_default_rules(self):
        """Load default categorization rules"""
        default_rules = [
            CategoryRule(
                category="Food & Dining",
                patterns=[r"restaurant", r"cafe", r"pizza", r"mcdonalds?", r"starbucks"],
                keywords=["food", "dining", "restaurant", "cafe", "fast food", "delivery"],
                priority=2
            ),
            CategoryRule(
                category="Transportation",
                patterns=[r"gas", r"fuel", r"uber", r"lyft", r"taxi", r"parking"],
                keywords=["gas", "fuel", "transport", "uber", "taxi", "parking"],
                priority=2
            ),
            CategoryRule(
                category="Shopping",
                patterns=[r"amazon", r"walmart", r"target", r"store", r"shop"],
                keywords=["shopping", "retail", "store", "purchase"],
                priority=1
            ),
            CategoryRule(
                category="Utilities",
                patterns=[r"electric", r"water", r"gas bill", r"internet", r"phone"],
                keywords=["utility", "bill", "electric", "water", "internet", "phone"],
                amount_range=(20.0, 500.0),
                priority=3
            ),
            CategoryRule(
                category="Entertainment",
                patterns=[r"netflix", r"spotify", r"movie", r"theater", r"cinema"],
                keywords=["entertainment", "streaming", "movie", "music", "subscription"],
                priority=2
            ),
            CategoryRule(
                category="Healthcare",
                patterns=[r"pharmacy", r"doctor", r"medical", r"hospital", r"cvs", r"walgreens"],
                keywords=["medical", "pharmacy", "doctor", "health", "prescription"],
                priority=3
            ),
            CategoryRule(
                category="Banking",
                patterns=[r"bank", r"atm", r"fee", r"transfer", r"deposit"],
                keywords=["bank", "fee", "transfer", "atm", "charge"],
                priority=2
            )
        ]
        self.rules.extend(default_rules)
    
    def add_rule(self, rule: CategoryRule):
        """Add a new categorization rule"""
        self.rules.append(rule)
        # Sort by priority (higher priority first)
        self.rules.sort(key=lambda x: x.priority, reverse=True)
    
    def _calculate_pattern_score(self, description: str, rule: CategoryRule) -> float:
        """Calculate confidence score based on pattern matching"""
        description_lower = description.lower()
        score = 0.0
        max_score = 0.0
        
        # Check regex patterns
        for pattern in rule.patterns:
            max_score += 0.4
            try:
                if re.search(pattern, description_lower, re.IGNORECASE):
                    score += 0.4
            except re.error:
                continue
        
        # Check keywords
        for keyword in rule.keywords:
            max_score += 0.3
            if keyword.lower() in description_lower:
                score += 0.3
        
        # Normalize score
        return score / max_score if max_score > 0 else 0.0
    
    def _check_amount_range(self, amount: float, rule: CategoryRule) -> bool:
        """Check if amount falls within rule's range"""
        if rule.amount_range is None:
            return True
        min_amount, max_amount = rule.amount_range
        return min_amount <= abs(amount) <= max_amount
    
    def categorize_transaction(self, transaction: Transaction) -> Transaction:
        """Categorize a single transaction"""
        try:
            # Check for manual override first
            if transaction.id in self.manual_overrides:
                transaction.category = self.manual_overrides[transaction.id]
                transaction.confidence = 1.0
                transaction.manual_override = True
                return transaction
            
            best_category = "Uncategorized"
            best_confidence = 0.0
            
            # Evaluate each rule
            for rule in self.rules:
                # Check amount range if specified
                if not self._check_amount_range(transaction.amount, rule):
                    continue
                
                # Calculate pattern-based confidence
                pattern_score = self._calculate_pattern_score(transaction.description, rule)
                
                # Apply priority weighting
                weighted_score = pattern_score * (rule.priority / 3.0)
                
                if weighted_score > best_confidence:
                    best_confidence = weighted_score
                    best_category = rule.category
            
            transaction.category = best_category
            transaction.confidence = best_confidence
            
            return transaction
            
        except Exception as e:
            print(f"Error categorizing transaction {transaction.id}: {str(e)}")
            transaction.category = "Error"
            transaction.confidence = 0.0
            return transaction
    
    def categorize_batch(self, transactions: List[Transaction]) -> List[Transaction]:
        """Categorize a batch of transactions"""
        categorized = []
        for transaction in transactions:
            categorized.append(self.categorize_transaction(transaction))
        return categorized
    
    def get_uncertain_transactions(self, transactions: List[Transaction]) -> List[Transaction]:
        """Get transactions with low confidence scores"""
        return [t for t in transactions if t.confidence and t.confidence < self.confidence_threshold]
    
    def set_manual_override(self, transaction_id: str, category: str):
        """Set manual override for a transaction"""
        self.manual_overrides[transaction_id] = category
        print(f"Manual override set: Transaction {transaction_id} -> {category}")
    
    def interactive_review(self, uncertain_transactions: List[Transaction]):
        """Interactive review of uncertain transactions"""
        if not uncertain_transactions:
            print("No uncertain transactions to review.")
            return
        
        print(f"\nFound {len(uncertain_transactions)} uncertain transactions:")
        print("=" * 60)
        
        available_categories = list(set(rule.category for rule in self.rules))
        available_categories.append("Custom")
        
        for i, transaction in enumerate(uncertain_transactions):
            print(f"\nTransaction {i+1}/{len(uncertain_transactions)}:")
            print(f"ID: {transaction.id}")
            print(f"Date: {transaction.date}")
            print(f"Description: {transaction.description}")
            print(f"Amount: ${transaction.amount:.2f}")
            print(f"Current Category: {transaction.category}")
            print(f"Confidence: {transaction.confidence:.2f}")
            print("\nAvailable categories:")
            for j, cat in enumerate(available_categories, 1):
                print(f"{j