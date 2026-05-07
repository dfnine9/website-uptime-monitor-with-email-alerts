```python
#!/usr/bin/env python3
"""
IMAP Email Newsletter Fetcher and Parser

This script connects to an IMAP email server to fetch newsletters from the last 24 hours
and parses their content into structured data. It extracts key information like sender,
subject, content, and links from HTML emails.

Usage: python script.py

Requirements:
- Standard library modules (imaplib, email, json, html.parser, etc.)
- No external dependencies beyond standard library

The script will prompt for email credentials and return structured JSON data
containing parsed newsletter information.
"""

import imaplib
import email
import json
import re
import html
from html.parser import HTMLParser
from datetime import datetime, timedelta
from email.header import decode_header
from urllib.parse import urljoin, urlparse
import sys
import getpass


class NewsletterHTMLParser(HTMLParser):
    """HTML parser specifically designed for newsletter content extraction."""
    
    def __init__(self):
        super().__init__()
        self.text_content = []
        self.links = []
        self.current_tag = None
        self.in_body = False
        
    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        if tag == 'body':
            self.in_body = True
        elif tag == 'a' and self.in_body:
            for attr, value in attrs:
                if attr == 'href' and value:
                    self.links.append(value)
                    
    def handle_endtag(self, tag):
        if tag == 'body':
            self.in_body = False
        self.current_tag = None
        
    def handle_data(self, data):
        if self.in_body and self.current_tag not in ['script', 'style']:
            cleaned_data = data.strip()
            if cleaned_data and len(cleaned_data) > 10:  # Filter out short snippets
                self.text_content.append(cleaned_data)


def decode_email_header(header):
    """Decode email header handling various encodings."""
    try:
        decoded_parts = decode_header(header)
        decoded_string = ""
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                if encoding:
                    decoded_string += part.decode(encoding)
                else:
                    decoded_string += part.decode('utf-8', errors='ignore')
            else:
                decoded_string += part
        return decoded_string
    except Exception as e:
        print(f"Error decoding header: {e}")
        return str(header)


def extract_email_content(msg):
    """Extract and parse content from email message."""
    content_data = {
        'subject': '',
        'sender': '',
        'date': '',
        'text_content': '',
        'html_content': '',
        'links': [],
        'content_summary': ''
    }
    
    try:
        # Extract headers
        content_data['subject'] = decode_email_header(msg['subject'] or '')
        content_data['sender'] = decode_email_header(msg['from'] or '')
        content_data['date'] = msg['date'] or ''
        
        # Extract body content
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get('Content-Disposition'))
                
                if content_type == 'text/plain' and 'attachment' not in content_disposition:
                    try:
                        text_content = part.get_payload(decode=True)
                        if text_content:
                            content_data['text_content'] = text_content.decode('utf-8', errors='ignore')
                    except Exception as e:
                        print(f"Error extracting plain text: {e}")
                        
                elif content_type == 'text/html' and 'attachment' not in content_disposition:
                    try:
                        html_content = part.get_payload(decode=True)
                        if html_content:
                            html_str = html_content.decode('utf-8', errors='ignore')
                            content_data['html_content'] = html_str
                            
                            # Parse HTML for structured data
                            parser = NewsletterHTMLParser()
                            parser.feed(html_str)
                            content_data['links'] = list(set(parser.links))  # Remove duplicates
                            content_data['content_summary'] = ' '.join(parser.text_content[:5])  # First 5 text blocks
                    except Exception as e:
                        print(f"Error extracting HTML content: {e}")
        else:
            # Single part message
            try:
                content = msg.get_payload(decode=True)
                if content:
                    content_str = content.decode('utf-8', errors='ignore')
                    if msg.get_content_type() == 'text/html':
                        content_data['html_content'] = content_str
                        parser = NewsletterHTMLParser()
                        parser.feed(content_str)
                        content_data['links'] = list(set(parser.links))
                        content_data['content_summary'] = ' '.join(parser.text_content[:5])
                    else:
                        content_data['text_content'] = content_str
            except Exception as e:
                print(f"Error extracting single part content: {e}")
                
    except Exception as e:
        print(f"Error processing email content: {e}")
    
    return content_data


def connect_to_imap(server, username, password, port=993):
    """Connect to IMAP server with SSL."""
    try:
        mail = imaplib.IMAP4_SSL(server, port)
        mail.login(username, password)
        return mail
    except Exception as e:
        raise Exception(f"Failed to connect to IMAP server: {e}")


def fetch_newsletters_last_24h(mail):
    """Fetch emails from the last 24 hours that appear to be newsletters."""
    try:
        mail.select('INBOX')
        
        # Calculate date for last 24 hours
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%d-%b-%Y")
        
        # Search for emails from last 24 hours
        search_criteria = f'(SINCE "{yesterday}")'
        typ, message_numbers = mail.search(None, search_criteria)
        
        if typ != 'OK':
            raise Exception("Failed to search emails")
            
        newsletters = []
        message_ids = message_numbers[0].split()
        
        print(f"Found {len(message_ids)} emails from last 24 hours")
        
        for msg_id in message_ids:
            try:
                typ, msg_data = mail.fetch(msg_id, '(RFC822)')
                if typ != 'OK':
                    continue
                    
                email_body = msg_data[0][1]
                msg = email.message_from_bytes(email_body)
                
                # Basic newsletter detection
                subject = decode_email_header(msg['subject'] or '').lower()
                sender = decode_email_header(msg['from'] or '').lower()
                
                # Keywords that suggest newsletter content
                newsletter_keywords = [
                    'newsletter', 'digest', 'weekly', 'daily', 'update',
                    'bulletin', 'news', 'unsubscribe', 'subscription'
                ]
                
                # Check if email appears to be a newsletter
                is_newsletter = any(keyword in subject or keyword in sender 
                                  for keyword in newsletter_keywords)
                
                # Also check for HTML content (newsletters are usually HTML)
                has_html = False
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == 'text/html':
                            has_html = True
                            break
                else:
                    has_html = msg.get_content_type() == 'text/html'
                
                if is_newsletter or has_html:
                    content_data = extract_email_content(msg)
                    newsletters.append(content_data)