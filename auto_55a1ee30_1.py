```python
"""
Email Receipt Text Extraction Module

This module extracts purchase information (amounts, merchant names, dates) from email content
using regex patterns and basic NLP techniques. Designed to handle common receipt formats
from major retailers like Amazon, Target, Walmart, etc.

Features:
- Purchase amount extraction with currency symbols
- Merchant name identification from common retailers
- Date extraction in multiple formats
- Self-contained with minimal dependencies
- Robust error handling for malformed content

Usage:
    python script.py
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import sys


class ReceiptExtractor:
    def __init__(self):
        # Common merchant patterns
        self.merchant_patterns = {
            'amazon': r'(?i)amazon(?:\.com)?',
            'target': r'(?i)target(?:\.com)?',
            'walmart': r'(?i)walmart(?:\.com)?',
            'bestbuy': r'(?i)best\s?buy',
            'homedepot': r'(?i)home\s?depot',
            'costco': r'(?i)costco',
            'ebay': r'(?i)ebay',
            'paypal': r'(?i)paypal',
            'apple': r'(?i)apple(?:\s+store)?',
            'google': r'(?i)google(?:\s+play)?',
            'microsoft': r'(?i)microsoft',
            'netflix': r'(?i)netflix',
            'spotify': r'(?i)spotify',
            'uber': r'(?i)uber',
            'lyft': r'(?i)lyft',
            'doordash': r'(?i)doordash',
            'grubhub': r'(?i)grubhub'
        }
        
        # Amount patterns - various currency formats
        self.amount_patterns = [
            r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # $123.45, $1,234.56
            r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*USD',  # 123.45 USD
            r'Total:?\s*\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # Total: $123.45
            r'Amount:?\s*\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # Amount: $123.45
            r'Charged:?\s*\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # Charged: $123.45
            r'Price:?\s*\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # Price: $123.45
        ]
        
        # Date patterns
        self.date_patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})',  # MM/DD/YYYY or MM-DD-YYYY
            r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',  # YYYY/MM/DD or YYYY-MM-DD
            r'(\w+\s+\d{1,2},?\s+\d{4})',      # January 15, 2024 or Jan 15 2024
            r'(\d{1,2}\s+\w+\s+\d{4})',       # 15 January 2024
            r'(\w+\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4})',  # January 15th, 2024
        ]

    def extract_amounts(self, text: str) -> List[float]:
        """Extract purchase amounts from text."""
        amounts = []
        try:
            for pattern in self.amount_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    # Clean and convert to float
                    clean_amount = match.replace(',', '').replace('$', '').strip()
                    try:
                        amount = float(clean_amount)
                        if 0.01 <= amount <= 99999.99:  # Reasonable range filter
                            amounts.append(amount)
                    except ValueError:
                        continue
        except Exception as e:
            print(f"Error extracting amounts: {e}", file=sys.stderr)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_amounts = []
        for amount in amounts:
            if amount not in seen:
                seen.add(amount)
                unique_amounts.append(amount)
        
        return unique_amounts

    def extract_merchants(self, text: str) -> List[str]:
        """Extract merchant names from text."""
        merchants = []
        try:
            for merchant_name, pattern in self.merchant_patterns.items():
                if re.search(pattern, text):
                    merchants.append(merchant_name.title())
            
            # Also look for common merchant indicators in subject/headers
            merchant_indicators = [
                r'(?:from|receipt from|order from)\s+([A-Z][a-zA-Z\s&]+?)(?:\s|$|<)',
                r'([A-Z][a-zA-Z\s&]+?)\s+(?:receipt|order|purchase)',
                r'Your\s+([A-Z][a-zA-Z\s&]+?)\s+(?:order|purchase)',
            ]
            
            for pattern in merchant_indicators:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    clean_merchant = match.strip()
                    if 2 <= len(clean_merchant) <= 50 and clean_merchant not in merchants:
                        merchants.append(clean_merchant)
                        
        except Exception as e:
            print(f"Error extracting merchants: {e}", file=sys.stderr)
        
        return merchants[:5]  # Limit to 5 most likely merchants

    def extract_dates(self, text: str) -> List[str]:
        """Extract dates from text."""
        dates = []
        try:
            for pattern in self.date_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    # Try to parse and validate the date
                    try:
                        # Attempt multiple parsing formats
                        parsed_date = self._parse_date(match)
                        if parsed_date and parsed_date not in dates:
                            dates.append(parsed_date)
                    except Exception:
                        continue
        except Exception as e:
            print(f"Error extracting dates: {e}", file=sys.stderr)
        
        return dates

    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse various date formats and return standardized format."""
        date_formats = [
            '%m/%d/%Y', '%m-%d-%Y',
            '%Y/%m/%d', '%Y-%m-%d',
            '%B %d, %Y', '%B %d %Y',
            '%b %d, %Y', '%b %d %Y',
            '%d %B %Y', '%d %b %Y',
            '%B %dst, %Y', '%B %dnd, %Y', '%B %drd, %Y', '%B %dth, %Y',
        ]
        
        for fmt in date_formats:
            try:
                parsed = datetime.strptime(date_str.strip(), fmt)
                return parsed.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        return None

    def extract_receipt_info(self, email_content: str) -> Dict:
        """Extract all receipt information from email content."""
        try:
            # Clean the text
            clean_text = re.sub(r'<[^>]+>', ' ', email_content)  # Remove HTML
            clean_text = re.sub(