#!/usr/bin/env python3
"""
GitHub Repository Health Analyzer

This script connects to the GitHub API to fetch comprehensive repository metadata
and calculates health metrics for open source projects. It analyzes:
- Basic metrics: stars, forks, watchers, size
- Activity metrics: last commit date, open/closed issues and PRs
- Documentation quality: README completeness score
- Community health: contributor count and activity patterns

The script outputs a structured health report with calculated scores to help
assess repository quality and maintenance status.

Usage: python script.py
Dependencies: httpx (for HTTP requests)
"""

import json
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import urllib.request
import urllib.parse
import urllib.error
import re


class GitHubAnalyzer:
    """Analyzes GitHub repository health metrics."""
    
    def __init__(self, token: Optional[str] = None):
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitHub-Health-Analyzer/1.0"
        }
        if token:
            self.headers["Authorization"] = f"token {token}"
    
    def make_request(self, url: str) -> Dict[str, Any]:
        """Make HTTP request to GitHub API with error handling."""
        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise ValueError(f"Repository not found: {url}")
            elif e.code == 403:
                raise ValueError("API rate limit exceeded or access forbidden")
            else:
                raise ValueError(f"HTTP error {e.code}: {e.reason}")
        except Exception as e:
            raise ValueError(f"Request failed: {str(e)}")
    
    def get_repository_metadata(self, owner: str, repo: str) -> Dict[str, Any]:
        """Fetch basic repository metadata."""
        url = f"{self.base_url}/repos/{owner}/{repo}"
        return self.make_request(url)
    
    def get_contributors(self, owner: str, repo: str) -> list:
        """Fetch repository contributors."""
        url = f"{self.base_url}/repos/{owner}/{repo}/contributors"
        try:
            return self.make_request(url)
        except ValueError:
            return []
    
    def get_issues_and_prs(self, owner: str, repo: str) -> Dict[str, int]:
        """Fetch issues and pull requests statistics."""
        metrics = {
            "open_issues": 0,
            "closed_issues": 0,
            "open_prs": 0,
            "closed_prs": 0
        }
        
        # Get open issues (includes PRs in GitHub API)
        try:
            url = f"{self.base_url}/repos/{owner}/{repo}/issues?state=open&per_page=100"
            open_items = self.make_request(url)
            
            for item in open_items:
                if "pull_request" in item:
                    metrics["open_prs"] += 1
                else:
                    metrics["open_issues"] += 1
        except ValueError:
            pass
        
        # Get closed issues (sample)
        try:
            url = f"{self.base_url}/repos/{owner}/{repo}/issues?state=closed&per_page=100"
            closed_items = self.make_request(url)
            
            for item in closed_items:
                if "pull_request" in item:
                    metrics["closed_prs"] += 1
                else:
                    metrics["closed_issues"] += 1
        except ValueError:
            pass
        
        return metrics
    
    def get_readme_content(self, owner: str, repo: str) -> str:
        """Fetch README content."""
        readme_files = ["README.md", "README.rst", "README.txt", "README"]
        
        for filename in readme_files:
            try:
                url = f"{self.base_url}/repos/{owner}/{repo}/contents/{filename}"
                content_data = self.make_request(url)
                
                if content_data.get("encoding") == "base64":
                    import base64
                    content = base64.b64decode(content_data["content"]).decode()
                    return content
            except ValueError:
                continue
        
        return ""
    
    def analyze_readme_completeness(self, readme_content: str) -> Dict[str, Any]:
        """Analyze README completeness and return score."""
        if not readme_content:
            return {"score": 0, "details": "No README found"}
        
        score = 0
        details = []
        
        # Check for essential sections
        sections = {
            "title": r"#\s*\w+",
            "description": r"(description|about|overview)",
            "installation": r"(install|setup|getting started)",
            "usage": r"(usage|example|how to)",
            "contributing": r"contribut",
            "license": r"license",
            "badges": r"!\[.*\]\(.*\)",
        }
        
        content_lower = readme_content.lower()
        
        for section, pattern in sections.items():
            if re.search(pattern, content_lower):
                score += 1
                details.append(f"✓ Has {section}")
            else:
                details.append(f"✗ Missing {section}")
        
        # Bonus points for length and code examples
        if len(readme_content) > 500:
            score += 1
            details.append("✓ Adequate length")
        
        if "