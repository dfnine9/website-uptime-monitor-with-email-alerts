#!/usr/bin/env python3
"""
File Duplicate Finder

This module recursively scans a target directory and generates MD5 hashes for all files
to identify duplicates. It uses only standard library modules for maximum compatibility.

Usage: python script.py [directory_path]
If no directory is specified, it scans the current directory.

The script will:
1. Recursively walk through all subdirectories
2. Calculate MD5 hash for each file
3. Group files by their hash values
4. Report duplicate files found

Output includes:
- Summary of total files scanned
- List of duplicate file groups
- File paths for each duplicate group
"""

import os
import hashlib
import sys
from collections import defaultdict


def calculate_md5(file_path):
    """Calculate MD5 hash of a file.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: MD5 hash in hexadecimal format
        
    Raises:
        IOError: If file cannot be read
    """
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, 'rb') as f:
            # Read file in chunks to handle large files efficiently
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except IOError as e:
        raise IOError(f"Cannot read file {file_path}: {e}")


def scan_directory(target_dir):
    """Recursively scan directory and calculate MD5 hashes for all files.
    
    Args:
        target_dir (str): Directory path to scan
        
    Returns:
        tuple: (file_hashes dict, error_files list, total_files int)
    """
    file_hashes = defaultdict(list)
    error_files = []
    total_files = 0
    
    try:
        for root, dirs, files in os.walk(target_dir):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                total_files += 1
                
                try:
                    file_hash = calculate_md5(file_path)
                    file_hashes[file_hash].append(file_path)
                    print(f"Processed: {file_path}")
                except IOError as e:
                    error_files.append((file_path, str(e)))
                    print(f"Error processing {file_path}: {e}")
                    
    except OSError as e:
        print(f"Error accessing directory {target_dir}: {e}")
        sys.exit(1)
        
    return file_hashes, error_files, total_files


def find_duplicates(file_hashes):
    """Find duplicate files from hash dictionary.
    
    Args:
        file_hashes (dict): Dictionary mapping hashes to file lists
        
    Returns:
        dict: Dictionary containing only duplicate file groups
    """
    duplicates = {}
    for file_hash, file_list in file_hashes.items():
        if len(file_list) > 1:
            duplicates[file_hash] = file_list
    return duplicates


def print_results(duplicates, error_files, total_files, target_dir):
    """Print scan results to stdout.
    
    Args:
        duplicates (dict): Dictionary of duplicate file groups
        error_files (list): List of files that couldn't be processed
        total_files (int): Total number of files scanned
        target_dir (str): Directory that was scanned
    """
    print("\n" + "="*60)
    print("FILE DUPLICATE SCAN RESULTS")
    print("="*60)
    print(f"Directory scanned: {os.path.abspath(target_dir)}")
    print(f"Total files processed: {total_files}")
    print(f"Files with errors: {len(error_files)}")
    print(f"Duplicate groups found: {len(duplicates)}")
    
    if error_files:
        print("\nFiles with errors:")
        print("-" * 30)
        for file_path, error in error_files:
            print(f"  {file_path}: {error}")
    
    if duplicates:
        print("\nDuplicate files found:")
        print("-" * 30)
        for i, (file_hash, file_list) in enumerate(duplicates.items(), 1):
            print(f"\nGroup {i} (MD5: {file_hash}):")
            for file_path in file_list:
                file_size = 0
                try:
                    file_size = os.path.getsize(file_path)
                except OSError:
                    pass
                print(f"  - {file_path} ({file_size} bytes)")
                
        # Calculate space that could be saved
        total_wasted_space = 0
        for file_list in duplicates.values():
            try:
                file_size = os.path.getsize(file_list[0])
                wasted_space = file_size * (len(file_list) - 1)
                total_wasted_space += wasted_space
            except OSError:
                pass
                
        if total_wasted_space > 0:
            print(f"\nPotential space savings: {total_wasted_space:,} bytes "
                  f"({total_wasted_space / (1024*1024):.2f} MB)")
    else:
        print("\nNo duplicate files found!")


def main():
    """Main function to run the duplicate file finder."""
    # Get target directory from command line argument or use current directory
    if len(sys.argv) > 1:
        target_directory = sys.argv[1]
    else:
        target_directory = "."
    
    # Validate directory exists
    if not os.path.isdir(target_directory):
        print(f"Error: '{target_directory}' is not a valid directory")
        sys.exit(1)
    
    print(f"Scanning directory: {os.path.abspath(target_directory)}")
    print("Calculating MD5 hashes for all files...")
    print("-" * 50)
    
    try:
        # Scan directory and calculate hashes
        file_hashes, error_files, total_files = scan_directory(target_directory)
        
        # Find duplicates
        duplicates = find_duplicates(file_hashes)
        
        # Print results
        print_results(duplicates, error_files, total_files, target_directory)
        
    except KeyboardInterrupt:
        print("\nScan interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()