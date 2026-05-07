```python
"""
Expense Categorization Configuration System

This module provides a comprehensive configuration file system for customizing
expense categorization rules. Users can:
- Define custom expense categories with associated keywords and patterns
- Add new keywords to existing categories
- Modify categorization rules through JSON configuration
- Apply regex patterns for advanced expense matching

The system uses JSON for configuration storage and provides methods to load,
modify, and save categorization rules. It includes validation and error handling
to ensure configuration integrity.
"""

import json
import re
import os
from typing import Dict, List, Any, Optional
from datetime import datetime


class ExpenseCategorizer:
    def __init__(self, config_file: str = "expense_config.json"):
        self.config_file = config_file
        self.config = self._load_default_config()
        self._load_config()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default categorization configuration."""
        return {
            "categories": {
                "food": {
                    "keywords": ["restaurant", "grocery", "coffee", "lunch", "dinner", "cafe"],
                    "patterns": [r"\b(pizza|burger|sandwich)\b", r"\bfood\s+delivery\b"],
                    "description": "Food and dining expenses"
                },
                "transportation": {
                    "keywords": ["uber", "taxi", "gas", "fuel", "parking", "metro", "bus"],
                    "patterns": [r"\bgas\s+station\b", r"\btransit\s+fare\b"],
                    "description": "Transportation and travel expenses"
                },
                "utilities": {
                    "keywords": ["electric", "water", "internet", "phone", "cable"],
                    "patterns": [r"\b(electricity|utility)\s+bill\b"],
                    "description": "Utility and service bills"
                },
                "entertainment": {
                    "keywords": ["movie", "theater", "concert", "netflix", "spotify"],
                    "patterns": [r"\bentertainment\b", r"\bstreaming\s+service\b"],
                    "description": "Entertainment and leisure expenses"
                },
                "shopping": {
                    "keywords": ["amazon", "store", "retail", "purchase", "buy"],
                    "patterns": [r"\bonline\s+purchase\b", r"\bretail\s+store\b"],
                    "description": "General shopping and purchases"
                }
            },
            "rules": {
                "case_sensitive": False,
                "priority_order": ["food", "transportation", "utilities", "entertainment", "shopping"],
                "default_category": "other",
                "min_confidence": 0.6
            },
            "metadata": {
                "version": "1.0",
                "created": datetime.now().isoformat(),
                "last_modified": datetime.now().isoformat()
            }
        }
    
    def _load_config(self) -> None:
        """Load configuration from file if it exists."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
                    print(f"Configuration loaded from {self.config_file}")
            else:
                print(f"No existing config found. Using default configuration.")
                self._save_config()
        except Exception as e:
            print(f"Error loading configuration: {e}")
            print("Using default configuration.")
    
    def _save_config(self) -> None:
        """Save current configuration to file."""
        try:
            self.config["metadata"]["last_modified"] = datetime.now().isoformat()
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print(f"Configuration saved to {self.config_file}")
        except Exception as e:
            print(f"Error saving configuration: {e}")
    
    def add_category(self, category_name: str, keywords: List[str], 
                    patterns: Optional[List[str]] = None, 
                    description: str = "") -> bool:
        """Add a new expense category."""
        try:
            if category_name.lower() in self.config["categories"]:
                print(f"Category '{category_name}' already exists. Use update_category() to modify.")
                return False
            
            self.config["categories"][category_name.lower()] = {
                "keywords": [kw.lower() for kw in keywords] if not self.config["rules"]["case_sensitive"] else keywords,
                "patterns": patterns or [],
                "description": description
            }
            
            # Add to priority order if not present
            if category_name.lower() not in self.config["rules"]["priority_order"]:
                self.config["rules"]["priority_order"].append(category_name.lower())
            
            self._save_config()
            print(f"Category '{category_name}' added successfully.")
            return True
            
        except Exception as e:
            print(f"Error adding category '{category_name}': {e}")
            return False
    
    def update_category(self, category_name: str, 
                       new_keywords: Optional[List[str]] = None,
                       new_patterns: Optional[List[str]] = None,
                       new_description: Optional[str] = None) -> bool:
        """Update an existing category."""
        try:
            category_key = category_name.lower()
            if category_key not in self.config["categories"]:
                print(f"Category '{category_name}' not found.")
                return False
            
            category = self.config["categories"][category_key]
            
            if new_keywords is not None:
                processed_keywords = [kw.lower() for kw in new_keywords] if not self.config["rules"]["case_sensitive"] else new_keywords
                category["keywords"] = processed_keywords
            
            if new_patterns is not None:
                category["patterns"] = new_patterns
            
            if new_description is not None:
                category["description"] = new_description
            
            self._save_config()
            print(f"Category '{category_name}' updated successfully.")
            return True
            
        except Exception as e:
            print(f"Error updating category '{category_name}': {e}")
            return False
    
    def add_keywords_to_category(self, category_name: str, keywords: List[str]) -> bool:
        """Add keywords to an existing category."""
        try:
            category_key = category_name.lower()
            if category_key not in self.config["categories"]:
                print(f"Category '{category_name}' not found.")
                return False
            
            existing_keywords = set(self.config["categories"][category_key]["keywords"])
            processed_keywords = [kw.lower() for kw in keywords] if not self.config["rules"]["case_sensitive"] else keywords
            
            for keyword in processed_keywords:
                existing_keywords.add(keyword)
            
            self.config["categories"][category_key]["keywords"] = list(existing_keywords)
            self._save_config()
            print(f"Added {len(keywords)} keywords to category '{category_name}'.")
            return True
            
        except Exception as e:
            print(f"Error adding keywords to category '{category_name}': {e}")
            return False
    
    def remove_category(self, category_name: str) -> bool:
        """Remove a category."""
        try:
            category_key = category_name.lower()
            if category_key not in self.config["categories"]:
                print(f"Category '{category_name}' not found.")
                return False
            
            del self.config["categories"][category_key]
            
            # Remove from priority order
            if category_key in self.config["rules"]["priority_order"]:
                self.config["rules"]["priority_order"].remove(category_key)
            
            self._save_config()
            print(f"Category '{category_name}' removed successfully.")
            return True
            
        except Exception as e:
            print(f"Error removing category '{category_name}':