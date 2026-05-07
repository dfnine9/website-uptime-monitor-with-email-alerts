```python
"""
Transaction Categorization System with Configurable Rules

This module provides a flexible transaction categorization system that allows users to:
- Define custom category keywords and rules via JSON configuration
- Automatically categorize transactions based on description matching
- Handle uncategorized transactions with AI-powered suggested categories
- Manage and update categorization rules dynamically

The system supports both rule-based categorization (using keyword matching)
and AI-assisted categorization for transactions that don't match existing rules.
"""

import json
import re
import os
import sys
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import httpx
import anthropic


class TransactionCategorizer:
    def __init__(self, config_file: str = "transaction_config.json"):
        """Initialize the categorizer with configuration file."""
        self.config_file = config_file
        self.config = self._load_or_create_config()
        self.anthropic_client = None
        self._initialize_ai_client()
    
    def _load_or_create_config(self) -> Dict:
        """Load existing config or create default one."""
        default_config = {
            "categories": {
                "Food & Dining": {
                    "keywords": ["restaurant", "cafe", "pizza", "mcdonalds", "starbucks", "food", "dining"],
                    "patterns": [".*restaurant.*", ".*cafe.*"],
                    "color": "#FF6B6B"
                },
                "Transportation": {
                    "keywords": ["gas", "fuel", "uber", "lyft", "taxi", "parking", "metro", "bus"],
                    "patterns": [".*gas.*", ".*fuel.*", ".*uber.*"],
                    "color": "#4ECDC4"
                },
                "Shopping": {
                    "keywords": ["amazon", "walmart", "target", "store", "shopping", "purchase"],
                    "patterns": [".*amazon.*", ".*store.*"],
                    "color": "#45B7D1"
                },
                "Utilities": {
                    "keywords": ["electric", "water", "internet", "phone", "utility", "bill"],
                    "patterns": [".*electric.*", ".*utility.*"],
                    "color": "#96CEB4"
                },
                "Entertainment": {
                    "keywords": ["netflix", "spotify", "movie", "game", "entertainment"],
                    "patterns": [".*netflix.*", ".*spotify.*"],
                    "color": "#FFEAA7"
                }
            },
            "ai_settings": {
                "enabled": True,
                "confidence_threshold": 0.7,
                "max_suggestions": 3
            },
            "learning_settings": {
                "auto_learn": True,
                "min_occurrences": 3
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading config: {e}. Using default config.")
                return default_config
        else:
            self._save_config(default_config)
            return default_config
    
    def _save_config(self, config: Dict) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except IOError as e:
            print(f"Error saving config: {e}")
    
    def _initialize_ai_client(self) -> None:
        """Initialize Anthropic AI client if API key is available."""
        try:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if api_key:
                self.anthropic_client = anthropic.Anthropic(api_key=api_key)
            else:
                print("ANTHROPIC_API_KEY not found. AI suggestions will be disabled.")
        except Exception as e:
            print(f"Error initializing AI client: {e}")
    
    def categorize_transaction(self, description: str, amount: float = 0.0) -> Tuple[Optional[str], float]:
        """
        Categorize a transaction based on description and amount.
        
        Returns:
            Tuple of (category_name, confidence_score)
        """
        description_lower = description.lower()
        
        # Rule-based categorization
        for category, rules in self.config["categories"].items():
            confidence = self._calculate_rule_confidence(description_lower, rules)
            if confidence > 0.5:  # Threshold for rule-based matching
                return category, confidence
        
        return None, 0.0
    
    def _calculate_rule_confidence(self, description: str, rules: Dict) -> float:
        """Calculate confidence score for rule-based matching."""
        keyword_matches = 0
        pattern_matches = 0
        
        # Check keyword matches
        keywords = rules.get("keywords", [])
        for keyword in keywords:
            if keyword.lower() in description:
                keyword_matches += 1
        
        # Check pattern matches
        patterns = rules.get("patterns", [])
        for pattern in patterns:
            try:
                if re.search(pattern, description, re.IGNORECASE):
                    pattern_matches += 1
            except re.error:
                continue
        
        total_rules = len(keywords) + len(patterns)
        if total_rules == 0:
            return 0.0
        
        return (keyword_matches + pattern_matches) / total_rules
    
    async def get_ai_suggestions(self, description: str, amount: float = 0.0) -> List[Tuple[str, float]]:
        """Get AI-powered category suggestions for uncategorized transactions."""
        if not self.anthropic_client or not self.config["ai_settings"]["enabled"]:
            return []
        
        try:
            categories_list = list(self.config["categories"].keys())
            
            prompt = f"""
            Analyze this transaction and suggest the most appropriate category from the following options:
            {', '.join(categories_list)}
            
            Transaction: "{description}"
            Amount: ${amount:.2f}
            
            Provide up to 3 suggestions with confidence scores (0-1).
            Format: category_name:confidence_score
            
            Example response:
            Food & Dining:0.85
            Shopping:0.12
            """
            
            message = self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            
            suggestions = self._parse_ai_response(message.content[0].text)
            return suggestions[:self.config["ai_settings"]["max_suggestions"]]
        
        except Exception as e:
            print(f"Error getting AI suggestions: {e}")
            return []
    
    def _parse_ai_response(self, response: str) -> List[Tuple[str, float]]:
        """Parse AI response into category suggestions."""
        suggestions = []
        lines = response.strip().split('\n')
        
        for line in lines:
            if ':' in line:
                try:
                    category, confidence = line.split(':', 1)
                    category = category.strip()
                    confidence = float(confidence.strip())
                    
                    if category in self.config["categories"] and 0 <= confidence <= 1:
                        suggestions.append((category, confidence))
                except (ValueError, IndexError):
                    continue
        
        return sorted(suggestions, key=lambda x: x[1], reverse=True)
    
    def add_category(self, name: str, keywords: List[str], patterns: List[str] = None, color: str = "#808080") -> None:
        """Add a new category to the configuration."""
        if patterns is None:
            patterns = []
        
        self.config["categories"][name] = {
            "keywords": keywords,
            "patterns": patterns,
            "color": color
        }
        self._save_config(self.config)
        print(f"Added category: {name}")
    
    def update_category