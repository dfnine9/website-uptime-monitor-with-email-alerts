#!/usr/bin/env python3
"""
Duplicate File Finder using MD5 Hashing

This script recursively walks through directories starting from the current working directory
and generates MD5 hashes for all files to identify duplicates. It uses only Python's
standard library (hashlib, os, sys, collections) to maintain self-containment.

The script will:
1. Traverse all subdirectories from the starting point
2. Calculate MD5 hash for each file encountered
3. Group files by their hash values
4. Report any duplicate files found
5. Provide summary statistics

Usage: python script.py
"""

import hashlib
import os
import sys
from collections import defaultdict


def calculate_md5(filepath):
    """
    Calculate MD5 hash of a file.
    
    Args:
        filepath (str): Path to the file
        
    Returns:
        str: MD5 hash as hexadecimal string, or None if error occurred
    """
    try:
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            # Read file in chunks to handle large files efficiently
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except (IOError, OSError, PermissionError) as e:
        print(f"Error reading file {filepath}: {e}", file=sys.stderr)
        return None


def find_duplicates(start_path="."):
    """
    Walk through directories and find duplicate files based on MD5 hash.
    
    Args:
        start_path (str): Starting directory path (defaults to current directory)
        
    Returns:
        tuple: (hash_to_files dict, total_files_processed, errors_encountered)
    """
    hash_to_files = defaultdict(list)
    total_files = 0
    error_count = 0
    
    try:
        for root, dirs, files in os.walk(start_path):
            for filename in files:
                filepath = os.path.join(root, filename)
                total_files += 1
                
                # Calculate hash
                file_hash = calculate_md5(filepath)
                if file_hash is not None:
                    hash_to_files[file_hash].append(filepath)
                else:
                    error_count += 1
                    
                # Progress indicator for large directories
                if total_files % 100 == 0:
                    print(f"Processed {total_files} files...", file=sys.stderr)
                    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error during directory traversal: {e}", file=sys.stderr)
        sys.exit(1)
        
    return hash_to_files, total_files, error_count


def main():
    """Main function to orchestrate duplicate file detection."""
    print("=== Duplicate File Finder ===")
    print(f"Starting scan from: {os.path.abspath('.')}")
    print()
    
    try:
        # Find all files and their hashes
        hash_to_files, total_files, error_count = find_duplicates()
        
        # Filter for duplicates only
        duplicates = {hash_val: files for hash_val, files in hash_to_files.items() if len(files) > 1}
        
        # Report results
        print(f"\n=== SCAN RESULTS ===")
        print(f"Total files processed: {total_files}")
        print(f"Errors encountered: {error_count}")
        print(f"Unique file hashes: {len(hash_to_files)}")
        print(f"Duplicate groups found: {len(duplicates)}")
        
        if duplicates:
            print(f"\n=== DUPLICATE FILES ===")
            duplicate_file_count = 0
            
            for hash_value, file_list in duplicates.items():
                duplicate_file_count += len(file_list)
                print(f"\nMD5: {hash_value}")
                print(f"Files ({len(file_list)}):")
                for filepath in sorted(file_list):
                    try:
                        file_size = os.path.getsize(filepath)
                        print(f"  - {filepath} ({file_size:,} bytes)")
                    except OSError:
                        print(f"  - {filepath} (size unavailable)")
            
            print(f"\n=== SUMMARY ===")
            print(f"Total duplicate files: {duplicate_file_count}")
            print(f"Storage waste: Files in {len(duplicates)} groups could be deduplicated")
            
        else:
            print("\nNo duplicate files found!")
            
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()