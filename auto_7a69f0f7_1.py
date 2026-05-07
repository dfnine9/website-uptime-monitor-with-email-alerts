```python
"""
AST Code Analysis Script

This script parses Python source files using the Abstract Syntax Tree (AST) module
to extract and analyze code structure including functions, classes, methods, 
docstrings, and type hints. The extracted data is structured into a standardized
JSON format for further analysis or documentation purposes.

Usage: python script.py [file_path]
If no file path is provided, it analyzes itself as a demonstration.
"""

import ast
import json
import sys
import os
from typing import Dict, List, Any, Optional, Union


class CodeAnalyzer:
    """Analyzes Python source code using AST parsing."""
    
    def __init__(self):
        self.analysis_data = {
            'file_info': {},
            'imports': [],
            'classes': [],
            'functions': [],
            'variables': [],
            'docstring': None
        }
    
    def extract_type_hint(self, annotation: Optional[ast.expr]) -> Optional[str]:
        """Extract type hint as string from AST annotation node."""
        if annotation is None:
            return None
        
        try:
            if isinstance(annotation, ast.Name):
                return annotation.id
            elif isinstance(annotation, ast.Constant):
                return str(annotation.value)
            elif isinstance(annotation, ast.Attribute):
                return f"{self.extract_type_hint(annotation.value)}.{annotation.attr}"
            elif isinstance(annotation, ast.Subscript):
                value = self.extract_type_hint(annotation.value)
                slice_val = self.extract_type_hint(annotation.slice)
                return f"{value}[{slice_val}]"
            elif isinstance(annotation, ast.Tuple):
                elements = [self.extract_type_hint(elt) for elt in annotation.elts]
                return f"({', '.join(filter(None, elements))})"
            elif isinstance(annotation, ast.List):
                elements = [self.extract_type_hint(elt) for elt in annotation.elts]
                return f"[{', '.join(filter(None, elements))}]"
            else:
                return ast.unparse(annotation)
        except Exception:
            return "Unknown"
    
    def extract_docstring(self, node: Union[ast.FunctionDef, ast.ClassDef, ast.Module]) -> Optional[str]:
        """Extract docstring from AST node."""
        try:
            if (isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)) and 
                node.body and 
                isinstance(node.body[0], ast.Expr) and 
                isinstance(node.body[0].value, ast.Constant) and 
                isinstance(node.body[0].value.value, str)):
                return node.body[0].value.value
        except (IndexError, AttributeError):
            pass
        return None
    
    def extract_function_info(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """Extract information from a function definition."""
        func_info = {
            'name': node.name,
            'type': 'function',
            'line_number': node.lineno,
            'docstring': self.extract_docstring(node),
            'parameters': [],
            'return_type': self.extract_type_hint(node.returns),
            'decorators': [ast.unparse(dec) for dec in node.decorator_list],
            'is_async': isinstance(node, ast.AsyncFunctionDef)
        }
        
        # Extract parameters with type hints
        for arg in node.args.args:
            param_info = {
                'name': arg.arg,
                'type_hint': self.extract_type_hint(arg.annotation),
                'default': None
            }
            func_info['parameters'].append(param_info)
        
        # Extract default values
        defaults = node.args.defaults
        if defaults:
            param_count = len(func_info['parameters'])
            default_count = len(defaults)
            start_idx = param_count - default_count
            
            for i, default in enumerate(defaults):
                try:
                    if isinstance(default, ast.Constant):
                        func_info['parameters'][start_idx + i]['default'] = default.value
                    else:
                        func_info['parameters'][start_idx + i]['default'] = ast.unparse(default)
                except Exception:
                    func_info['parameters'][start_idx + i]['default'] = "Unknown"
        
        return func_info
    
    def extract_class_info(self, node: ast.ClassDef) -> Dict[str, Any]:
        """Extract information from a class definition."""
        class_info = {
            'name': node.name,
            'type': 'class',
            'line_number': node.lineno,
            'docstring': self.extract_docstring(node),
            'base_classes': [ast.unparse(base) for base in node.bases],
            'decorators': [ast.unparse(dec) for dec in node.decorator_list],
            'methods': [],
            'attributes': []
        }
        
        # Extract methods and class attributes
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_info = self.extract_function_info(item)
                method_info['type'] = 'method'
                class_info['methods'].append(method_info)
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        attr_info = {
                            'name': target.id,
                            'line_number': item.lineno,
                            'type_hint': None
                        }
                        class_info['attributes'].append(attr_info)
            elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                attr_info = {
                    'name': item.target.id,
                    'line_number': item.lineno,
                    'type_hint': self.extract_type_hint(item.annotation)
                }
                class_info['attributes'].append(attr_info)
        
        return class_info
    
    def extract_imports(self, node: Union[ast.Import, ast.ImportFrom]) -> List[Dict[str, Any]]:
        """Extract import information."""
        imports = []
        
        if isinstance(node, ast.Import):
            for alias in node.names:
                import_info = {
                    'type': 'import',
                    'module': alias.name,
                    'alias': alias.asname,
                    'line_number': node.lineno
                }
                imports.append(import_info)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                import_info = {
                    'type': 'from_import',
                    'module': node.module,
                    'name': alias.name,
                    'alias': alias.asname,
                    'line_number': node.lineno
                }
                imports.append(import_info)
        
        return imports
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a Python file and extract code structure."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                source_code = file.read()
            
            # Parse the source code into AST
            tree = ast.parse(source_code, filename=file_path)
            
            # Initialize analysis data
            self.analysis_data = {
                'file_info': {
                    'path': file_path,
                    'name': os.path.basename(file_path),
                    'size': len(source_code),
                    'lines': len(source_code.splitlines())
                },
                'imports': [],
                'classes': [],
                'functions': [],
                'variables': [],
                'docstring': self.extract_docstring(tree)
            }
            
            # Walk through all nodes in the AST
            for node in ast.walk(tree):
                try:
                    if isinstance(node, (ast.