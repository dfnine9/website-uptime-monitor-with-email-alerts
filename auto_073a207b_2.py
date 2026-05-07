```python
#!/usr/bin/env python3
"""
Code Quality Assessment Tool

A comprehensive tool for analyzing Python codebases to assess code quality across multiple dimensions:
- File structure analysis (organization, naming conventions)
- Documentation coverage (docstrings, comments)
- Coding standards compliance (PEP 8, naming conventions)
- Test coverage indicators (test file presence, test patterns)
- Maintainability scoring (complexity, structure, documentation)

Usage: python script.py [directory_path]
If no directory is provided, analyzes the current directory.
"""

import os
import ast
import re
import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class FileMetrics:
    """Metrics for a single Python file."""
    path: str
    lines_of_code: int
    cyclomatic_complexity: int
    has_docstring: bool
    docstring_coverage: float
    functions: int
    classes: int
    test_functions: int
    pep8_issues: List[str]
    maintainability_score: float


@dataclass
class ProjectMetrics:
    """Overall project quality metrics."""
    total_files: int
    total_lines: int
    avg_complexity: float
    documentation_coverage: float
    test_coverage_indicator: float
    structure_score: float
    overall_maintainability: float
    file_metrics: List[FileMetrics]
    recommendations: List[str]


class ComplexityAnalyzer(ast.NodeVisitor):
    """AST visitor to calculate cyclomatic complexity."""
    
    def __init__(self):
        self.complexity = 1
        
    def visit_If(self, node):
        self.complexity += 1
        self.generic_visit(node)
        
    def visit_For(self, node):
        self.complexity += 1
        self.generic_visit(node)
        
    def visit_While(self, node):
        self.complexity += 1
        self.generic_visit(node)
        
    def visit_ExceptHandler(self, node):
        self.complexity += 1
        self.generic_visit(node)
        
    def visit_With(self, node):
        self.complexity += 1
        self.generic_visit(node)


class DocstringAnalyzer(ast.NodeVisitor):
    """AST visitor to analyze documentation coverage."""
    
    def __init__(self):
        self.functions = 0
        self.classes = 0
        self.documented_functions = 0
        self.documented_classes = 0
        self.test_functions = 0
        
    def visit_FunctionDef(self, node):
        self.functions += 1
        if node.name.startswith('test_'):
            self.test_functions += 1
        if ast.get_docstring(node):
            self.documented_functions += 1
        self.generic_visit(node)
        
    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)
        
    def visit_ClassDef(self, node):
        self.classes += 1
        if ast.get_docstring(node):
            self.documented_classes += 1
        self.generic_visit(node)


class CodeQualityAssessor:
    """Main class for assessing code quality."""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.python_files = []
        self._discover_python_files()
        
    def _discover_python_files(self):
        """Discover all Python files in the project."""
        try:
            for file_path in self.root_path.rglob("*.py"):
                if not any(part.startswith('.') for part in file_path.parts):
                    self.python_files.append(file_path)
        except Exception as e:
            print(f"Error discovering files: {e}")
            
    def _analyze_file_structure(self) -> float:
        """Analyze project file structure and organization."""
        score = 0.0
        total_checks = 4
        
        # Check for standard Python project structure
        standard_dirs = ['tests', 'src', 'docs']
        has_standard_structure = any(
            (self.root_path / dirname).exists() for dirname in standard_dirs
        )
        if has_standard_structure:
            score += 25
            
        # Check for setup files
        setup_files = ['setup.py', 'pyproject.toml', 'requirements.txt']
        has_setup = any(
            (self.root_path / filename).exists() for filename in setup_files
        )
        if has_setup:
            score += 25
            
        # Check for README
        readme_files = ['README.md', 'README.rst', 'README.txt']
        has_readme = any(
            (self.root_path / filename).exists() for filename in readme_files
        )
        if has_readme:
            score += 25
            
        # Check naming conventions
        proper_naming = all(
            file_path.name.islower() and '_' in file_path.name or len(file_path.name.split('.')[0]) <= 15
            for file_path in self.python_files
        )
        if proper_naming:
            score += 25
            
        return score
    
    def _check_pep8_compliance(self, content: str, file_path: str) -> List[str]:
        """Basic PEP 8 compliance checks."""
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Line length check
            if len(line) > 79:
                issues.append(f"Line {i}: Line too long ({len(line)} > 79)")
                
            # Trailing whitespace
            if line.endswith(' ') or line.endswith('\t'):
                issues.append(f"Line {i}: Trailing whitespace")
                
            # Multiple imports on one line
            if line.strip().startswith('import ') and ',' in line:
                issues.append(f"Line {i}: Multiple imports on one line")
                
        # Check for proper spacing around operators
        operator_pattern = re.compile(r'\w[+\-*/=<>!]=?\w')
        for i, line in enumerate(lines, 1):
            if operator_pattern.search(line):
                issues.append(f"Line {i}: Missing spaces around operator")
                
        return issues[:10]  # Limit to first 10 issues
    
    def _analyze_single_file(self, file_path: Path) -> Optional[FileMetrics]:
        """Analyze a single Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse AST
            try:
                tree = ast.parse(content)
            except SyntaxError as e:
                print(f"Syntax error in {file_path}: {e}")
                return None
                
            # Calculate complexity
            complexity_analyzer = ComplexityAnalyzer()
            complexity_analyzer.visit(tree)
            
            # Analyze documentation
            doc_analyzer = DocstringAnalyzer()
            doc_analyzer.visit(tree)
            
            # Calculate documentation coverage
            total_items = doc_analyzer.functions + doc_analyzer.classes
            documented_items = doc_analyzer.documented_functions + doc_analyzer.documented_classes
            doc_coverage = (documented_items / total_items * 100) if total_items > 0 else 100
            
            # Check for module docstring
            has_module_docstring = ast.get_docstring(tree) is not None
            
            # Count lines of code (excluding empty lines and comments)
            loc = len([line for line in content.split('\n') 
                      if line.strip() and not line.strip().startswith('#')])
            
            # PEP 8 compliance
            pep8_issues = self._check_pep8_compliance(content, str(file_path))
            
            # Calculate maintainability score
            maintain