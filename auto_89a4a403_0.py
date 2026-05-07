```python
#!/usr/bin/env python3
"""
GitHub Repository Data Fetcher

This module connects to the GitHub API to fetch comprehensive repository data including:
- Basic repository information (name, description, stars, forks)
- Commit statistics and recent commits
- Issues (open/closed counts and recent issues)
- Pull requests (open/closed/merged counts and recent PRs)
- README file presence detection
- Recent activity metrics (last commit, last issue, last PR)

The script fetches data for a specified repository and outputs structured JSON data
containing all the gathered information with proper error handling.

Dependencies: httpx (for HTTP requests)
Usage: python script.py
"""

import json
import sys
from datetime import datetime, timedelta
from urllib.parse import urljoin
from typing import Dict, List, Optional, Any
import httpx


class GitHubAPIClient:
    """GitHub API client for fetching repository data."""
    
    def __init__(self, token: Optional[str] = None):
        """Initialize the GitHub API client."""
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitHub-Repo-Analyzer/1.0"
        }
        if token:
            self.headers["Authorization"] = f"token {token}"
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make a request to the GitHub API with error handling."""
        try:
            url = urljoin(self.base_url, endpoint)
            with httpx.Client(timeout=30.0) as client:
                response = client.get(url, headers=self.headers, params=params or {})
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    print(f"Resource not found: {endpoint}", file=sys.stderr)
                    return None
                elif response.status_code == 403:
                    print(f"Rate limit exceeded or access forbidden: {endpoint}", file=sys.stderr)
                    return None
                else:
                    print(f"API request failed with status {response.status_code}: {endpoint}", file=sys.stderr)
                    return None
                    
        except httpx.TimeoutException:
            print(f"Request timeout for endpoint: {endpoint}", file=sys.stderr)
            return None
        except httpx.RequestError as e:
            print(f"Request error for {endpoint}: {str(e)}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"Unexpected error for {endpoint}: {str(e)}", file=sys.stderr)
            return None
    
    def get_repository_info(self, owner: str, repo: str) -> Optional[Dict]:
        """Fetch basic repository information."""
        return self._make_request(f"/repos/{owner}/{repo}")
    
    def get_commits(self, owner: str, repo: str, limit: int = 10) -> List[Dict]:
        """Fetch recent commits."""
        params = {"per_page": limit, "page": 1}
        commits = self._make_request(f"/repos/{owner}/{repo}/commits", params)
        return commits if commits else []
    
    def get_issues(self, owner: str, repo: str, state: str = "all", limit: int = 10) -> List[Dict]:
        """Fetch repository issues."""
        params = {"state": state, "per_page": limit, "page": 1}
        issues = self._make_request(f"/repos/{owner}/{repo}/issues", params)
        return issues if issues else []
    
    def get_pull_requests(self, owner: str, repo: str, state: str = "all", limit: int = 10) -> List[Dict]:
        """Fetch repository pull requests."""
        params = {"state": state, "per_page": limit, "page": 1}
        prs = self._make_request(f"/repos/{owner}/{repo}/pulls", params)
        return prs if prs else []
    
    def check_readme(self, owner: str, repo: str) -> bool:
        """Check if repository has a README file."""
        readme_files = ["README.md", "README.rst", "README.txt", "README"]
        
        for filename in readme_files:
            result = self._make_request(f"/repos/{owner}/{repo}/contents/{filename}")
            if result:
                return True
        return False


class GitHubDataAnalyzer:
    """Analyzer for processing and structuring GitHub repository data."""
    
    def __init__(self):
        self.client = GitHubAPIClient()
    
    def analyze_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """Perform comprehensive analysis of a GitHub repository."""
        print(f"Analyzing repository: {owner}/{repo}", file=sys.stderr)
        
        analysis_result = {
            "repository": f"{owner}/{repo}",
            "analyzed_at": datetime.now().isoformat(),
            "basic_info": {},
            "commits": {},
            "issues": {},
            "pull_requests": {},
            "readme_present": False,
            "activity_metrics": {},
            "errors": []
        }
        
        try:
            # Fetch basic repository information
            repo_info = self.client.get_repository_info(owner, repo)
            if repo_info:
                analysis_result["basic_info"] = {
                    "name": repo_info.get("name"),
                    "full_name": repo_info.get("full_name"),
                    "description": repo_info.get("description"),
                    "stars": repo_info.get("stargazers_count", 0),
                    "forks": repo_info.get("forks_count", 0),
                    "watchers": repo_info.get("watchers_count", 0),
                    "language": repo_info.get("language"),
                    "created_at": repo_info.get("created_at"),
                    "updated_at": repo_info.get("updated_at"),
                    "size": repo_info.get("size", 0),
                    "open_issues_count": repo_info.get("open_issues_count", 0)
                }
            else:
                analysis_result["errors"].append("Failed to fetch basic repository information")
            
            # Fetch and analyze commits
            commits = self.client.get_commits(owner, repo, limit=50)
            analysis_result["commits"] = self._analyze_commits(commits)
            
            # Fetch and analyze issues
            issues = self.client.get_issues(owner, repo, state="all", limit=50)
            analysis_result["issues"] = self._analyze_issues(issues)
            
            # Fetch and analyze pull requests
            prs = self.client.get_pull_requests(owner, repo, state="all", limit=50)
            analysis_result["pull_requests"] = self._analyze_pull_requests(prs)
            
            # Check README presence
            analysis_result["readme_present"] = self.client.check_readme(owner, repo)
            
            # Calculate activity metrics
            analysis_result["activity_metrics"] = self._calculate_activity_metrics(
                commits, issues, prs
            )
            
        except Exception as e:
            error_msg = f"Unexpected error during analysis: {str(e)}"
            analysis_result["errors"].append(error_msg)
            print(error_msg, file=sys.stderr)
        
        return analysis_result
    
    def _analyze_commits(self, commits: List[Dict]) -> Dict[str, Any]:
        """Analyze commit data."""
        if not commits:
            return {"total_fetched": 0, "recent_commits": [], "commit_frequency": {}}
        
        commit_analysis = {
            "total_fetched": len(commits),
            "recent_commits": [],
            "commit_frequency": {}
        }
        
        # Process recent commits
        for commit in commits[:10]:
            commit_data = {
                "sha": commit.get("sha"),
                "message": commit.get("commit", {}).get("message"),
                "author": commit.get("commit