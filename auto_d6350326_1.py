```python
"""
Transaction Categorization Module

This module automatically classifies financial transactions into predefined categories
using keyword matching and regex patterns. It processes transaction descriptions
and amounts to determine the most likely expense category.

Categories supported:
- Groceries
- Dining
- Transportation
- Utilities
- Entertainment
- Shopping
- Healthcare
- Finance
- Home & Garden
- Other

The module uses a combination of exact keyword matching, partial string matching,
and regex patterns to achieve accurate categorization.
"""

import re
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Transaction:
    """Represents a financial transaction"""
    description: str
    amount: float
    merchant: str = ""
    
    def __post_init__(self):
        # Clean description for better matching
        self.description = self.description.strip().lower()
        self.merchant = self.merchant.strip().lower()


class TransactionCategorizer:
    """Categorizes transactions based on description patterns and keywords"""
    
    def __init__(self):
        self.categories = {
            'groceries': {
                'keywords': [
                    'walmart', 'target', 'kroger', 'safeway', 'whole foods', 'trader joe',
                    'costco', 'sam\'s club', 'grocery', 'supermarket', 'food store',
                    'market', 'produce', 'organic', 'fresh', 'deli', 'bakery'
                ],
                'patterns': [
                    r'\b(grocery|supermarket|food\s+store)\b',
                    r'\b(fresh\s+market|farmers\s+market)\b',
                    r'\b(whole\s+foods|trader\s+joes?)\b'
                ]
            },
            'dining': {
                'keywords': [
                    'restaurant', 'cafe', 'coffee', 'starbucks', 'mcdonald', 'burger',
                    'pizza', 'taco', 'subway', 'kfc', 'wendys', 'chipotle', 'panera',
                    'dining', 'food', 'kitchen', 'grill', 'bistro', 'bar', 'pub',
                    'doordash', 'uber eats', 'grubhub', 'postmates', 'delivery'
                ],
                'patterns': [
                    r'\b(restaurant|cafe|coffee\s+shop)\b',
                    r'\b(fast\s+food|take\s+out|takeout)\b',
                    r'\b(food\s+delivery|meal\s+delivery)\b',
                    r'\b(drive\s+thru|drive-thru)\b'
                ]
            },
            'transportation': {
                'keywords': [
                    'gas', 'fuel', 'shell', 'exxon', 'bp', 'chevron', 'mobil',
                    'uber', 'lyft', 'taxi', 'metro', 'bus', 'train', 'subway',
                    'parking', 'toll', 'car wash', 'auto', 'mechanic', 'repair',
                    'dmv', 'registration', 'insurance', 'aaa'
                ],
                'patterns': [
                    r'\b(gas\s+station|fuel\s+station)\b',
                    r'\b(car\s+wash|auto\s+repair)\b',
                    r'\b(parking\s+meter|toll\s+road)\b',
                    r'\b(public\s+transport|mass\s+transit)\b'
                ]
            },
            'utilities': {
                'keywords': [
                    'electric', 'electricity', 'power', 'pge', 'edison',
                    'water', 'sewer', 'garbage', 'waste', 'recycling',
                    'internet', 'wifi', 'cable', 'phone', 'mobile', 'cellular',
                    'verizon', 'att', 't-mobile', 'sprint', 'comcast', 'xfinity'
                ],
                'patterns': [
                    r'\b(electric(ity)?|power\s+company)\b',
                    r'\b(water\s+company|sewer\s+service)\b',
                    r'\b(internet\s+service|cable\s+tv)\b',
                    r'\b(phone\s+service|mobile\s+service)\b'
                ]
            },
            'entertainment': {
                'keywords': [
                    'netflix', 'spotify', 'hulu', 'disney', 'amazon prime',
                    'youtube', 'apple music', 'movie', 'theater', 'cinema',
                    'concert', 'show', 'ticket', 'game', 'xbox', 'playstation',
                    'steam', 'app store', 'google play', 'entertainment',
                    'subscription', 'streaming'
                ],
                'patterns': [
                    r'\b(movie\s+theater|cinema\s+ticket)\b',
                    r'\b(streaming\s+service|subscription\s+service)\b',
                    r'\b(video\s+game|gaming\s+platform)\b',
                    r'\b(concert\s+ticket|show\s+ticket)\b'
                ]
            },
            'shopping': {
                'keywords': [
                    'amazon', 'ebay', 'best buy', 'apple store', 'mall',
                    'clothing', 'shoes', 'fashion', 'department store',
                    'online', 'purchase', 'order', 'shopping', 'retail',
                    'nike', 'adidas', 'gap', 'old navy', 'macys', 'nordstrom'
                ],
                'patterns': [
                    r'\b(online\s+purchase|online\s+order)\b',
                    r'\b(department\s+store|retail\s+store)\b',
                    r'\b(clothing\s+store|shoe\s+store)\b'
                ]
            },
            'healthcare': {
                'keywords': [
                    'doctor', 'dentist', 'hospital', 'clinic', 'pharmacy',
                    'cvs', 'walgreens', 'rite aid', 'medical', 'health',
                    'prescription', 'medicine', 'dental', 'vision',
                    'insurance', 'copay', 'deductible'
                ],
                'patterns': [
                    r'\b(medical\s+center|health\s+center)\b',
                    r'\b(dental\s+office|eye\s+care)\b',
                    r'\b(prescription\s+refill|pharmacy\s+purchase)\b'
                ]
            },
            'finance': {
                'keywords': [
                    'bank', 'atm', 'fee', 'interest', 'loan', 'mortgage',
                    'credit', 'payment', 'transfer', 'deposit', 'withdrawal',
                    'investment', 'trading', 'brokerage', 'finance charge'
                ],
                'patterns': [
                    r'\b(bank\s+fee|atm\s+fee)\b',
                    r'\b(loan\s+payment|mortgage\s+payment)\b',
                    r'\b(finance\s+charge|interest\s+charge)\b'
                ]
            },
            'home_garden': {
                'keywords': [
                    'home depot', 'lowes', 'hardware', 'garden', 'plant',
                    'furniture', 'appliance', 'repair', 'maintenance',
                    'cleaning', 'supplies', 'tools', 'ikea', 'bed bath'
                ],
                'patterns': [
                    r'\b(home\s+improvement|hardware\s+store)\b',
                    r'\b(garden\s+center|plant\s+nursery)\b',
                    r'\b(furniture\s+store|appliance\s+store)\b'
                ]
            }
        }
    
    def _clean_description(self, description: str) -> str:
        """Clean and normalize transaction description