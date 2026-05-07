```python
"""
Task Data Parser and Analyzer

This module reads task data from text files and JSON APIs, then parses task descriptions
to extract deadlines and dependencies using regex patterns and date parsing libraries.
It processes various date formats and identifies task dependencies through pattern matching.

Features:
- Reads from local text files and remote JSON APIs
- Extracts deadlines using multiple date format patterns
- Identifies task dependencies through keyword matching
- Handles errors gracefully with comprehensive exception handling
- Outputs structured results to stdout

Usage: python script.py
"""

import json
import re
import os
import sys
from datetime import datetime, timedelta
from urllib.parse import urlparse
import httpx


class TaskParser:
    def __init__(self):
        # Date patterns for various formats
        self.date_patterns = [
            r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b',  # MM/DD/YYYY or MM-DD-YYYY
            r'\b(\d{4}[/-]\d{1,2}[/-]\d{1,2})\b',    # YYYY/MM/DD or YYYY-MM-DD
            r'\b(\w+ \d{1,2},? \d{4})\b',            # Month DD, YYYY
            r'\b(\d{1,2} \w+ \d{4})\b',              # DD Month YYYY
            r'\bby (\w+day)\b',                      # by Monday/Tuesday etc
            r'\bin (\d+) days?\b',                   # in 5 days
            r'\bnext (\w+)\b',                       # next week/month
        ]
        
        # Dependency keywords and patterns
        self.dependency_patterns = [
            r'\bdepends on (.+?)(?:\.|$)',
            r'\brequires (.+?)(?:\.|$)',
            r'\bafter (.+?)(?:\.|$)',
            r'\bwaiting for (.+?)(?:\.|$)',
            r'\bblocked by (.+?)(?:\.|$)',
            r'\bneeds (.+?)(?:\.|$)',
        ]
        
        # Common date formats for parsing
        self.date_formats = [
            '%m/%d/%Y', '%m-%d-%Y', '%m/%d/%y', '%m-%d-%y',
            '%Y/%m/%d', '%Y-%m-%d',
            '%B %d, %Y', '%B %d %Y',
            '%d %B %Y', '%d %b %Y'
        ]

    def parse_date(self, date_string):
        """Parse various date formats and return datetime object"""
        if not date_string:
            return None
            
        date_string = date_string.strip()
        
        # Handle relative dates
        if 'in' in date_string.lower() and 'days' in date_string.lower():
            try:
                days = int(re.search(r'(\d+)', date_string).group(1))
                return datetime.now() + timedelta(days=days)
            except:
                pass
                
        if 'next week' in date_string.lower():
            return datetime.now() + timedelta(days=7)
            
        if 'next month' in date_string.lower():
            return datetime.now() + timedelta(days=30)
            
        # Handle weekday references
        weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for day in weekdays:
            if day in date_string.lower():
                # Find next occurrence of this weekday
                today = datetime.now()
                days_ahead = weekdays.index(day) - today.weekday()
                if days_ahead <= 0:
                    days_ahead += 7
                return today + timedelta(days=days_ahead)
        
        # Try standard date formats
        for fmt in self.date_formats:
            try:
                return datetime.strptime(date_string, fmt)
            except ValueError:
                continue
                
        return None

    def extract_deadlines(self, text):
        """Extract all potential deadlines from text"""
        deadlines = []
        
        for pattern in self.date_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                date_str = match.group(1) if match.groups() else match.group(0)
                parsed_date = self.parse_date(date_str)
                if parsed_date:
                    deadlines.append({
                        'raw_text': date_str,
                        'parsed_date': parsed_date,
                        'context': text[max(0, match.start()-20):match.end()+20].strip()
                    })
                    
        return deadlines

    def extract_dependencies(self, text):
        """Extract task dependencies from text"""
        dependencies = []
        
        for pattern in self.dependency_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                dependency = match.group(1).strip()
                # Clean up common punctuation and conjunctions
                dependency = re.sub(r'\b(and|or|the|a|an)\b', ' ', dependency, flags=re.IGNORECASE)
                dependency = re.sub(r'[,;.]$', '', dependency).strip()
                if dependency:
                    dependencies.append({
                        'dependency': dependency,
                        'type': self.classify_dependency_type(match.group(0)),
                        'context': text[max(0, match.start()-20):match.end()+20].strip()
                    })
                    
        return dependencies

    def classify_dependency_type(self, match_text):
        """Classify the type of dependency based on the matched text"""
        match_text = match_text.lower()
        if 'depends on' in match_text:
            return 'depends_on'
        elif 'requires' in match_text:
            return 'requires'
        elif 'after' in match_text:
            return 'sequential'
        elif 'waiting for' in match_text:
            return 'waiting'
        elif 'blocked by' in match_text:
            return 'blocked'
        elif 'needs' in match_text:
            return 'needs'
        return 'generic'

    def read_text_file(self, filepath):
        """Read and return content from a text file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error reading file {filepath}: {e}")
            return None

    def fetch_json_api(self, url):
        """Fetch data from a JSON API endpoint"""
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(url)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"Error fetching from API {url}: {e}")
            return None

    def parse_task_data(self, data, source_type, source_path):
        """Parse task data and extract deadlines and dependencies"""
        tasks = []
        
        if source_type == 'text':
            # Treat entire text as one task or split by common delimiters
            task_sections = re.split(r'\n\s*\n|\n-{3,}|\n={3,}', data)
            for i, section in enumerate(task_sections):
                if section.strip():
                    task = {
                        'id': f"{source_path}_task_{i+1}",
                        'description': section.strip(),
                        'deadlines': self.extract_deadlines(section),
                        'dependencies': self.extract_dependencies(section),
                        'source': source_path,
                        'source_type': source_type
                    }
                    tasks.append(task)
                    
        elif source_type == 'json':
            # Handle different JSON structures
            if isinstance(data, list):
                for i, item in enumerate(data):
                    task = self.process_json_item(item, f"{source_path