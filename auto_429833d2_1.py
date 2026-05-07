```python
#!/usr/bin/env python3
"""
Health Analysis Module

This module evaluates repository health across three dimensions:
1. Documentation Quality: README completeness, code comments, wiki presence
2. Security Status: Dependency vulnerabilities, secrets detection patterns
3. Maintenance Indicators: Commit frequency, issue resolution, stale branches

Analyzes local Git repositories and provides scored health metrics.
"""

import os
import re
import json
import subprocess
import pathlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional


class RepositoryHealthAnalyzer:
    """Analyzes repository health across documentation, security, and maintenance dimensions."""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = pathlib.Path(repo_path).resolve()
        self.results = {
            "documentation": {},
            "security": {},
            "maintenance": {},
            "overall_score": 0
        }
    
    def analyze(self) -> Dict[str, Any]:
        """Perform complete health analysis of the repository."""
        try:
            if not self._is_git_repo():
                raise ValueError("Not a Git repository")
            
            print(f"Analyzing repository health: {self.repo_path}")
            
            self._analyze_documentation()
            self._analyze_security()
            self._analyze_maintenance()
            self._calculate_overall_score()
            
            return self.results
            
        except Exception as e:
            print(f"Error during analysis: {e}")
            return {"error": str(e)}
    
    def _is_git_repo(self) -> bool:
        """Check if the current directory is a Git repository."""
        return (self.repo_path / ".git").exists()
    
    def _analyze_documentation(self):
        """Analyze documentation quality metrics."""
        try:
            doc_score = 0
            max_score = 100
            
            # README analysis
            readme_score = self._analyze_readme()
            doc_score += readme_score
            
            # Code comments analysis
            comments_score = self._analyze_code_comments()
            doc_score += comments_score
            
            # Wiki presence (check for docs/ folder or wiki references)
            wiki_score = self._analyze_wiki_presence()
            doc_score += wiki_score
            
            self.results["documentation"] = {
                "readme_score": readme_score,
                "comments_score": comments_score,
                "wiki_score": wiki_score,
                "total_score": min(doc_score, max_score),
                "max_score": max_score
            }
            
        except Exception as e:
            self.results["documentation"] = {"error": str(e)}
    
    def _analyze_readme(self) -> int:
        """Analyze README file completeness (max 40 points)."""
        readme_files = ["README.md", "README.rst", "README.txt", "README"]
        readme_path = None
        
        for readme in readme_files:
            path = self.repo_path / readme
            if path.exists():
                readme_path = path
                break
        
        if not readme_path:
            return 0
        
        try:
            content = readme_path.read_text(encoding="utf-8")
            score = 10  # Base score for having a README
            
            # Check for key sections
            sections = [
                (r"#.*installation", 5),
                (r"#.*usage", 5),
                (r"#.*description|#.*about", 5),
                (r"#.*license", 3),
                (r"#.*contributing", 3),
                (r"#.*requirements|#.*dependencies", 4),
                (r"badge", 5)  # Badges indicate mature project
            ]
            
            for pattern, points in sections:
                if re.search(pattern, content.lower()):
                    score += points
            
            return min(score, 40)
            
        except Exception:
            return 5  # Partial credit for having a README file
    
    def _analyze_code_comments(self) -> int:
        """Analyze code comment density (max 30 points)."""
        try:
            code_files = []
            comment_lines = 0
            total_lines = 0
            
            # Find code files
            for ext in [".py", ".js", ".java", ".cpp", ".c", ".go", ".rs"]:
                code_files.extend(self.repo_path.rglob(f"*{ext}"))
            
            if not code_files:
                return 15  # Neutral score if no code files
            
            for file_path in code_files[:20]:  # Limit to first 20 files for performance
                try:
                    content = file_path.read_text(encoding="utf-8")
                    lines = content.split('\n')
                    total_lines += len(lines)
                    
                    # Count comment lines (basic patterns)
                    for line in lines:
                        stripped = line.strip()
                        if (stripped.startswith('#') or 
                            stripped.startswith('//') or
                            stripped.startswith('/*') or
                            stripped.startswith('*') or
                            '"""' in stripped or
                            "'''" in stripped):
                            comment_lines += 1
                            
                except Exception:
                    continue
            
            if total_lines == 0:
                return 15
            
            comment_ratio = comment_lines / total_lines
            # Score based on comment ratio (10-20% is good)
            if comment_ratio >= 0.15:
                return 30
            elif comment_ratio >= 0.10:
                return 25
            elif comment_ratio >= 0.05:
                return 20
            else:
                return 10
                
        except Exception:
            return 15
    
    def _analyze_wiki_presence(self) -> int:
        """Check for documentation/wiki presence (max 30 points)."""
        score = 0
        
        # Check for documentation directories
        doc_dirs = ["docs", "documentation", "wiki", "doc"]
        for doc_dir in doc_dirs:
            if (self.repo_path / doc_dir).exists():
                score += 15
                break
        
        # Check for additional documentation files
        doc_files = ["CHANGELOG.md", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md"]
        for doc_file in doc_files:
            if (self.repo_path / doc_file).exists():
                score += 5
        
        return min(score, 30)
    
    def _analyze_security(self):
        """Analyze security status metrics."""
        try:
            sec_score = 0
            max_score = 100
            
            # Dependency vulnerability check
            vuln_score = self._check_dependencies()
            sec_score += vuln_score
            
            # Secrets detection
            secrets_score = self._detect_secrets()
            sec_score += secrets_score
            
            # Security files presence
            security_files_score = self._check_security_files()
            sec_score += security_files_score
            
            self.results["security"] = {
                "dependency_score": vuln_score,
                "secrets_score": secrets_score,
                "security_files_score": security_files_score,
                "total_score": min(sec_score, max_score),
                "max_score": max_score
            }
            
        except Exception as e:
            self.results["security"] = {"error": str(e)}
    
    def _check_dependencies(self) -> int:
        """Check for dependency files and potential issues (max 40 points)."""
        score = 40  # Start with full score, deduct for issues
        
        dep_files = [
            "requirements.txt", "package.json", "Gemfile", 
            "composer.json", "go.mod", "Cargo.toml"
        ]
        
        found_deps = False
        for dep_file in dep_files:
            path = self.repo_path / dep_file
            if path.exists():
                found_deps = True
                try:
                    content = path.read_text(encoding="utf-8")
                    # Look