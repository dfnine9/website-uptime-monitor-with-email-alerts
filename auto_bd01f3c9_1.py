```python
#!/usr/bin/env python3
"""
Transaction Categorization Module

This module provides automated categorization of financial transactions using keyword 
matching and regex patterns. It classifies expenses into predefined categories such as 
groceries, dining, transportation, utilities, and entertainment with confidence scoring.

The categorizer uses a multi-layered approach:
1. Exact keyword matching for high-confidence categorization
2. Regex pattern matching for flexible text analysis
3. Confidence scoring based on match quality and specificity
4. Fallback to 'Other' category for unmatched transactions

Categories supported:
- Groceries: Supermarkets, grocery stores, food markets
- Dining: Restaurants, cafes, food delivery, bars
- Transportation: Gas, public transit, rideshare, parking
- Utilities: Electric, gas, water, internet, phone bills
- Entertainment: Movies, streaming, games, events
- Shopping: Retail stores, online shopping, clothing
- Healthcare: Medical, pharmacy, dental, insurance
- Other: Unclassified transactions
"""

import re
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Transaction:
    """Represents a financial transaction."""
    description: str
    amount: float
    merchant: Optional[str] = None
    
    
@dataclass
class CategoryMatch:
    """Represents a category match result."""
    category: str
    confidence: float
    matched_keywords: List[str]
    pattern_matches: List[str]


class TransactionCategorizer:
    """
    Automated transaction categorizer using keyword and pattern matching.
    """
    
    def __init__(self):
        """Initialize the categorizer with predefined rules."""
        self.categories = {
            'Groceries': {
                'keywords': [
                    'grocery', 'supermarket', 'market', 'food store', 'walmart', 'target',
                    'kroger', 'safeway', 'publix', 'whole foods', 'trader joe', 'costco',
                    'sam\'s club', 'aldi', 'wegmans', 'harris teeter', 'food lion',
                    'giant eagle', 'stop & shop', 'king soopers', 'fred meyer'
                ],
                'patterns': [
                    r'\b(grocery|market|food)\s+(store|shop|mart)\b',
                    r'\b(super|hyper)market\b',
                    r'\b(organic|natural)\s+foods?\b'
                ]
            },
            'Dining': {
                'keywords': [
                    'restaurant', 'cafe', 'coffee', 'pizza', 'burger', 'taco', 'sushi',
                    'chinese', 'italian', 'mexican', 'thai', 'indian', 'fast food',
                    'mcdonald', 'burger king', 'subway', 'kfc', 'taco bell', 'domino',
                    'starbucks', 'dunkin', 'chipotle', 'panda express', 'olive garden',
                    'applebee', 'chili\'s', 'outback', 'red lobster', 'bar', 'pub',
                    'bistro', 'grill', 'diner', 'bakery', 'doordash', 'uber eats',
                    'grubhub', 'postmates', 'seamless'
                ],
                'patterns': [
                    r'\b(restaurant|cafe|bistro|diner|grill)\b',
                    r'\b(pizza|burger|taco|sushi|coffee)\s+(hut|king|bell|shop|bar)?\b',
                    r'\b(food\s+delivery|takeout|take\s+out)\b',
                    r'\b\w+\s+(bar|pub|grill|kitchen|cafe)\b'
                ]
            },
            'Transportation': {
                'keywords': [
                    'gas', 'gasoline', 'fuel', 'shell', 'exxon', 'bp', 'chevron',
                    'mobil', 'texaco', 'citgo', 'sunoco', 'parking', 'toll',
                    'uber', 'lyft', 'taxi', 'cab', 'metro', 'bus', 'train',
                    'subway', 'transit', 'mta', 'bart', 'caltrain', 'amtrak',
                    'airline', 'flight', 'airport', 'car rental', 'hertz', 'avis',
                    'enterprise', 'budget', 'alamo', 'national'
                ],
                'patterns': [
                    r'\b(gas|fuel)\s+(station|pump)\b',
                    r'\b(parking|toll|fare)\b',
                    r'\b(uber|lyft|taxi|cab)\b',
                    r'\b(metro|bus|train|transit)\b',
                    r'\b(car\s+rental|rent\s+a\s+car)\b'
                ]
            },
            'Utilities': {
                'keywords': [
                    'electric', 'electricity', 'gas bill', 'water', 'sewer',
                    'internet', 'cable', 'phone', 'mobile', 'wireless',
                    'verizon', 'att', 'tmobile', 'sprint', 'comcast', 'xfinity',
                    'spectrum', 'cox', 'optimum', 'fios', 'dish', 'directv',
                    'utility', 'pge', 'sce', 'sdge', 'con ed', 'duke energy',
                    'florida power', 'georgia power', 'commonwealth edison'
                ],
                'patterns': [
                    r'\b(electric|electricity|power)\s+(company|corp|co\.?)\b',
                    r'\b(gas|water|sewer)\s+(company|utility|bill)\b',
                    r'\b(internet|cable|phone|wireless)\s+(service|provider|bill)\b',
                    r'\butility\s+(bill|payment|company)\b'
                ]
            },
            'Entertainment': {
                'keywords': [
                    'movie', 'cinema', 'theater', 'netflix', 'hulu', 'disney',
                    'amazon prime', 'spotify', 'apple music', 'youtube',
                    'gaming', 'xbox', 'playstation', 'nintendo', 'steam',
                    'twitch', 'concert', 'show', 'event', 'ticket',
                    'amc', 'regal', 'cinemark', 'imax', 'hbo', 'showtime',
                    'paramount', 'peacock', 'discovery', 'espn'
                ],
                'patterns': [
                    r'\b(movie|cinema|theater|theatre)\b',
                    r'\b(streaming|subscription)\s+(service)?\b',
                    r'\b(gaming|game|console)\b',
                    r'\b(concert|show|event|ticket)\b',
                    r'\b(music|video)\s+(streaming|subscription)\b'
                ]
            },
            'Shopping': {
                'keywords': [
                    'amazon', 'ebay', 'etsy', 'walmart', 'target', 'best buy',
                    'home depot', 'lowe\'s', 'macy\'s', 'nordstrom', 'tj maxx',
                    'marshall\'s', 'ross', 'old navy', 'gap', 'banana republic',
                    'victoria secret', 'bath body works', 'bed bath beyond',
                    'ikea', 'pottery barn', 'williams sonoma', 'crate barrel',
                    'clothing', 'shoes', 'apparel', 'retail', 'department store',
                    'online shopping', 'paypal', 'apple store', 'google play'
                ],
                'patterns': [
                    r'\b(online|internet)\s+shopping\b',
                    r'\b(retail|department)\s+store\b',
                    r'\b(clothing|apparel|shoes|fashion)\b',
                    r'\b(home|furniture|decor