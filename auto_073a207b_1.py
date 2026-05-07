```python
#!/usr/bin/env python3
"""
Security Analysis Module for Repository Scanning

This module performs comprehensive security analysis on repository files by:
1. Scanning source code for common vulnerability patterns (SQL injection, XSS, hardcoded secrets)
2. Checking for presence of security policy files (SECURITY.md, .github/SECURITY.md)
3. Analyzing dependency files (requirements.txt, package.json, Pipfile) for known CVEs
4. Integrating with GitHub's Security Advisories API for vulnerability data
5. Generating a comprehensive security report with risk ratings

The module is designed to be self-contained and can analyze local repositories
or be extended to work with remote repositories via API integration.
"""

import os
import re
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import urllib.request
import urllib.parse
import urllib.error

class SecurityAnalyzer:
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.vulnerabilities = []
        self.security_policies = []
        self.dependency_issues = []
        
        # Common vulnerability patterns
        self.vuln_patterns = {
            'sql_injection': [
                r'execute\s*\(\s*["\'].*\+.*["\']',
                r'query\s*\(\s*["\'].*\+.*["\']',
                r'SELECT.*\+.*FROM',
                r'cursor\.execute\s*\(\s*["\'].*%.*["\']'
            ],
            'xss': [
                r'innerHTML\s*=\s*.*\+',
                r'document\.write\s*\(\s*.*\+',
                r'dangerouslySetInnerHTML',
                r'eval\s*\(\s*.*\+.*\)'
            ],
            'hardcoded_secrets': [
                r'password\s*=\s*["\'][^"\']{8,}["\']',
                r'api_key\s*=\s*["\'][^"\']{20,}["\']',
                r'secret\s*=\s*["\'][^"\']{16,}["\']',
                r'token\s*=\s*["\'][^"\']{20,}["\']',
                r'-----BEGIN\s+(PRIVATE|RSA|DSA|EC)\s+KEY-----'
            ],
            'path_traversal': [
                r'open\s*\(\s*.*\+.*\.\.',
                r'file\s*\(\s*.*\+.*\.\.',
                r'include\s*\(\s*.*\+.*\.\.',
                r'require\s*\(\s*.*\+.*\.\.'
            ],
            'command_injection': [
                r'os\.system\s*\(\s*.*\+',
                r'subprocess\.call\s*\(\s*.*\+',
                r'eval\s*\(\s*request\.',
                r'exec\s*\(\s*request\.'
            ]
        }
        
        # Security policy file locations
        self.security_files = [
            'SECURITY.md',
            'SECURITY.rst',
            'SECURITY.txt',
            '.github/SECURITY.md',
            'docs/SECURITY.md',
            'security/README.md'
        ]
        
        # Dependency files to analyze
        self.dependency_files = [
            'requirements.txt',
            'package.json',
            'package-lock.json',
            'Pipfile',
            'Pipfile.lock',
            'composer.json',
            'composer.lock',
            'Gemfile',
            'Gemfile.lock',
            'pom.xml',
            'build.gradle'
        ]

    def scan_vulnerabilities(self) -> List[Dict]:
        """Scan repository files for common vulnerability patterns."""
        print("🔍 Scanning for vulnerability patterns...")
        
        code_extensions = {'.py', '.js', '.php', '.java', '.rb', '.go', '.rs', '.cpp', '.c', '.cs'}
        
        try:
            for file_path in self.repo_path.rglob('*'):
                if file_path.is_file() and file_path.suffix in code_extensions:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                        for vuln_type, patterns in self.vuln_patterns.items():
                            for pattern in patterns:
                                matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                                for match in matches:
                                    line_num = content[:match.start()].count('\n') + 1
                                    self.vulnerabilities.append({
                                        'type': vuln_type,
                                        'file': str(file_path.relative_to(self.repo_path)),
                                        'line': line_num,
                                        'pattern': pattern,
                                        'match': match.group(),
                                        'severity': self._get_severity(vuln_type)
                                    })
                    except Exception as e:
                        print(f"⚠️  Error scanning {file_path}: {e}")
                        
        except Exception as e:
            print(f"❌ Error during vulnerability scan: {e}")
            
        return self.vulnerabilities

    def check_security_policies(self) -> List[Dict]:
        """Check for presence of security policy files."""
        print("📋 Checking for security policy files...")
        
        try:
            for policy_file in self.security_files:
                policy_path = self.repo_path / policy_file
                if policy_path.exists():
                    try:
                        size = policy_path.stat().st_size
                        with open(policy_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        self.security_policies.append({
                            'file': policy_file,
                            'exists': True,
                            'size': size,
                            'has_contact_info': bool(re.search(r'@|email|contact', content, re.IGNORECASE)),
                            'has_disclosure_policy': bool(re.search(r'disclosure|report|vulnerability', content, re.IGNORECASE))
                        })
                    except Exception as e:
                        print(f"⚠️  Error reading {policy_file}: {e}")
                        
        except Exception as e:
            print(f"❌ Error checking security policies: {e}")
            
        return self.security_policies

    def analyze_dependencies(self) -> List[Dict]:
        """Analyze dependency files for potential security issues."""
        print("📦 Analyzing dependency files...")
        
        try:
            for dep_file in self.dependency_files:
                dep_path = self.repo_path / dep_file
                if dep_path.exists():
                    try:
                        with open(dep_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        deps = self._parse_dependencies(dep_file, content)
                        for dep in deps:
                            # Check for known vulnerable patterns
                            issues = self._check_dependency_security(dep)
                            if issues:
                                self.dependency_issues.extend(issues)
                                
                    except Exception as e:
                        print(f"⚠️  Error analyzing {dep_file}: {e}")
                        
        except Exception as e:
            print(f"❌ Error during dependency analysis: {e}")
            
        return self.dependency_issues

    def query_github_advisories(self, package_name: str) -> List[Dict]:
        """Query GitHub Security Advisories API for package vulnerabilities."""
        try:
            # GitHub GraphQL API endpoint
            url = "https://api.github.com/graphql"
            
            query = """
            query($package: String!) {
              securityVulnerabilities(first: 10, ecosystem