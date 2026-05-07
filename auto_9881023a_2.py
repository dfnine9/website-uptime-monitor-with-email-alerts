```python
"""
Function Example Generator

This module analyzes Python function signatures and automatically generates
realistic usage examples with sample inputs and expected outputs. It uses
introspection to examine function parameters, types, and docstrings to create
comprehensive examples that demonstrate proper function usage.

The generator supports:
- Functions with various parameter types (int, str, float, bool, list, dict)
- Default parameters and keyword arguments
- Type hints and annotations
- Docstring parsing for context
- Error handling for edge cases

Usage:
    python script.py

The script will demonstrate example generation on several sample functions
and print the results to stdout.
"""

import inspect
import ast
import random
import string
from typing import Any, Dict, List, Tuple, Union, Optional, get_type_hints
import re


class FunctionExampleGenerator:
    """Generates realistic usage examples for Python functions."""
    
    def __init__(self):
        self.sample_data = {
            'str': ['hello', 'world', 'test', 'example', 'data', 'python', 'code'],
            'int': [1, 5, 10, 42, 100, -1, 0],
            'float': [1.0, 3.14, 2.5, -1.5, 0.0, 99.9],
            'bool': [True, False],
            'list': [[1, 2, 3], ['a', 'b', 'c'], [], [1, 'mixed', 3.14]],
            'dict': [{'key': 'value'}, {}, {'a': 1, 'b': 2}, {'nested': {'key': 'val'}}]
        }
    
    def _get_type_name(self, annotation: Any) -> str:
        """Extract type name from annotation."""
        if hasattr(annotation, '__name__'):
            return annotation.__name__
        elif hasattr(annotation, '_name'):
            return annotation._name
        elif str(annotation).startswith('typing.'):
            # Handle typing module types
            type_str = str(annotation)
            if 'Union' in type_str:
                return 'Union'
            elif 'List' in type_str:
                return 'list'
            elif 'Dict' in type_str:
                return 'dict'
            elif 'Optional' in type_str:
                return 'Optional'
        return str(annotation)
    
    def _generate_sample_value(self, param_type: str, param_name: str) -> Any:
        """Generate a sample value based on parameter type and name."""
        param_name_lower = param_name.lower()
        
        # Type-specific generation
        if param_type in self.sample_data:
            return random.choice(self.sample_data[param_type])
        
        # Name-based heuristics
        if 'name' in param_name_lower:
            return random.choice(['Alice', 'Bob', 'Charlie', 'Diana'])
        elif 'email' in param_name_lower:
            return f"{random.choice(['user', 'test', 'admin'])}@example.com"
        elif 'url' in param_name_lower:
            return 'https://example.com'
        elif 'path' in param_name_lower or 'file' in param_name_lower:
            return '/path/to/file.txt'
        elif 'count' in param_name_lower or 'num' in param_name_lower:
            return random.choice([1, 5, 10])
        elif 'size' in param_name_lower or 'length' in param_name_lower:
            return random.choice([10, 50, 100])
        elif 'id' in param_name_lower:
            return random.randint(1000, 9999)
        
        # Default fallbacks
        if param_type == 'str' or 'str' in param_type:
            return f"sample_{param_name}"
        elif param_type in ['int', 'integer'] or 'int' in param_type:
            return random.choice(self.sample_data['int'])
        elif param_type == 'float' or 'float' in param_type:
            return random.choice(self.sample_data['float'])
        elif param_type == 'bool' or 'bool' in param_type:
            return random.choice(self.sample_data['bool'])
        elif param_type == 'list' or 'list' in param_type.lower():
            return random.choice(self.sample_data['list'])
        elif param_type == 'dict' or 'dict' in param_type.lower():
            return random.choice(self.sample_data['dict'])
        
        # Unknown type fallback
        return f"<{param_type}_value>"
    
    def _extract_examples_from_docstring(self, docstring: str) -> List[str]:
        """Extract existing examples from function docstring."""
        if not docstring:
            return []
        
        examples = []
        lines = docstring.split('\n')
        in_example = False
        current_example = []
        
        for line in lines:
            line = line.strip()
            if 'example' in line.lower() or '>>>' in line:
                in_example = True
                if '>>>' in line:
                    current_example.append(line)
            elif in_example:
                if line and not line.startswith('>>>') and not line.startswith('...'):
                    if current_example:
                        examples.append('\n'.join(current_example))
                        current_example = []
                    in_example = False
                else:
                    current_example.append(line)
        
        if current_example:
            examples.append('\n'.join(current_example))
        
        return examples
    
    def analyze_function(self, func) -> Dict[str, Any]:
        """Analyze function signature and metadata."""
        try:
            sig = inspect.signature(func)
            type_hints = get_type_hints(func) if hasattr(func, '__annotations__') else {}
            
            analysis = {
                'name': func.__name__,
                'signature': str(sig),
                'docstring': inspect.getdoc(func),
                'parameters': [],
                'return_type': None,
                'existing_examples': []
            }
            
            # Analyze parameters
            for param_name, param in sig.parameters.items():
                param_info = {
                    'name': param_name,
                    'annotation': param.annotation,
                    'default': param.default,
                    'has_default': param.default != inspect.Parameter.empty,
                    'kind': param.kind
                }
                
                # Get type information
                if param_name in type_hints:
                    param_info['type'] = self._get_type_name(type_hints[param_name])
                elif param.annotation != inspect.Parameter.empty:
                    param_info['type'] = self._get_type_name(param.annotation)
                else:
                    param_info['type'] = 'Any'
                
                analysis['parameters'].append(param_info)
            
            # Get return type
            if 'return' in type_hints:
                analysis['return_type'] = self._get_type_name(type_hints['return'])
            elif sig.return_annotation != inspect.Signature.empty:
                analysis['return_type'] = self._get_type_name(sig.return_annotation)
            
            # Extract existing examples
            if analysis['docstring']:
                analysis['existing_examples'] = self._extract_examples_from_docstring(analysis['docstring'])
            
            return analysis
            
        except Exception as e:
            return {'error': f"Failed to analyze function: {str(e)}"}
    
    def generate_examples(self, func, num_examples: int = 3) -> List[Dict[str, Any]]:
        """Generate usage examples for a function."""
        analysis = self.analyze_function(func)
        
        if 'error' in analysis:
            return [{'error': analysis['error']}]
        
        examples = []
        
        try:
            for i in range(num_examples):
                example = {
                    'example_