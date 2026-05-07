```python
#!/usr/bin/env python3
"""
Python Code Quality Analyzer

This script walks through directories, parses Python files using the AST module,
and performs basic code quality checks including:
- Line length violations (default: 88 characters)
- Function complexity analysis (cyclomatic complexity)
- Import usage analysis (unused imports, relative vs absolute)
- Basic style violations

Usage:
    python script.py [directory_path]

If no directory is specified, it analyzes the current directory.
"""

import ast
import os
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any


class CodeQualityAnalyzer(ast.NodeVisitor):
    """AST visitor that performs code quality analysis."""
    
    def __init__(self, source_lines: List[str]):
        self.source_lines = source_lines
        self.issues = []
        self.imports = set()
        self.used_names = set()
        self.functions = []
        
    def visit_Import(self, node: ast.Import) -> None:
        """Track import statements."""
        for alias in node.names:
            self.imports.add(alias.name)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Track from-import statements."""
        if node.module:
            for alias in node.names:
                if alias.name == '*':
                    self.issues.append(f"Line {node.lineno}: Wildcard import from {node.module}")
                else:
                    self.imports.add(f"{node.module}.{alias.name}")
        self.generic_visit(node)
    
    def visit_Name(self, node: ast.Name) -> None:
        """Track name usage."""
        self.used_names.add(node.id)
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Analyze function definitions."""
        complexity = self._calculate_complexity(node)
        self.functions.append({
            'name': node.name,
            'line': node.lineno,
            'complexity': complexity
        })
        
        if complexity > 10:
            self.issues.append(f"Line {node.lineno}: Function '{node.name}' has high complexity ({complexity})")
        
        # Check for missing docstring
        if not ast.get_docstring(node):
            self.issues.append(f"Line {node.lineno}: Function '{node.name}' missing docstring")
        
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Analyze async function definitions."""
        self.visit_FunctionDef(node)  # Reuse logic
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1
            elif isinstance(child, ast.comprehension):
                complexity += 1
        
        return complexity


def check_line_length(file_path: str, max_length: int = 88) -> List[str]:
    """Check for line length violations."""
    issues = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line_stripped = line.rstrip('\n\r')
                if len(line_stripped) > max_length:
                    issues.append(f"Line {line_num}: Line too long ({len(line_stripped)} > {max_length})")
    except UnicodeDecodeError:
        issues.append(f"Encoding error: Unable to read {file_path}")
    except Exception as e:
        issues.append(f"Error reading file: {e}")
    
    return issues


def analyze_python_file(file_path: str) -> Dict[str, Any]:
    """Analyze a single Python file for code quality issues."""
    results = {
        'file': file_path,
        'line_issues': [],
        'ast_issues': [],
        'functions': [],
        'imports': set(),
        'parse_error': None
    }
    
    try:
        # Check line length
        results['line_issues'] = check_line_length(file_path)
        
        # Parse AST and analyze
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
            source_lines = source.splitlines()
        
        try:
            tree = ast.parse(source, filename=file_path)
            analyzer = CodeQualityAnalyzer(source_lines)
            analyzer.visit(tree)
            
            results['ast_issues'] = analyzer.issues
            results['functions'] = analyzer.functions
            results['imports'] = analyzer.imports
            
        except SyntaxError as e:
            results['parse_error'] = f"Syntax error: {e}"
        
    except Exception as e:
        results['parse_error'] = f"Error analyzing file: {e}"
    
    return results


def find_python_files(directory: str) -> List[str]:
    """Find all Python files in directory and subdirectories."""
    python_files = []
    
    try:
        for root, dirs, files in os.walk(directory):
            # Skip common directories to avoid
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
    except Exception as e:
        print(f"Error walking directory {directory}: {e}", file=sys.stderr)
    
    return python_files


def print_results(results: List[Dict[str, Any]]) -> None:
    """Print analysis results to stdout."""
    total_files = len(results)
    total_issues = 0
    
    print(f"Code Quality Analysis Report")
    print(f"{'=' * 50}")
    print(f"Analyzed {total_files} Python files\n")
    
    for result in results:
        file_path = result['file']
        issues = result['line_issues'] + result['ast_issues']
        
        if result['parse_error']:
            print(f"❌ {file_path}")
            print(f"   {result['parse_error']}\n")
            total_issues += 1
            continue
        
        if issues:
            print(f"⚠️  {file_path}")
            for issue in issues:
                print(f"   {issue}")
            print()
            total_issues += len(issues)
        else:
            print(f"✅ {file_path} - No issues found")
    
    print(f"{'=' * 50}")
    print(f"Summary: {total_issues} total issues found across {total_files} files")
    
    if total_issues > 0:
        print(f"\nIssue breakdown:")
        line_issues = sum(len(r['line_issues']) for r in results)
        ast_issues = sum(len(r['ast_issues']) for r in results)
        parse_errors = sum(1 for r in results if r['parse_error'])
        
        if line_issues > 0:
            print(f"  - Line length violations: {line_issues}")
        if ast_issues > 0:
            print(f"  - Code quality issues: {ast_issues}")
        if parse_errors > 0:
            print(f"  - Parse errors: {parse_errors}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Analyze Python