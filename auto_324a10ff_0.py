```python
#!/usr/bin/env python3
"""
Email Transaction Extractor

This module connects to an email account via IMAP, searches for bank transaction
emails using common keywords, extracts transaction details (amount, date, merchant,
account) using regex patterns for major banks, and saves the structured data to JSON files.

The script identifies transaction emails from major banks and credit card companies,
parses key transaction details, and outputs structured JSON data for further analysis.

Usage: python script.py
"""

import imaplib
import email
import re
import json
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any
import getpass


class TransactionExtractor:
    def __init__(self):
        self.transaction_patterns = {
            'chase': {
                'amount': r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)',
                'date': r'(\d{1,2}/\d{1,2}/\d{4}|\w+ \d{1,2}, \d{4})',
                'merchant': r'(?:at|from)\s+([A-Z][A-Za-z0-9\s\-&\.]+?)(?:\s+on|\s+\$|\s*$)',
                'account': r'account\s+ending\s+in\s+(\d{4})',
            },
            'bofa': {
                'amount': r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)',
                'date': r'(\d{1,2}/\d{1,2}/\d{4})',
                'merchant': r'(?:Transaction at|Purchase at)\s+([A-Z][A-Za-z0-9\s\-&\.]+)',
                'account': r'card\s+ending\s+in\s+(\d{4})',
            },
            'wells_fargo': {
                'amount': r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)',
                'date': r'(\d{1,2}/\d{1,2}/\d{4})',
                'merchant': r'merchant:\s+([A-Z][A-Za-z0-9\s\-&\.]+)',
                'account': r'account\s+\*(\d{4})',
            },
            'citi': {
                'amount': r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)',
                'date': r'(\d{1,2}/\d{1,2}/\d{4})',
                'merchant': r'(?:at|from)\s+([A-Z][A-Za-z0-9\s\-&\.]+)',
                'account': r'card\s+ending\s+(\d{4})',
            },
            'generic': {
                'amount': r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)',
                'date': r'(\d{1,2}/\d{1,2}/\d{4}|\w+\s+\d{1,2},?\s+\d{4})',
                'merchant': r'(?:merchant|vendor|at|from)[\s:]+([A-Z][A-Za-z0-9\s\-&\.]{3,30})',
                'account': r'(?:account|card).*?(?:ending|#).*?(\d{4})',
            }
        }
        
        self.search_keywords = [
            'transaction', 'purchase', 'payment', 'charge', 'debit',
            'withdrawal', 'transfer', 'deposit', 'balance', 'statement'
        ]

    def connect_to_email(self, server: str, username: str, password: str) -> Optional[imaplib.IMAP4_SSL]:
        """Connect to IMAP server and login."""
        try:
            mail = imaplib.IMAP4_SSL(server)
            mail.login(username, password)
            return mail
        except Exception as e:
            print(f"Error connecting to email: {e}")
            return None

    def search_transaction_emails(self, mail: imaplib.IMAP4_SSL, folder: str = 'INBOX') -> List[str]:
        """Search for emails containing transaction keywords."""
        try:
            mail.select(folder)
            email_ids = []
            
            for keyword in self.search_keywords:
                try:
                    _, messages = mail.search(None, f'SUBJECT "{keyword}"')
                    email_ids.extend(messages[0].split())
                    
                    _, messages = mail.search(None, f'BODY "{keyword}"')
                    email_ids.extend(messages[0].split())
                except:
                    continue
            
            return list(set(email_ids))  # Remove duplicates
            
        except Exception as e:
            print(f"Error searching emails: {e}")
            return []

    def extract_email_content(self, mail: imaplib.IMAP4_SSL, email_id: str) -> Dict[str, Any]:
        """Extract content from a single email."""
        try:
            _, msg_data = mail.fetch(email_id, '(RFC822)')
            email_body = msg_data[0][1]
            email_message = email.message_from_bytes(email_body)
            
            content = {
                'id': email_id,
                'subject': email_message['subject'] or '',
                'from': email_message['from'] or '',
                'date': email_message['date'] or '',
                'body': ''
            }
            
            # Extract email body
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True)
                        if body:
                            content['body'] = body.decode('utf-8', errors='ignore')
                            break
            else:
                body = email_message.get_payload(decode=True)
                if body:
                    content['body'] = body.decode('utf-8', errors='ignore')
            
            return content
            
        except Exception as e:
            print(f"Error extracting email {email_id}: {e}")
            return {'id': email_id, 'error': str(e)}

    def identify_bank(self, email_content: Dict[str, Any]) -> str:
        """Identify which bank the email is from based on sender and content."""
        sender = email_content.get('from', '').lower()
        subject = email_content.get('subject', '').lower()
        body = email_content.get('body', '').lower()
        
        bank_indicators = {
            'chase': ['chase', 'jpmorgan'],
            'bofa': ['bankofamerica', 'bofa', 'bank of america'],
            'wells_fargo': ['wellsfargo', 'wells fargo'],
            'citi': ['citi', 'citibank', 'citicorp']
        }
        
        for bank, indicators in bank_indicators.items():
            for indicator in indicators:
                if indicator in sender or indicator in subject or indicator in body:
                    return bank
        
        return 'generic'

    def extract_transaction_details(self, email_content: Dict[str, Any]) -> Dict[str, Any]:
        """Extract transaction details from email content."""
        bank = self.identify_bank(email_content)
        patterns = self.transaction_patterns.get(bank, self.transaction_patterns['generic'])
        
        text = f"{email_content.get('subject', '')} {email_content.get('body', '')}"
        
        transaction = {
            'email_id': email_content['id'],
            'bank': bank,
            'sender': email_content.get('from', ''),
            'email_date': email_content.get('date', ''),
            'amount': None,
            'transaction_date': None,
            'merchant': None,
            'account': None,
            'raw_subject': email_content.get('subject', ''),
        }
        
        # Extract amount
        amount_match =