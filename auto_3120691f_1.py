```python
"""
CSV Monitoring Logger with Rotation and Backup

This module implements a robust CSV logging system for monitoring results with:
- Timestamped entries with configurable fields
- File rotation based on size or age
- Automatic backup creation to prevent data loss
- Atomic write operations to prevent corruption
- Comprehensive error handling and recovery

Usage:
    python script.py

The script demonstrates logging monitoring results with automatic rotation
when files exceed size limits or age thresholds.
"""

import csv
import os
import shutil
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import tempfile
import json


class CSVMonitoringLogger:
    """
    Thread-safe CSV logger with rotation and backup capabilities.
    """
    
    def __init__(self, 
                 log_file: str = "monitoring.csv",
                 max_size_mb: int = 10,
                 max_age_days: int = 7,
                 backup_count: int = 5,
                 fieldnames: Optional[List[str]] = None):
        """
        Initialize the CSV monitoring logger.
        
        Args:
            log_file: Path to the main log file
            max_size_mb: Maximum file size in MB before rotation
            max_age_days: Maximum age in days before rotation
            backup_count: Number of backup files to keep
            fieldnames: CSV column headers (default includes common monitoring fields)
        """
        self.log_file = Path(log_file)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.max_age_days = max_age_days
        self.backup_count = backup_count
        self.lock = threading.Lock()
        
        # Default fieldnames for monitoring data
        self.fieldnames = fieldnames or [
            'timestamp',
            'level',
            'component',
            'metric_name',
            'metric_value',
            'status',
            'message',
            'details'
        ]
        
        # Ensure log directory exists
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize CSV file with headers if it doesn't exist
        self._initialize_csv()
    
    def _initialize_csv(self):
        """Initialize CSV file with headers if it doesn't exist."""
        try:
            if not self.log_file.exists():
                with open(self.log_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                    writer.writeheader()
                print(f"Initialized CSV log file: {self.log_file}")
        except Exception as e:
            print(f"Error initializing CSV file: {e}")
            raise
    
    def _should_rotate(self) -> bool:
        """Check if log file should be rotated based on size or age."""
        try:
            if not self.log_file.exists():
                return False
            
            # Check file size
            if self.log_file.stat().st_size > self.max_size_bytes:
                return True
            
            # Check file age
            file_age = datetime.now() - datetime.fromtimestamp(self.log_file.stat().st_mtime)
            if file_age > timedelta(days=self.max_age_days):
                return True
            
            return False
        except Exception as e:
            print(f"Error checking rotation criteria: {e}")
            return False
    
    def _create_backup_filename(self) -> str:
        """Create a timestamped backup filename."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = self.log_file.stem
        extension = self.log_file.suffix
        return f"{base_name}_{timestamp}{extension}"
    
    def _rotate_log(self):
        """Rotate the current log file and manage backups."""
        try:
            if not self.log_file.exists():
                return
            
            # Create backup filename
            backup_name = self._create_backup_filename()
            backup_path = self.log_file.parent / backup_name
            
            # Move current log to backup
            shutil.move(str(self.log_file), str(backup_path))
            print(f"Rotated log file to: {backup_path}")
            
            # Clean old backups
            self._cleanup_old_backups()
            
            # Initialize new log file
            self._initialize_csv()
            
        except Exception as e:
            print(f"Error during log rotation: {e}")
            # Try to restore the original file if rotation failed
            try:
                if backup_path.exists() and not self.log_file.exists():
                    shutil.move(str(backup_path), str(self.log_file))
            except:
                pass
            raise
    
    def _cleanup_old_backups(self):
        """Remove old backup files beyond the backup count limit."""
        try:
            # Find all backup files
            base_name = self.log_file.stem
            extension = self.log_file.suffix
            pattern = f"{base_name}_*{extension}"
            
            backup_files = list(self.log_file.parent.glob(pattern))
            
            # Sort by modification time (newest first)
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Remove excess backups
            for backup_file in backup_files[self.backup_count:]:
                try:
                    backup_file.unlink()
                    print(f"Removed old backup: {backup_file}")
                except Exception as e:
                    print(f"Error removing backup {backup_file}: {e}")
        
        except Exception as e:
            print(f"Error cleaning up backups: {e}")
    
    def _atomic_write(self, data: Dict[str, Any]):
        """Write data atomically to prevent corruption."""
        temp_file = None
        try:
            # Create temporary file in the same directory
            with tempfile.NamedTemporaryFile(
                mode='w', 
                newline='',
                encoding='utf-8',
                dir=self.log_file.parent,
                delete=False
            ) as temp_file:
                temp_path = Path(temp_file.name)
                
                # If original file exists, copy its content first
                if self.log_file.exists():
                    with open(self.log_file, 'r', encoding='utf-8') as original:
                        temp_file.write(original.read())
                else:
                    # Write headers for new file
                    writer = csv.DictWriter(temp_file, fieldnames=self.fieldnames)
                    writer.writeheader()
                
                # Append new data
                writer = csv.DictWriter(temp_file, fieldnames=self.fieldnames)
                writer.writerow(data)
            
            # Atomically replace the original file
            temp_path.replace(self.log_file)
            
        except Exception as e:
            # Clean up temporary file if it exists
            if temp_file and hasattr(temp_file, 'name'):
                try:
                    Path(temp_file.name).unlink(missing_ok=True)
                except:
                    pass
            raise e
    
    def log(self, 
            level: str = "INFO",
            component: str = "",
            metric_name: str = "",
            metric_value: Any = "",
            status: str = "OK",
            message: str = "",
            **kwargs):
        """
        Log a monitoring entry with automatic rotation and backup.
        
        Args:
            level: Log level (INFO, WARN, ERROR, etc.)
            component: System component being monitored
            metric_name: Name of the metric being logged
            metric_value: Value of the metric
            status: Status (OK, WARN, ERROR, etc.)
            message: Human-readable message
            **kwargs: Additional fields to log
        """
        with self.lock:
            try:
                # Check if rotation is needed
                if self._should_rotate():
                    self._rotate_log()