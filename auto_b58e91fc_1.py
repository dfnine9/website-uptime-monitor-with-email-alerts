"""
GitHub Repository Analysis Tool

This module provides comprehensive analysis of GitHub repositories by evaluating:
- README quality (length, sections, formatting)
- License presence and type detection
- Commit frequency patterns and trends
- Issue response time metrics and patterns

The tool uses GitHub's REST API to gather repository data and performs
statistical analysis to provide insights into repository health and maintenance.

Usage: python script.py
"""

import json
import re
import statistics
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin

try:
    import httpx
except ImportError:
    print("Error: httpx library required. Install with: pip install httpx")
    sys.exit(1)


class GitHubAnalyzer:
    """Main analyzer class for GitHub repository evaluation."""
    
    def __init__(self, token: Optional[str] = None):
        """Initialize analyzer with optional GitHub token for higher rate limits."""
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitHub-Analyzer/1.0"
        }
        if token:
            self.headers["Authorization"] = f"token {token}"
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make HTTP request to GitHub API with error handling."""
        try:
            url = urljoin(self.base_url, endpoint)
            with httpx.Client() as client:
                response = client.get(url, headers=self.headers, params=params or {})
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            print(f"HTTP error occurred: {e}")
            return None
        except Exception as e:
            print(f"Request error: {e}")
            return None


class ReadmeAnalyzer:
    """Analyzes README file quality and content."""
    
    QUALITY_SECTIONS = [
        'installation', 'usage', 'examples', 'documentation',
        'contributing', 'license', 'changelog', 'api', 'features'
    ]
    
    @staticmethod
    def analyze_readme(content: str) -> Dict:
        """Analyze README content for quality metrics."""
        try:
            if not content:
                return {"score": 0, "issues": ["README is empty"], "sections_found": []}
            
            content_lower = content.lower()
            lines = content.split('\n')
            
            # Basic metrics
            char_count = len(content)
            word_count = len(content.split())
            line_count = len(lines)
            
            # Section detection
            sections_found = []
            for section in ReadmeAnalyzer.QUALITY_SECTIONS:
                if section in content_lower:
                    sections_found.append(section)
            
            # Quality indicators
            has_headers = bool(re.search(r'^#{1,6}\s', content, re.MULTILINE))
            has_code_blocks = bool(re.search(r'