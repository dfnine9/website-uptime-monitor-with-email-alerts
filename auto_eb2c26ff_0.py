```python
"""
Bank CSV Transaction Categorizer

A self-contained Python script that parses bank CSV files and automatically
categorizes transactions using keyword matching and regex patterns. Supports
multiple common CSV formats with built-in data validation.

Features:
- Parses various bank CSV formats (auto-detection)
- Transaction categorization using keywords and regex patterns
- Data validation and error handling
- Extensible categorization rules
- Detailed transaction reports

Usage: python script.py
"""

import csv
import re
import os
import sys
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field


@dataclass
class Transaction:
    """Represents a single bank transaction."""
    date: str
    description: str
    amount: float
    balance: Optional[float] = None
    category: str = "Uncategorized"
    confidence: float = 0.0


@dataclass 
class CSVFormat:
    """Defines a CSV format structure."""
    name: str
    date_col: str
    description_col: str  
    amount_col: str
    balance_col: Optional[str] = None
    header_row: int = 0
    date_formats: List[str] = field(default_factory=lambda: ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"])


class TransactionCategorizer:
    """Handles transaction categorization using keywords and regex patterns."""
    
    def __init__(self):
        self.categories = {
            "Food & Dining": {
                "keywords": ["restaurant", "pizza", "mcdonalds", "starbucks", "cafe", "diner", "food", "grocery", "supermarket"],
                "patterns": [r".*restaurant.*", r".*pizza.*", r".*grocery.*", r".*food.*"]
            },
            "Transportation": {
                "keywords": ["uber", "lyft", "taxi", "gas", "fuel", "parking", "metro", "bus"],
                "patterns": [r".*uber.*", r".*gas\s*station.*", r".*parking.*"]
            },
            "Shopping": {
                "keywords": ["amazon", "walmart", "target", "store", "shop", "mall", "retail"],
                "patterns": [r".*amazon.*", r".*shop.*", r".*store.*"]
            },
            "Bills & Utilities": {
                "keywords": ["electric", "water", "internet", "phone", "utility", "bill", "payment"],
                "patterns": [r".*electric.*", r".*utility.*", r".*bill.*"]
            },
            "Healthcare": {
                "keywords": ["doctor", "medical", "pharmacy", "hospital", "health", "dental"],
                "patterns": [r".*medical.*", r".*pharmacy.*", r".*doctor.*"]
            },
            "Entertainment": {
                "keywords": ["movie", "theater", "netflix", "spotify", "game", "entertainment"],
                "patterns": [r".*netflix.*", r".*spotify.*", r".*theater.*"]
            },
            "Banking": {
                "keywords": ["atm", "fee", "transfer", "deposit", "withdrawal", "interest"],
                "patterns": [r".*atm.*", r".*fee.*", r".*transfer.*"]
            },
            "Income": {
                "keywords": ["salary", "payroll", "deposit", "income", "wages"],
                "patterns": [r".*payroll.*", r".*salary.*", r".*wages.*"]
            }
        }
    
    def categorize(self, description: str, amount: float) -> Tuple[str, float]:
        """
        Categorize a transaction based on description and amount.
        Returns (category, confidence_score).
        """
        description_lower = description.lower().strip()
        
        # Income detection (positive amounts)
        if amount > 0:
            for keyword in self.categories["Income"]["keywords"]:
                if keyword in description_lower:
                    return "Income", 0.9
        
        best_category = "Uncategorized"
        best_confidence = 0.0
        
        for category, rules in self.categories.items():
            confidence = self._calculate_confidence(description_lower, rules)
            if confidence > best_confidence:
                best_confidence = confidence
                best_category = category
        
        return best_category, best_confidence
    
    def _calculate_confidence(self, description: str, rules: Dict) -> float:
        """Calculate confidence score for a category match."""
        confidence = 0.0
        
        # Keyword matching
        for keyword in rules["keywords"]:
            if keyword in description:
                confidence += 0.6
                break
        
        # Regex pattern matching
        for pattern in rules["patterns"]:
            if re.search(pattern, description, re.IGNORECASE):
                confidence += 0.4
                break
        
        return min(confidence, 1.0)


class BankCSVParser:
    """Parses bank CSV files with format auto-detection and validation."""
    
    def __init__(self):
        self.categorizer = TransactionCategorizer()
        self.supported_formats = [
            CSVFormat(
                name="Standard Bank Format",
                date_col="Date",
                description_col="Description", 
                amount_col="Amount",
                balance_col="Balance"
            ),
            CSVFormat(
                name="Chase Bank Format",
                date_col="Transaction Date",
                description_col="Description",
                amount_col="Amount", 
                balance_col="Running Bal."
            ),
            CSVFormat(
                name="Wells Fargo Format",
                date_col="Date",
                description_col="Description",
                amount_col="Amount",
                balance_col=None
            ),
            CSVFormat(
                name="Bank of America Format", 
                date_col="Posted Date",
                description_col="Payee",
                amount_col="Amount",
                balance_col="Running Balance"
            ),
            CSVFormat(
                name="Generic Format",
                date_col="date",
                description_col="description",
                amount_col="amount", 
                balance_col="balance"
            )
        ]
    
    def detect_format(self, filepath: str) -> Optional[CSVFormat]:
        """Auto-detect CSV format by examining headers."""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                # Try different encodings if utf-8 fails
                try:
                    sample = file.read(1024)
                    file.seek(0)
                except UnicodeDecodeError:
                    file.close()
                    with open(filepath, 'r', encoding='latin-1') as file:
                        sample = file.read(1024)
                        file.seek(0)
                
                reader = csv.reader(file)
                headers = next(reader)
                headers_lower = [h.lower().strip() for h in headers]
                
                for fmt in self.supported_formats:
                    if self._format_matches(headers_lower, fmt):
                        print(f"Detected format: {fmt.name}")
                        return fmt
                        
        except Exception as e:
            print(f"Error detecting format: {e}")
            
        return None
    
    def _format_matches(self, headers: List[str], fmt: CSVFormat) -> bool:
        """Check if headers match a specific format."""
        required_cols = [fmt.date_col.lower(), fmt.description_col.lower(), fmt.amount_col.lower()]
        
        for col in required_cols:
            if col not in headers:
                return False
        return True
    
    def validate_date(self, date_str: str, date_formats: List[str]) -> bool:
        """Validate date string against known formats."""
        for fmt in date_formats:
            try:
                datetime.strptime(date_str.strip(), fmt)
                return True
            except ValueError:
                continue
        return False
    
    def parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float, handling various formats."""
        if not amount_str or amount_str.strip() == '':
            return 0.0
            
        # Remove currency symbols and whitespace