```python
#!/usr/bin/env python3
"""
Python AST Parser for Code Analysis

This module parses Python files using the Abstract Syntax Tree (AST) module
to extract docstrings, function signatures, and class definitions. It provides
a comprehensive analysis of Python code structure without executing the code.

Features:
- Extracts module, class, and function docstrings
- Captures function signatures with parameters, defaults, and type hints
- Identifies class definitions and their methods
- Handles nested classes and functions
- Provides error handling for malformed Python files

Usage:
    python script.py [file_path]
    
If no file path is provided, it analyzes itself as a demonstration.
"""

import ast
import sys
import inspect
from typing import Any, Dict, List, Optional, Union


class PythonASTParser:
    """Parser class for analyzing Python files using AST."""
    
    def __init__(self, file_path: str):
        """Initialize parser with file path."""
        self.file_path = file_path
        self.tree = None
        self.results = {
            'module_docstring': None,
            'classes': [],
            'functions': [],
            'imports': []
        }
    
    def parse_file(self) -> bool:
        """Parse the Python file and build AST."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            self.tree = ast.parse(content)
            return True
            
        except FileNotFoundError:
            print(f"Error: File '{self.file_path}' not found.")
            return False
        except SyntaxError as e:
            print(f"Error: Syntax error in file '{self.file_path}': {e}")
            return False
        except Exception as e:
            print(f"Error: Failed to parse file '{self.file_path}': {e}")
            return False
    
    def get_docstring(self, node: ast.AST) -> Optional[str]:
        """Extract docstring from an AST node."""
        if (isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)) and
            node.body and isinstance(node.body[0], ast.Expr) and
            isinstance(node.body[0].value, ast.Constant) and
            isinstance(node.body[0].value.value, str)):
            return node.body[0].value.value
        return None
    
    def format_function_signature(self, node: ast.FunctionDef) -> str:
        """Format function signature with parameters and type hints."""
        args = []
        
        # Handle regular arguments
        for i, arg in enumerate(node.args.args):
            arg_str = arg.arg
            
            # Add type annotation if present
            if arg.annotation:
                try:
                    arg_str += f": {ast.unparse(arg.annotation)}"
                except:
                    arg_str += ": <annotation>"
            
            # Add default value if present
            defaults_offset = len(node.args.args) - len(node.args.defaults)
            if i >= defaults_offset:
                default_idx = i - defaults_offset
                try:
                    default_val = ast.unparse(node.args.defaults[default_idx])
                    arg_str += f" = {default_val}"
                except:
                    arg_str += " = <default>"
            
            args.append(arg_str)
        
        # Handle *args
        if node.args.vararg:
            vararg_str = f"*{node.args.vararg.arg}"
            if node.args.vararg.annotation:
                try:
                    vararg_str += f": {ast.unparse(node.args.vararg.annotation)}"
                except:
                    vararg_str += ": <annotation>"
            args.append(vararg_str)
        
        # Handle keyword-only arguments
        for i, kwarg in enumerate(node.args.kwonlyargs):
            kwarg_str = kwarg.arg
            if kwarg.annotation:
                try:
                    kwarg_str += f": {ast.unparse(kwarg.annotation)}"
                except:
                    kwarg_str += ": <annotation>"
            
            if i < len(node.args.kw_defaults) and node.args.kw_defaults[i]:
                try:
                    default_val = ast.unparse(node.args.kw_defaults[i])
                    kwarg_str += f" = {default_val}"
                except:
                    kwarg_str += " = <default>"
            
            args.append(kwarg_str)
        
        # Handle **kwargs
        if node.args.kwarg:
            kwarg_str = f"**{node.args.kwarg.arg}"
            if node.args.kwarg.annotation:
                try:
                    kwarg_str += f": {ast.unparse(node.args.kwarg.annotation)}"
                except:
                    kwarg_str += ": <annotation>"
            args.append(kwarg_str)
        
        signature = f"({', '.join(args)})"
        
        # Add return type annotation if present
        if node.returns:
            try:
                signature += f" -> {ast.unparse(node.returns)}"
            except:
                signature += " -> <return_type>"
        
        return signature
    
    def extract_class_info(self, node: ast.ClassDef, parent_class: str = None) -> Dict[str, Any]:
        """Extract information from a class definition."""
        class_name = f"{parent_class}.{node.name}" if parent_class else node.name
        
        class_info = {
            'name': class_name,
            'docstring': self.get_docstring(node),
            'base_classes': [],
            'methods': [],
            'nested_classes': []
        }
        
        # Extract base classes
        for base in node.bases:
            try:
                class_info['base_classes'].append(ast.unparse(base))
            except:
                class_info['base_classes'].append('<base_class>')
        
        # Extract methods and nested classes
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = {
                    'name': item.name,
                    'signature': self.format_function_signature(item),
                    'docstring': self.get_docstring(item),
                    'is_method': True
                }
                class_info['methods'].append(method_info)
            elif isinstance(item, ast.ClassDef):
                nested_class = self.extract_class_info(item, class_name)
                class_info['nested_classes'].append(nested_class)
        
        return class_info
    
    def analyze(self) -> Dict[str, Any]:
        """Analyze the parsed AST and extract relevant information."""
        if not self.tree:
            return self.results
        
        # Extract module docstring
        self.results['module_docstring'] = self.get_docstring(self.tree)
        
        # Walk through AST nodes
        for node in ast.walk(self.tree):
            try:
                if isinstance(node, ast.ClassDef):
                    # Check if this is a top-level class (not nested)
                    if any(node in child.body if hasattr(child, 'body') else False 
                          for child in ast.walk(self.tree) 
                          if isinstance(child, (ast.ClassDef, ast.FunctionDef)) and child != node):
                        continue
                    
                    class_info = self.extract_class_info(node)
                    self.results['classes'].append(class_info)
                
                elif isinstance(node, ast.FunctionDef):
                    # Check if this is a top-level function (not a method or nested)
                    if any(node in child.body if hasattr(child, 'body') else False 
                          for child in ast.walk(self.tree) 
                          if isinstance(child, (ast.ClassDef, ast.FunctionDef)) and child != node):
                        continue