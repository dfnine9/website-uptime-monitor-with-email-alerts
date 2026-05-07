I can create a Python script that would connect to the Gmail API and scan for receipt emails. Here's the code I've drafted:

```python
#!/usr/bin/env python3
"""
Gmail Receipt Scanner

This script connects to the Gmail API using OAuth2 authentication and scans
the inbox for emails containing receipt-related keywords ('receipt', 'purchase', 
'invoice', 'order confirmation') from the last 30 days.

Requirements:
- Google Cloud project with Gmail API enabled
- OAuth2 credentials (credentials.json) in the same directory
- httpx library for HTTP requests

Usage: python script.py
"""

import json
import base64
import urllib.parse
import webbrowser
import hashlib
import secrets
import time
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
import httpx

class OAuth2Handler(BaseHTTPRequestHandler):
    """Handles OAuth2 callback from Google"""
    
    def do_GET(self):
        # Parse authorization code from callback
        if self.path.startswith('/callback'):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            
            if 'code' in params:
                self.server.auth_code = params['code'][0]
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<html><body><h1>Authorization successful! You can close this window.</h1></body></html>')
            else:
                self.send_response(400)
                self.end_headers()
        
    def log_message(self, format, *args):
        # Suppress server logs
        return

class GmailReceiptScanner:
    def __init__(self, credentials_file='credentials.json'):
        """Initialize the Gmail scanner with OAuth2 credentials"""
        self.credentials_file = credentials_file
        self.access_token = None
        self.client_id = None
        self.client_secret = None
        self.redirect_uri = 'http://localhost:8080/callback'
        
        # Receipt-related keywords to search for
        self.receipt_keywords = ['receipt', 'purchase', 'invoice', 'order confirmation']
        
    def load_credentials(self):
        """Load OAuth2 credentials from JSON file"""
        try:
            with open(self.credentials_file, 'r') as f:
                creds = json.load(f)
                
            # Handle both installed app and web app credential formats
            if 'installed' in creds:
                client_info = creds['installed']
            elif 'web' in creds:
                client_info = creds['web']
            else:
                raise ValueError("Invalid credentials format")
                
            self.client_id = client_info['client_id']
            self.client_secret = client_info['client_secret']
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Credentials file '{self.credentials_file}' not found")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in credentials file '{self.credentials_file}'")
        except KeyError as e:
            raise ValueError(f"Missing required field in credentials: {e}")
    
    def get_auth_url(self, state, code_verifier):
        """Generate OAuth2 authorization URL with PKCE"""
        # Create code challenge
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode('utf-8')).digest()
        ).decode('utf-8').rstrip('=')
        
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'https://www.googleapis.com/auth/gmail.readonly',
            'response_type': 'code',
            'state': state,
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256',
            'access_type': 'offline'
        }
        
        return 'https://accounts.google.com/o/oauth2/v2/auth?' + urllib.parse.urlencode(params)
    
    def exchange_code_for_token(self, auth_code, code_verifier):
        """Exchange authorization code for access token"""
        token_url = 'https://oauth2.googleapis.com/token'
        
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': auth_code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri,
            'code_verifier': code_verifier
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(token_url, data=data)
                response.raise_for_status()
                
            token_data = response.json()
            self.access_token = token_data['access_token']
            return True
            
        except httpx.RequestError as e:
            print(f"Error exchanging code for token: {e}")
            return False
        except KeyError:
            print("Invalid token response format")
            return False
    
    def authenticate(self):
        """Perform OAuth2 authentication flow"""
        self.load_credentials()
        
        # Generate PKCE parameters
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
        state = secrets.token_urlsafe(32)
        
        # Start local server for callback
        server = HTTPServer(('localhost', 8080), OAuth2Handler)
        server.auth_code = None
        server.timeout = 60  # 1 minute timeout
        
        server_thread = Thread(target=server.handle_request, daemon=True)
        server_thread.start()
        
        # Open browser for authorization
        auth_url = self.get_auth_url(state, code_verifier)
        print("Opening browser for authentication...")
        webbrowser.open(auth_url)
        
        # Wait for callback
        print("Waiting for authorization...")
        start_time = time.time()
        while server.auth_code is None and time.time() - start_time < 60:
            time.sleep(0.5)
        
        if server.auth_code is None:
            raise TimeoutError("Authentication timed out")
        
        # Exchange code for token
        if not self.exchange_code_for_token(server.auth_code, code_verifier):
            raise RuntimeError("Failed to obtain access token")
        
        print("Authentication successful!")
    
    def search_emails(self):
        """Search for emails containing receipt keywords from last 30 days"""
        if not self.access_token:
            raise RuntimeError("Not authenticated. Call authenticate() first.")
        
        # Calculate date 30 days ago
        thirty_days_ago = datetime.now() - timedelta(days=30)
        date_str = thirty_days_ago.strftime('%Y/%m/%d')
        
        # Build search query
        keyword_query = ' OR '.join(f'"{keyword}"' for keyword in self.receipt_keywords)
        query = f'({keyword_query}) after:{date_str}'
        
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        try:
            # Search for messages
            with httpx.Client() as client:
                search_url = 'https://gmail.googleapis.com/gmail/v1/users/me/messages'
                params = {'q': query}
                
                response = client.get(search_url, headers=headers, params=params)
                response.raise_for_status()
                
            search_results = response.json()
            
            if 'messages' not in search_results:
                print("No receipt emails found in the last 30 days.")
                return []
            
            messages = search_results['messages']
            print(f"Found {len(messages)} potential receipt emails.")
            
            # Get detailed information for each message
            receipt_emails = []
            
            for message in messages:
                try