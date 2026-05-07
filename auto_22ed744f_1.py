```python
"""
Transaction Categorization Engine

A self-contained Python module that categorizes financial transactions using regex patterns.
Matches transaction descriptions against predefined categories (groceries, gas, dining, utilities, etc.)
with fallback rules and confidence scoring.

Features:
- Regex-based pattern matching for common transaction types
- Confidence scoring based on pattern specificity
- Fallback categorization for unmatched transactions
- Extensible category definitions
- Error handling for malformed inputs

Usage:
    python script.py

The script includes sample transactions for demonstration.
"""

import re
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict


@dataclass
class CategoryMatch:
    """Represents a category match with confidence score."""
    category: str
    confidence: float
    matched_pattern: str
    description: str


class TransactionCategorizer:
    """Categorizes transactions using regex patterns with confidence scoring."""
    
    def __init__(self):
        """Initialize the categorizer with predefined patterns."""
        self.categories = {
            'groceries': {
                'patterns': [
                    r'(?i)\b(walmart|target|kroger|safeway|albertsons|publix)\b',
                    r'(?i)\b(whole foods|trader joe|aldi|costco|sam\'s club)\b',
                    r'(?i)\b(grocery|supermarket|market|food store)\b',
                    r'(?i)\b(produce|dairy|deli|bakery)\b'
                ],
                'confidence_base': 0.9
            },
            'gas': {
                'patterns': [
                    r'(?i)\b(shell|exxon|bp|chevron|mobil|texaco|arco)\b',
                    r'(?i)\b(gas station|fuel|gasoline|petrol)\b',
                    r'(?i)\b(pump #\d+|fuel stop)\b'
                ],
                'confidence_base': 0.95
            },
            'dining': {
                'patterns': [
                    r'(?i)\b(mcdonald|burger king|subway|kfc|taco bell|pizza hut)\b',
                    r'(?i)\b(restaurant|cafe|diner|bistro|grill|bar)\b',
                    r'(?i)\b(starbucks|dunkin|coffee|doordash|ubereats|grubhub)\b',
                    r'(?i)\b(pizza|chinese|thai|mexican|italian)\b'
                ],
                'confidence_base': 0.85
            },
            'utilities': {
                'patterns': [
                    r'(?i)\b(electric|electricity|power|pge|edison)\b',
                    r'(?i)\b(water|sewer|waste|garbage|trash)\b',
                    r'(?i)\b(gas company|natural gas|utility)\b',
                    r'(?i)\b(internet|cable|phone|telecom|verizon|att)\b'
                ],
                'confidence_base': 0.9
            },
            'transportation': {
                'patterns': [
                    r'(?i)\b(uber|lyft|taxi|cab)\b',
                    r'(?i)\b(metro|bus|transit|train|subway)\b',
                    r'(?i)\b(parking|toll|bridge fee)\b',
                    r'(?i)\b(car rental|hertz|enterprise|budget)\b'
                ],
                'confidence_base': 0.88
            },
            'shopping': {
                'patterns': [
                    r'(?i)\b(amazon|ebay|etsy|paypal)\b',
                    r'(?i)\b(best buy|home depot|lowes|ikea)\b',
                    r'(?i)\b(clothing|apparel|shoes|fashion)\b',
                    r'(?i)\b(department store|mall|outlet)\b'
                ],
                'confidence_base': 0.8
            },
            'healthcare': {
                'patterns': [
                    r'(?i)\b(pharmacy|cvs|walgreens|rite aid)\b',
                    r'(?i)\b(doctor|clinic|hospital|medical)\b',
                    r'(?i)\b(dentist|dental|orthodontist)\b',
                    r'(?i)\b(prescription|rx|medicine)\b'
                ],
                'confidence_base': 0.92
            },
            'entertainment': {
                'patterns': [
                    r'(?i)\b(netflix|spotify|hulu|disney|amazon prime)\b',
                    r'(?i)\b(movie|cinema|theater|tickets)\b',
                    r'(?i)\b(gym|fitness|sports|recreation)\b',
                    r'(?i)\b(gaming|xbox|playstation|steam)\b'
                ],
                'confidence_base': 0.85
            },
            'banking': {
                'patterns': [
                    r'(?i)\b(atm|withdrawal|deposit|transfer)\b',
                    r'(?i)\b(bank|credit union|fee|charge)\b',
                    r'(?i)\b(interest|dividend|payment)\b'
                ],
                'confidence_base': 0.9
            }
        }
        
        self.fallback_patterns = {
            'unknown_retail': {
                'pattern': r'(?i)\b(store|shop|retail|purchase|buy)\b',
                'confidence': 0.3
            },
            'unknown_service': {
                'pattern': r'(?i)\b(service|fee|charge|payment)\b',
                'confidence': 0.25
            },
            'unknown_online': {
                'pattern': r'(?i)\b(www\.|\.com|online|digital)\b',
                'confidence': 0.35
            }
        }

    def categorize_transaction(self, description: str, amount: Optional[float] = None) -> CategoryMatch:
        """
        Categorize a single transaction description.
        
        Args:
            description: Transaction description text
            amount: Transaction amount (optional, for future enhancement)
            
        Returns:
            CategoryMatch object with category, confidence, and matched pattern
        """
        try:
            if not description or not isinstance(description, str):
                return CategoryMatch('uncategorized', 0.0, 'empty_description', description or '')
            
            description = description.strip()
            best_match = None
            highest_confidence = 0.0
            
            # Check main categories
            for category, config in self.categories.items():
                for pattern in config['patterns']:
                    match = re.search(pattern, description)
                    if match:
                        # Calculate confidence based on match specificity
                        match_length = len(match.group(0))
                        description_length = len(description)
                        specificity_bonus = min(0.1, match_length / description_length)
                        confidence = config['confidence_base'] + specificity_bonus
                        
                        if confidence > highest_confidence:
                            highest_confidence = confidence
                            best_match = CategoryMatch(
                                category=category,
                                confidence=confidence,
                                matched_pattern=pattern,
                                description=description
                            )
            
            # If no main category match, try fallback patterns
            if not best_match:
                for fallback_name, fallback_config in self.fallback_patterns.items():
                    match = re.search(fallback_config['pattern'], description)
                    if match:
                        confidence = fallback_config['confidence']
                        if confidence > highest_confidence:
                            highest_confidence = confidence
                            best_match = CategoryMatch(
                                category=fallback_name.replace('unknown_', ''),
                                confidence=confidence,
                                matched_pattern=fallback_config['pattern'],
                                description=description
                            )
            
            # Final fallback for completely unmatched transactions
            if not best_match:
                best_match = CategoryMatch(
                    category='uncategorized',
                    confidence=0.1,
                    matched_pattern='no_match',
                    description=description
                )
                
            return best_match
            
        except Exception as e:
            print(f"Error categorizing transaction '{description}':