```python
"""
GitHub Data Analysis Module

This module processes GitHub repository data to calculate comprehensive code quality metrics,
issue response times, documentation completeness scores, and activity trends.

Features:
- Code quality assessment based on repository structure and best practices
- Issue response time analysis with statistical summaries
- Documentation completeness scoring across multiple file types
- Activity trend analysis over time periods
- Comprehensive error handling and logging

Usage:
    python script.py

The script fetches data from GitHub's API and generates detailed analytics reports
suitable for repository assessment and team performance evaluation.
"""

import json
import statistics
import re
import datetime
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urlparse
import httpx


class GitHubDataAnalyzer:
    """Analyzes GitHub repository data for various quality and performance metrics."""
    
    def __init__(self):
        self.client = httpx.Client(timeout=30.0)
        self.results = {}
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()
    
    def fetch_repository_data(self, owner: str, repo: str, token: Optional[str] = None) -> Dict[str, Any]:
        """Fetch comprehensive repository data from GitHub API."""
        headers = {}
        if token:
            headers['Authorization'] = f'token {token}'
            
        base_url = f"https://api.github.com/repos/{owner}/{repo}"
        
        try:
            # Repository metadata
            repo_response = self.client.get(base_url, headers=headers)
            repo_response.raise_for_status()
            repo_data = repo_response.json()
            
            # Repository contents for documentation analysis
            contents_response = self.client.get(f"{base_url}/contents", headers=headers)
            contents_data = contents_response.json() if contents_response.status_code == 200 else []
            
            # Issues for response time analysis
            issues_response = self.client.get(f"{base_url}/issues?state=all&per_page=100", headers=headers)
            issues_data = issues_response.json() if issues_response.status_code == 200 else []
            
            # Commits for activity trends
            commits_response = self.client.get(f"{base_url}/commits?per_page=100", headers=headers)
            commits_data = commits_response.json() if commits_response.status_code == 200 else []
            
            # Languages for code quality assessment
            languages_response = self.client.get(f"{base_url}/languages", headers=headers)
            languages_data = languages_response.json() if languages_response.status_code == 200 else {}
            
            return {
                'repository': repo_data,
                'contents': contents_data,
                'issues': issues_data,
                'commits': commits_data,
                'languages': languages_data
            }
            
        except httpx.HTTPStatusError as e:
            print(f"HTTP Error fetching repository data: {e.response.status_code} - {e.response.text}")
            return {}
        except Exception as e:
            print(f"Error fetching repository data: {str(e)}")
            return {}
    
    def calculate_code_quality_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate code quality metrics based on repository characteristics."""
        try:
            repo = data.get('repository', {})
            contents = data.get('contents', [])
            languages = data.get('languages', {})
            
            metrics = {
                'has_readme': any(file.get('name', '').lower().startswith('readme') for file in contents),
                'has_license': any(file.get('name', '').lower().startswith('license') for file in contents),
                'has_contributing': any('contributing' in file.get('name', '').lower() for file in contents),
                'has_code_of_conduct': any('code_of_conduct' in file.get('name', '').lower() for file in contents),
                'has_tests': any('test' in file.get('name', '').lower() for file in contents),
                'has_ci_config': any(file.get('name', '') in ['.github', '.gitlab-ci.yml', 'Jenkinsfile', '.travis.yml'] for file in contents),
                'language_diversity': len(languages),
                'primary_language': max(languages.items(), key=lambda x: x[1])[0] if languages else 'Unknown',
                'stars': repo.get('stargazers_count', 0),
                'forks': repo.get('forks_count', 0),
                'open_issues': repo.get('open_issues_count', 0),
                'has_description': bool(repo.get('description')),
                'has_website': bool(repo.get('homepage')),
                'has_topics': len(repo.get('topics', [])),
                'last_updated': repo.get('updated_at')
            }
            
            # Calculate quality score (0-100)
            score_components = {
                'documentation': (metrics['has_readme'] + metrics['has_contributing'] + metrics['has_code_of_conduct']) * 10,
                'project_setup': (metrics['has_license'] + metrics['has_description'] + bool(metrics['has_topics'])) * 10,
                'testing_ci': (metrics['has_tests'] + metrics['has_ci_config']) * 15,
                'community': min(metrics['stars'] / 100, 1) * 20 + min(metrics['forks'] / 50, 1) * 10,
                'maintenance': max(0, 10 - min(metrics['open_issues'] / 10, 10))
            }
            
            metrics['quality_score'] = sum(score_components.values())
            metrics['score_breakdown'] = score_components
            
            return metrics
            
        except Exception as e:
            print(f"Error calculating code quality metrics: {str(e)}")
            return {}
    
    def calculate_issue_response_times(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate issue response time statistics."""
        try:
            issues = data.get('issues', [])
            
            if not issues:
                return {'message': 'No issues found'}
            
            response_times = []
            issue_stats = {
                'total_issues': len(issues),
                'open_issues': 0,
                'closed_issues': 0,
                'issues_with_responses': 0,
                'avg_response_time_hours': 0,
                'median_response_time_hours': 0,
                'response_time_distribution': {}
            }
            
            for issue in issues:
                if issue.get('state') == 'open':
                    issue_stats['open_issues'] += 1
                else:
                    issue_stats['closed_issues'] += 1
                
                created_at = datetime.datetime.fromisoformat(issue['created_at'].replace('Z', '+00:00'))
                
                # Check for first comment (response)
                if issue.get('comments', 0) > 0:
                    issue_stats['issues_with_responses'] += 1
                    
                    # For closed issues, use closed_at as proxy for response time
                    if issue.get('closed_at'):
                        closed_at = datetime.datetime.fromisoformat(issue['closed_at'].replace('Z', '+00:00'))
                        response_time = (closed_at - created_at).total_seconds() / 3600  # hours
                        response_times.append(response_time)
            
            if response_times:
                issue_stats['avg_response_time_hours'] = round(statistics.mean(response_times), 2)
                issue_stats['median_response_time_hours'] = round(statistics.median(response_times), 2)
                
                # Distribution analysis
                quick_responses = len([t for t in response_times if t <= 24])  # < 24 hours
                medium_responses = len([t for t in response_times if 24 < t <= 168])  # 1-7