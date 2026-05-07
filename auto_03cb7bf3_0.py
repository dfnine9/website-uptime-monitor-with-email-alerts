```python
#!/usr/bin/env python3
"""
GitHub Repository Health Metrics Analyzer

This script fetches repository data via the GitHub API, analyzes file structures,
README quality, and generates standardized health metrics reports. It evaluates
repositories based on documentation quality, project structure, activity levels,
and community engagement metrics.

Dependencies: httpx, anthropic (plus standard library)
Usage: python script.py
"""

import json
import sys
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import httpx
import anthropic


class GitHubAnalyzer:
    def __init__(self, github_token: Optional[str] = None):
        self.github_token = github_token
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'GitHub-Health-Analyzer/1.0'
        }
        if github_token:
            self.headers['Authorization'] = f'token {github_token}'
        
        self.client = httpx.Client(headers=self.headers, timeout=30.0)
        
    def fetch_repo_data(self, owner: str, repo: str) -> Dict:
        """Fetch comprehensive repository data from GitHub API."""
        try:
            # Basic repo info
            repo_response = self.client.get(f'https://api.github.com/repos/{owner}/{repo}')
            repo_response.raise_for_status()
            repo_data = repo_response.json()
            
            # Repository contents
            contents_response = self.client.get(f'https://api.github.com/repos/{owner}/{repo}/contents')
            contents_response.raise_for_status()
            contents_data = contents_response.json()
            
            # Recent commits
            commits_response = self.client.get(f'https://api.github.com/repos/{owner}/{repo}/commits?per_page=100')
            commits_response.raise_for_status()
            commits_data = commits_response.json()
            
            # Contributors
            contributors_response = self.client.get(f'https://api.github.com/repos/{owner}/{repo}/contributors')
            contributors_response.raise_for_status()
            contributors_data = contributors_response.json()
            
            # Issues and PRs
            issues_response = self.client.get(f'https://api.github.com/repos/{owner}/{repo}/issues?state=all&per_page=100')
            issues_response.raise_for_status()
            issues_data = issues_response.json()
            
            # Releases
            releases_response = self.client.get(f'https://api.github.com/repos/{owner}/{repo}/releases')
            releases_response.raise_for_status()
            releases_data = releases_response.json()
            
            return {
                'repo': repo_data,
                'contents': contents_data,
                'commits': commits_data,
                'contributors': contributors_data,
                'issues': issues_data,
                'releases': releases_data
            }
            
        except httpx.HTTPStatusError as e:
            print(f"HTTP error fetching data for {owner}/{repo}: {e.response.status_code}")
            return {}
        except Exception as e:
            print(f"Error fetching data for {owner}/{repo}: {str(e)}")
            return {}
    
    def analyze_file_structure(self, contents: List[Dict]) -> Dict:
        """Analyze repository file structure and organization."""
        try:
            structure_metrics = {
                'has_readme': False,
                'has_license': False,
                'has_contributing': False,
                'has_changelog': False,
                'has_tests': False,
                'has_docs': False,
                'has_config_files': False,
                'directory_count': 0,
                'file_count': 0,
                'python_files': 0,
                'javascript_files': 0,
                'markdown_files': 0,
                'config_files': 0
            }
            
            readme_patterns = re.compile(r'^readme\.(md|txt|rst)$', re.IGNORECASE)
            license_patterns = re.compile(r'^(license|licence)(\.(md|txt))?$', re.IGNORECASE)
            contributing_patterns = re.compile(r'^contributing\.(md|txt|rst)$', re.IGNORECASE)
            changelog_patterns = re.compile(r'^(changelog|changes|history)\.(md|txt|rst)$', re.IGNORECASE)
            
            for item in contents:
                name = item.get('name', '').lower()
                item_type = item.get('type', '')
                
                if item_type == 'dir':
                    structure_metrics['directory_count'] += 1
                    if name in ['test', 'tests', '__tests__', 'spec']:
                        structure_metrics['has_tests'] = True
                    elif name in ['docs', 'documentation', 'doc']:
                        structure_metrics['has_docs'] = True
                else:
                    structure_metrics['file_count'] += 1
                    
                    # Check for important files
                    if readme_patterns.match(name):
                        structure_metrics['has_readme'] = True
                    elif license_patterns.match(name):
                        structure_metrics['has_license'] = True
                    elif contributing_patterns.match(name):
                        structure_metrics['has_contributing'] = True
                    elif changelog_patterns.match(name):
                        structure_metrics['has_changelog'] = True
                    
                    # File type analysis
                    if name.endswith('.py'):
                        structure_metrics['python_files'] += 1
                    elif name.endswith(('.js', '.jsx', '.ts', '.tsx')):
                        structure_metrics['javascript_files'] += 1
                    elif name.endswith('.md'):
                        structure_metrics['markdown_files'] += 1
                    elif name in ['package.json', 'requirements.txt', 'setup.py', 'pyproject.toml', 'cargo.toml', 'pom.xml']:
                        structure_metrics['has_config_files'] = True
                        structure_metrics['config_files'] += 1
            
            return structure_metrics
            
        except Exception as e:
            print(f"Error analyzing file structure: {str(e)}")
            return {}
    
    def analyze_readme_quality(self, owner: str, repo: str, contents: List[Dict]) -> Dict:
        """Analyze README file quality and completeness."""
        try:
            readme_metrics = {
                'exists': False,
                'length': 0,
                'has_description': False,
                'has_installation': False,
                'has_usage': False,
                'has_contributing': False,
                'has_license_section': False,
                'has_badges': False,
                'has_links': False,
                'sections_count': 0,
                'quality_score': 0
            }
            
            # Find README file
            readme_file = None
            for item in contents:
                if re.match(r'^readme\.(md|txt|rst)$', item.get('name', ''), re.IGNORECASE):
                    readme_file = item
                    break
            
            if not readme_file:
                return readme_metrics
            
            # Fetch README content
            readme_response = self.client.get(readme_file['download_url'])
            readme_response.raise_for_status()
            readme_content = readme_response.text
            
            readme_metrics['exists'] = True
            readme_metrics['length'] = len(readme_content)
            
            # Analyze content
            content_lower = readme_content.lower()
            
            # Check for key sections
            if any(word in content_lower for word in ['description', 'about', 'overview']):
                readme_metrics['has_description'] = True
            if any(word in content_lower for word in ['install', 'setup', 'getting started']):
                readme_metrics['has_installation'] = True
            if any(word in content_lower for word in ['usage', 'example', 'how to', 'quickstart']):