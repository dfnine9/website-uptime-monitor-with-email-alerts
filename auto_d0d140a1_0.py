```python
#!/usr/bin/env python3
"""
File Analyzer and Categorization System

This script scans a directory recursively, analyzes file types and metadata,
identifies content patterns, and creates intelligent categorization rules.
It generates a comprehensive report of file distribution and suggests
organizational strategies based on discovered patterns.

Usage: python script.py [directory_path]
If no directory is provided, current directory is used.

Features:
- File type analysis and statistics
- Metadata extraction (size, dates, permissions)
- Content pattern recognition
- Duplicate detection
- Categorization rule generation
- Directory structure optimization suggestions
"""

import os
import sys
import hashlib
import mimetypes
import json
import re
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime
import stat
import traceback


class FileAnalyzer:
    def __init__(self, root_directory="."):
        self.root_directory = Path(root_directory).resolve()
        self.file_data = []
        self.categories = defaultdict(list)
        self.patterns = defaultdict(int)
        self.duplicates = defaultdict(list)
        self.size_distribution = defaultdict(int)
        
    def get_file_hash(self, filepath):
        """Generate MD5 hash for duplicate detection."""
        try:
            hash_md5 = hashlib.md5()
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except (IOError, OSError):
            return None

    def analyze_content_patterns(self, filepath):
        """Analyze file content for patterns (text files only)."""
        patterns = {
            'config': [r'\.conf$', r'\.cfg$', r'\.ini$', r'config'],
            'log': [r'\.log$', r'\.out$', r'log'],
            'backup': [r'\.bak$', r'\.backup$', r'~$', r'\.old$'],
            'temporary': [r'\.tmp$', r'\.temp$', r'#.*#$'],
            'source_code': [r'\.(py|js|html|css|cpp|c|java|php)$'],
            'data': [r'\.(json|xml|csv|sql|db)$'],
            'media': [r'\.(jpg|png|gif|mp4|mp3|avi|pdf)$'],
            'document': [r'\.(doc|docx|txt|md|pdf)$'],
            'archive': [r'\.(zip|tar|gz|rar|7z)$']
        }
        
        filename = filepath.name.lower()
        matched_patterns = []
        
        for category, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, filename):
                    matched_patterns.append(category)
                    self.patterns[category] += 1
                    break
        
        return matched_patterns if matched_patterns else ['uncategorized']

    def get_size_category(self, size):
        """Categorize file by size."""
        if size < 1024:  # < 1KB
            return 'tiny'
        elif size < 1024 * 1024:  # < 1MB
            return 'small'
        elif size < 1024 * 1024 * 100:  # < 100MB
            return 'medium'
        else:
            return 'large'

    def scan_directory(self):
        """Recursively scan directory and collect file information."""
        print(f"Scanning directory: {self.root_directory}")
        
        for root, dirs, files in os.walk(self.root_directory):
            for filename in files:
                try:
                    filepath = Path(root) / filename
                    
                    # Get file stats
                    file_stats = filepath.stat()
                    
                    # Get MIME type
                    mime_type, _ = mimetypes.guess_type(str(filepath))
                    if not mime_type:
                        mime_type = 'application/octet-stream'
                    
                    # Analyze patterns
                    content_patterns = self.analyze_content_patterns(filepath)
                    
                    # Get file hash for duplicate detection
                    file_hash = self.get_file_hash(filepath)
                    if file_hash:
                        self.duplicates[file_hash].append(str(filepath))
                    
                    # Size categorization
                    size_category = self.get_size_category(file_stats.st_size)
                    self.size_distribution[size_category] += 1
                    
                    file_info = {
                        'path': str(filepath),
                        'name': filename,
                        'extension': filepath.suffix.lower(),
                        'size': file_stats.st_size,
                        'size_category': size_category,
                        'mime_type': mime_type,
                        'created': datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
                        'modified': datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                        'permissions': oct(file_stats.st_mode)[-3:],
                        'content_patterns': content_patterns,
                        'hash': file_hash,
                        'relative_path': str(filepath.relative_to(self.root_directory))
                    }
                    
                    self.file_data.append(file_info)
                    
                    # Categorize by primary pattern
                    primary_category = content_patterns[0]
                    self.categories[primary_category].append(file_info)
                    
                except (OSError, IOError) as e:
                    print(f"Error processing {filepath}: {e}")
                    continue

    def generate_categorization_rules(self):
        """Generate intelligent categorization rules based on patterns."""
        rules = {
            'extension_based': {},
            'size_based': {},
            'pattern_based': {},
            'directory_based': {},
            'date_based': {}
        }
        
        # Extension-based rules
        extensions = Counter(f['extension'] for f in self.file_data if f['extension'])
        for ext, count in extensions.most_common(10):
            if count > 1:
                rules['extension_based'][ext] = {
                    'count': count,
                    'suggested_category': self.get_extension_category(ext),
                    'action': f'Move all {ext} files to {self.get_extension_category(ext)} folder'
                }
        
        # Size-based rules
        for size_cat, count in self.size_distribution.items():
            rules['size_based'][size_cat] = {
                'count': count,
                'action': f'Consider archiving {size_cat} files' if size_cat == 'large' else f'Group {size_cat} files together'
            }
        
        # Pattern-based rules
        for pattern, count in self.patterns.items():
            if count > 2:
                rules['pattern_based'][pattern] = {
                    'count': count,
                    'action': f'Create dedicated folder for {pattern} files'
                }
        
        # Directory depth analysis
        depths = [len(Path(f['relative_path']).parts) for f in self.file_data]
        avg_depth = sum(depths) / len(depths) if depths else 0
        
        rules['directory_based']['structure'] = {
            'average_depth': round(avg_depth, 2),
            'recommendation': 'Flatten structure' if avg_depth > 4 else 'Structure is reasonable'
        }
        
        return rules

    def get_extension_category(self, extension):
        """Map file extension to logical category."""
        mapping = {
            '.txt': 'documents', '.md': 'documents', '.pdf': 'documents',
            '.jpg': 'images', '.png': 'images', '.gif': 'images',
            '.mp3': 'audio', '.wav': 'audio', '.m4a': 'audio',
            '.mp4': 'video', '.avi':