```python
#!/usr/bin/env python3
"""
File Organization Script

This script scans target directories and organizes files into categorized folders
based on file extensions and date rules. It uses the standard library modules
os and shutil to perform file operations safely with comprehensive error handling.

Features:
- Scans specified directories for files
- Categorizes files by extension type (documents, images, videos, etc.)
- Organizes files by modification date (year/month structure)
- Creates necessary directory structures automatically
- Provides detailed logging of all operations
- Handles errors gracefully without stopping execution

Usage: python script.py
"""

import os
import shutil
import datetime
from pathlib import Path
import sys


class FileOrganizer:
    def __init__(self, source_dir=None, target_dir=None):
        """Initialize the file organizer with source and target directories."""
        self.source_dir = source_dir or os.path.expanduser("~/Downloads")
        self.target_dir = target_dir or os.path.expanduser("~/OrganizedFiles")
        
        # File extension categories
        self.categories = {
            'documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx'],
            'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.tiff', '.webp'],
            'videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'],
            'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'],
            'archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz'],
            'code': ['.py', '.js', '.html', '.css', '.cpp', '.java', '.php', '.rb', '.go'],
            'data': ['.json', '.xml', '.csv', '.sql', '.db', '.sqlite']
        }
        
        self.stats = {
            'processed': 0,
            'moved': 0,
            'errors': 0,
            'skipped': 0
        }
    
    def get_file_category(self, file_path):
        """Determine the category of a file based on its extension."""
        extension = os.path.splitext(file_path)[1].lower()
        
        for category, extensions in self.categories.items():
            if extension in extensions:
                return category
        
        return 'miscellaneous'
    
    def get_file_date_info(self, file_path):
        """Get the modification date information for organizing by date."""
        try:
            mod_time = os.path.getmtime(file_path)
            date_obj = datetime.datetime.fromtimestamp(mod_time)
            return date_obj.year, date_obj.strftime("%m-%B")
        except Exception as e:
            print(f"Warning: Could not get date info for {file_path}: {e}")
            current_date = datetime.datetime.now()
            return current_date.year, current_date.strftime("%m-%B")
    
    def create_target_directory(self, category, year, month):
        """Create the target directory structure if it doesn't exist."""
        target_path = os.path.join(self.target_dir, category, str(year), month)
        
        try:
            os.makedirs(target_path, exist_ok=True)
            return target_path
        except Exception as e:
            print(f"Error creating directory {target_path}: {e}")
            return None
    
    def move_file(self, source_path, target_dir, filename):
        """Move a file to the target directory with collision handling."""
        target_path = os.path.join(target_dir, filename)
        
        # Handle filename collisions
        if os.path.exists(target_path):
            base_name, extension = os.path.splitext(filename)
            counter = 1
            
            while os.path.exists(target_path):
                new_filename = f"{base_name}_{counter}{extension}"
                target_path = os.path.join(target_dir, new_filename)
                counter += 1
        
        try:
            shutil.move(source_path, target_path)
            return target_path
        except Exception as e:
            print(f"Error moving {source_path} to {target_path}: {e}")
            return None
    
    def scan_and_organize(self):
        """Main method to scan source directory and organize files."""
        print(f"Starting file organization...")
        print(f"Source directory: {self.source_dir}")
        print(f"Target directory: {self.target_dir}")
        print("-" * 50)
        
        if not os.path.exists(self.source_dir):
            print(f"Error: Source directory {self.source_dir} does not exist!")
            return False
        
        try:
            # Create main target directory
            os.makedirs(self.target_dir, exist_ok=True)
            
            # Walk through all files in source directory
            for root, dirs, files in os.walk(self.source_dir):
                for filename in files:
                    source_path = os.path.join(root, filename)
                    self.stats['processed'] += 1
                    
                    try:
                        # Skip if it's the same as target directory
                        if os.path.commonpath([source_path, self.target_dir]) == self.target_dir:
                            self.stats['skipped'] += 1
                            continue
                        
                        # Get file category and date info
                        category = self.get_file_category(filename)
                        year, month = self.get_file_date_info(source_path)
                        
                        # Create target directory
                        target_dir = self.create_target_directory(category, year, month)
                        if not target_dir:
                            self.stats['errors'] += 1
                            continue
                        
                        # Move the file
                        new_path = self.move_file(source_path, target_dir, filename)
                        if new_path:
                            self.stats['moved'] += 1
                            print(f"Moved: {filename} -> {category}/{year}/{month}/")
                        else:
                            self.stats['errors'] += 1
                    
                    except Exception as e:
                        print(f"Error processing {filename}: {e}")
                        self.stats['errors'] += 1
                        continue
        
        except Exception as e:
            print(f"Critical error during organization: {e}")
            return False
        
        return True
    
    def print_summary(self):
        """Print a summary of the organization process."""
        print("\n" + "=" * 50)
        print("FILE ORGANIZATION SUMMARY")
        print("=" * 50)
        print(f"Files processed: {self.stats['processed']}")
        print(f"Files moved: {self.stats['moved']}")
        print(f"Files skipped: {self.stats['skipped']}")
        print(f"Errors encountered: {self.stats['errors']}")
        print(f"Target directory: {self.target_dir}")
        
        if self.stats['moved'] > 0:
            print(f"\nSuccess rate: {(self.stats['moved'] / self.stats['processed']) * 100:.1f}%")
        
        print("\nDirectory structure created:")
        try:
            for category in os.listdir(self.target_dir):
                category_path = os.path.join(self.target_dir, category)
                if os.path.isdir(category_path):
                    print(f"  📁 {category}/")
                    for year in sorted(os.listdir(category_path)):
                        year_path = os.path.join(category_path, year)
                        if os.path.isdir(year_path):
                            print(f"    📁 {year}/")
                            for month in sorted(os.listdir(year_path)):
                                month_path = os.path.join(year_path