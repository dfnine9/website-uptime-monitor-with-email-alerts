```python
#!/usr/bin/env python3
"""
Python Code Analysis Tool

This script recursively walks through directories and extracts:
- Function signatures (name, arguments, return annotations)
- Class definitions (name, base classes, methods)
- Docstrings from modules, classes, and functions

Uses Python's built-in AST (Abstract Syntax Tree) module for parsing.
No external dependencies required beyond Python standard library.

Usage: python script.py [directory_path]
If no directory is specified, analyzes the current directory.
"""

import ast
import os
import sys
from typing import List, Dict, Any, Optional


class CodeAnalyzer(ast.NodeVisitor):
    """AST visitor that extracts code structure information."""
    
    def __init__(self):
        self.functions = []
        self.classes = []
        self.module_docstring = None
        
    def visit_Module(self, node):
        """Extract module-level docstring."""
        if (node.body and 
            isinstance(node.body[0], ast.Expr) and 
            isinstance(node.body[0].value, ast.Constant) and
            isinstance(node.body[0].value.value, str)):
            self.module_docstring = node.body[0].value.value
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        """Extract function information."""
        try:
            # Get function signature
            args = []
            for arg in node.args.args:
                arg_str = arg.arg
                if arg.annotation:
                    arg_str += f": {ast.unparse(arg.annotation)}"
                args.append(arg_str)
            
            # Handle *args and **kwargs
            if node.args.vararg:
                vararg = f"*{node.args.vararg.arg}"
                if node.args.vararg.annotation:
                    vararg += f": {ast.unparse(node.args.vararg.annotation)}"
                args.append(vararg)
            
            if node.args.kwarg:
                kwarg = f"**{node.args.kwarg.arg}"
                if node.args.kwarg.annotation:
                    kwarg += f": {ast.unparse(node.args.kwarg.annotation)}"
                args.append(kwarg)
            
            # Get return annotation
            return_annotation = ""
            if node.returns:
                return_annotation = f" -> {ast.unparse(node.returns)}"
            
            # Get docstring
            docstring = None
            if (node.body and 
                isinstance(node.body[0], ast.Expr) and 
                isinstance(node.body[0].value, ast.Constant) and
                isinstance(node.body[0].value.value, str)):
                docstring = node.body[0].value.value
            
            self.functions.append({
                'name': node.name,
                'signature': f"{node.name}({', '.join(args)}){return_annotation}",
                'docstring': docstring,
                'lineno': node.lineno
            })
        except Exception as e:
            print(f"Error processing function {node.name}: {e}", file=sys.stderr)
        
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node):
        """Handle async functions the same way as regular functions."""
        self.visit_FunctionDef(node)
    
    def visit_ClassDef(self, node):
        """Extract class information."""
        try:
            # Get base classes
            bases = [ast.unparse(base) for base in node.bases]
            base_str = f"({', '.join(bases)})" if bases else ""
            
            # Get docstring
            docstring = None
            if (node.body and 
                isinstance(node.body[0], ast.Expr) and 
                isinstance(node.body[0].value, ast.Constant) and
                isinstance(node.body[0].value.value, str)):
                docstring = node.body[0].value.value
            
            # Get method names
            methods = []
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    methods.append(item.name)
            
            self.classes.append({
                'name': node.name,
                'signature': f"class {node.name}{base_str}",
                'docstring': docstring,
                'methods': methods,
                'lineno': node.lineno
            })
        except Exception as e:
            print(f"Error processing class {node.name}: {e}", file=sys.stderr)
        
        self.generic_visit(node)


def analyze_python_file(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Analyze a single Python file and extract code structure.
    
    Args:
        filepath: Path to the Python file
        
    Returns:
        Dictionary containing analysis results or None if error
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
        
        tree = ast.parse(content, filename=filepath)
        analyzer = CodeAnalyzer()
        analyzer.visit(tree)
        
        return {
            'filepath': filepath,
            'module_docstring': analyzer.module_docstring,
            'functions': analyzer.functions,
            'classes': analyzer.classes
        }
    except SyntaxError as e:
        print(f"Syntax error in {filepath}: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error analyzing {filepath}: {e}", file=sys.stderr)
        return None


def walk_directory(directory: str) -> List[str]:
    """
    Recursively find all Python files in directory.
    
    Args:
        directory: Root directory to search
        
    Returns:
        List of Python file paths
    """
    python_files = []
    try:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
    except Exception as e:
        print(f"Error walking directory {directory}: {e}", file=sys.stderr)
    
    return python_files


def print_analysis_results(results: List[Dict[str, Any]]):
    """Print formatted analysis results."""
    for result in results:
        if not result:
            continue
            
        print(f"\n{'='*80}")
        print(f"FILE: {result['filepath']}")
        print(f"{'='*80}")
        
        if result['module_docstring']:
            print(f"\nMODULE DOCSTRING:")
            print(f"  {result['module_docstring'][:200]}{'...' if len(result['module_docstring']) > 200 else ''}")
        
        if result['classes']:
            print(f"\nCLASSES:")
            for cls in result['classes']:
                print(f"  Line {cls['lineno']}: {cls['signature']}")
                if cls['docstring']:
                    print(f"    Docstring: {cls['docstring'][:100]}{'...' if len(cls['docstring']) > 100 else ''}")
                if cls['methods']:
                    print(f"    Methods: {', '.join(cls['methods'])}")
        
        if result['functions']:
            print(f"\nFUNCTIONS:")
            for func in result['functions']:
                print(f"  Line {func['lineno']}: {func['signature']}")
                if func['docstring']:
                    print(f"    Docstring: {func['docstring'][:100]}{'...' if len(func['docstring']) > 100 else ''}")


def main():
    """Main entry point."""
    # Get directory from command line or use current directory
    directory = sys.argv[1] if len(sys.argv) > 1 else '.'
    
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory", file=sys.stderr)
        sys.exit(1