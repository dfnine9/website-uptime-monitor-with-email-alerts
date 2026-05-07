```python
#!/usr/bin/env python3
"""
GitHub Repository Analyzer

This module fetches repository contents using the GitHub API, analyzes the file structure,
and identifies key project files to determine project type and dependencies.

Key features:
- Fetches repository tree structure via GitHub API
- Identifies project configuration files (setup.py, package.json, requirements.txt, etc.)
- Determines project type based on detected files
- Extracts dependency information where possible
- Handles API rate limits and errors gracefully

Usage: python script.py
"""

import json
import re
import sys
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import base64


class GitHubAnalyzer:
    def __init__(self):
        self.session_headers = {
            'User-Agent': 'GitHub-Repository-Analyzer/1.0',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # Key files that indicate project types
        self.project_indicators = {
            'python': ['setup.py', 'pyproject.toml', 'requirements.txt', 'Pipfile', 'poetry.lock'],
            'javascript': ['package.json', 'yarn.lock', 'package-lock.json'],
            'java': ['pom.xml', 'build.gradle', 'gradle.properties'],
            'rust': ['Cargo.toml', 'Cargo.lock'],
            'go': ['go.mod', 'go.sum'],
            'ruby': ['Gemfile', 'Gemfile.lock'],
            'php': ['composer.json', 'composer.lock'],
            'c++': ['CMakeLists.txt', 'Makefile'],
            'docker': ['Dockerfile', 'docker-compose.yml'],
            'terraform': ['main.tf', '*.tf'],
        }

    def make_request(self, url):
        """Make HTTP request with error handling"""
        try:
            request = Request(url, headers=self.session_headers)
            with urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode('utf-8'))
        except HTTPError as e:
            if e.code == 403:
                print(f"Error: Rate limit exceeded or access denied (HTTP {e.code})")
            elif e.code == 404:
                print(f"Error: Repository not found (HTTP {e.code})")
            else:
                print(f"Error: HTTP {e.code} - {e.reason}")
            return None
        except URLError as e:
            print(f"Error: Network error - {e.reason}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON response - {e}")
            return None

    def parse_repo_url(self, repo_url):
        """Extract owner and repo name from GitHub URL"""
        try:
            parsed = urlparse(repo_url)
            path_parts = parsed.path.strip('/').split('/')
            if len(path_parts) >= 2:
                return path_parts[0], path_parts[1]
            else:
                raise ValueError("Invalid repository URL format")
        except Exception as e:
            print(f"Error parsing repository URL: {e}")
            return None, None

    def get_repo_tree(self, owner, repo):
        """Fetch repository tree structure"""
        url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/HEAD?recursive=1"
        return self.make_request(url)

    def get_file_content(self, owner, repo, file_path):
        """Fetch content of a specific file"""
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
        response = self.make_request(url)
        
        if response and 'content' in response:
            try:
                # Decode base64 content
                content = base64.b64decode(response['content']).decode('utf-8')
                return content
            except Exception as e:
                print(f"Error decoding file content for {file_path}: {e}")
                return None
        return None

    def identify_project_types(self, files):
        """Identify project types based on present files"""
        detected_types = []
        key_files_found = {}
        
        file_names = [f['path'] for f in files if f['type'] == 'blob']
        
        for project_type, indicators in self.project_indicators.items():
            found_indicators = []
            for indicator in indicators:
                if indicator.endswith('*'):
                    # Handle wildcard patterns
                    pattern = indicator.replace('*', '.*')
                    if any(re.search(pattern, fname) for fname in file_names):
                        found_indicators.append(indicator)
                else:
                    if indicator in file_names:
                        found_indicators.append(indicator)
            
            if found_indicators:
                detected_types.append(project_type)
                key_files_found[project_type] = found_indicators
        
        return detected_types, key_files_found

    def extract_dependencies(self, owner, repo, key_files):
        """Extract dependencies from key configuration files"""
        dependencies = {}
        
        for project_type, files in key_files.items():
            deps = []
            
            for file_name in files:
                content = self.get_file_content(owner, repo, file_name)
                if not content:
                    continue
                
                try:
                    if file_name == 'package.json' and project_type == 'javascript':
                        pkg_data = json.loads(content)
                        deps.extend(list(pkg_data.get('dependencies', {}).keys()))
                        deps.extend(list(pkg_data.get('devDependencies', {}).keys()))
                    
                    elif file_name == 'requirements.txt' and project_type == 'python':
                        for line in content.split('\n'):
                            line = line.strip()
                            if line and not line.startswith('#'):
                                # Extract package name (before version specifiers)
                                pkg_name = re.split(r'[>=<~!]', line)[0].strip()
                                if pkg_name:
                                    deps.append(pkg_name)
                    
                    elif file_name == 'Cargo.toml' and project_type == 'rust':
                        # Simple regex-based parsing for Cargo.toml dependencies
                        dep_section = False
                        for line in content.split('\n'):
                            line = line.strip()
                            if line == '[dependencies]':
                                dep_section = True
                                continue
                            elif line.startswith('[') and dep_section:
                                dep_section = False
                            elif dep_section and '=' in line:
                                dep_name = line.split('=')[0].strip().strip('"')
                                if dep_name:
                                    deps.append(dep_name)
                    
                    elif file_name == 'go.mod' and project_type == 'go':
                        in_require = False
                        for line in content.split('\n'):
                            line = line.strip()
                            if line.startswith('require'):
                                in_require = True
                                if '(' not in line:
                                    # Single require statement
                                    parts = line.split()
                                    if len(parts) >= 2:
                                        deps.append(parts[1])
                                continue
                            elif in_require:
                                if line == ')':
                                    in_require = False
                                elif line and not line.startswith('//'):
                                    parts = line.split()
                                    if parts:
                                        deps.append(parts[0])
                
                except (json.JSONDecodeError, Exception) as e:
                    print(f"Warning: Could not parse {file_name}: {e}")
            
            if deps:
                dependencies[project_type] = list(set(deps))  # Remove duplicates
        
        return dependencies

    def analyze_repository(self, repo_url):
        """Main analysis function"""
        print(f"