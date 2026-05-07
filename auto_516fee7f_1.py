```python
#!/usr/bin/env python3
"""
CSV Data Validation Module

A comprehensive data validation module that checks CSV format consistency,
handles missing values, and sanitizes input data for processing.

Features:
- CSV format validation (headers, delimiters, row consistency)
- Missing value detection and handling strategies
- Data sanitization (HTML entities, special characters, whitespace)
- Type inference and validation
- Comprehensive error reporting

Usage:
    python script.py

The script will validate sample CSV data and demonstrate all validation features.
"""

import csv
import re
import html
import io
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import json


class CSVValidator:
    """Main CSV validation class with comprehensive data checking capabilities."""
    
    def __init__(self, strict_mode: bool = False):
        """
        Initialize the CSV validator.
        
        Args:
            strict_mode: If True, validation will be more restrictive
        """
        self.strict_mode = strict_mode
        self.validation_errors = []
        self.validation_warnings = []
        self.sanitization_log = []
    
    def validate_csv_format(self, csv_content: str) -> Dict[str, Any]:
        """
        Validate basic CSV format consistency.
        
        Args:
            csv_content: Raw CSV content as string
            
        Returns:
            Dictionary containing validation results
        """
        try:
            # Detect delimiter
            delimiter = self._detect_delimiter(csv_content)
            
            # Parse CSV content
            csv_reader = csv.reader(io.StringIO(csv_content), delimiter=delimiter)
            rows = list(csv_reader)
            
            if not rows:
                self.validation_errors.append("CSV file is empty")
                return {"valid": False, "errors": self.validation_errors}
            
            headers = rows[0]
            data_rows = rows[1:]
            
            # Validate headers
            header_validation = self._validate_headers(headers)
            
            # Validate row consistency
            row_validation = self._validate_row_consistency(data_rows, len(headers))
            
            return {
                "valid": len(self.validation_errors) == 0,
                "delimiter": delimiter,
                "headers": headers,
                "row_count": len(data_rows),
                "column_count": len(headers),
                "header_validation": header_validation,
                "row_validation": row_validation,
                "errors": self.validation_errors,
                "warnings": self.validation_warnings
            }
            
        except Exception as e:
            self.validation_errors.append(f"CSV parsing error: {str(e)}")
            return {"valid": False, "errors": self.validation_errors}
    
    def _detect_delimiter(self, csv_content: str) -> str:
        """Detect the most likely delimiter used in the CSV."""
        sample = csv_content[:1024]  # Use first 1KB for detection
        sniffer = csv.Sniffer()
        
        try:
            dialect = sniffer.sniff(sample, delimiters=',;\t|')
            return dialect.delimiter
        except:
            # Default to comma if detection fails
            return ','
    
    def _validate_headers(self, headers: List[str]) -> Dict[str, Any]:
        """Validate CSV headers for common issues."""
        issues = []
        
        # Check for empty headers
        for i, header in enumerate(headers):
            if not header.strip():
                issues.append(f"Empty header at column {i + 1}")
        
        # Check for duplicate headers
        header_counts = {}
        for header in headers:
            header_counts[header] = header_counts.get(header, 0) + 1
        
        duplicates = [header for header, count in header_counts.items() if count > 1]
        if duplicates:
            issues.append(f"Duplicate headers found: {duplicates}")
        
        # Check for problematic characters in headers
        for header in headers:
            if re.search(r'[^\w\s\-_]', header):
                self.validation_warnings.append(f"Header '{header}' contains special characters")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "header_count": len(headers)
        }
    
    def _validate_row_consistency(self, rows: List[List[str]], expected_columns: int) -> Dict[str, Any]:
        """Validate that all rows have consistent column counts."""
        inconsistent_rows = []
        
        for i, row in enumerate(rows):
            if len(row) != expected_columns:
                inconsistent_rows.append({
                    "row_number": i + 2,  # +2 because of 0-indexing and header row
                    "expected_columns": expected_columns,
                    "actual_columns": len(row)
                })
        
        if inconsistent_rows:
            self.validation_errors.extend([
                f"Row {row['row_number']}: Expected {row['expected_columns']} columns, got {row['actual_columns']}"
                for row in inconsistent_rows
            ])
        
        return {
            "consistent": len(inconsistent_rows) == 0,
            "inconsistent_rows": inconsistent_rows,
            "total_rows": len(rows)
        }
    
    def handle_missing_values(self, csv_content: str, strategy: str = "flag") -> Dict[str, Any]:
        """
        Handle missing values in CSV data.
        
        Args:
            csv_content: Raw CSV content
            strategy: 'flag', 'remove', 'fill_empty', 'fill_default'
            
        Returns:
            Dictionary with missing value analysis and processed data
        """
        try:
            delimiter = self._detect_delimiter(csv_content)
            csv_reader = csv.DictReader(io.StringIO(csv_content), delimiter=delimiter)
            rows = list(csv_reader)
            headers = csv_reader.fieldnames
            
            missing_analysis = self._analyze_missing_values(rows, headers)
            processed_rows = self._apply_missing_value_strategy(rows, headers, strategy)
            
            return {
                "original_row_count": len(rows),
                "processed_row_count": len(processed_rows),
                "missing_analysis": missing_analysis,
                "strategy_applied": strategy,
                "processed_data": processed_rows
            }
            
        except Exception as e:
            self.validation_errors.append(f"Missing value handling error: {str(e)}")
            return {"error": str(e)}
    
    def _analyze_missing_values(self, rows: List[Dict], headers: List[str]) -> Dict[str, Any]:
        """Analyze missing values in the dataset."""
        missing_stats = {}
        total_rows = len(rows)
        
        for header in headers:
            missing_count = 0
            for row in rows:
                value = row.get(header, '').strip()
                if not value or value.lower() in ['null', 'none', 'n/a', 'na', '']:
                    missing_count += 1
            
            missing_stats[header] = {
                "missing_count": missing_count,
                "missing_percentage": (missing_count / total_rows * 100) if total_rows > 0 else 0
            }
        
        return missing_stats
    
    def _apply_missing_value_strategy(self, rows: List[Dict], headers: List[str], strategy: str) -> List[Dict]:
        """Apply the specified missing value handling strategy."""
        processed_rows = []
        
        for row in rows:
            if strategy == "remove":
                # Remove rows with any missing values
                has_missing = any(not row.get(header, '').strip() for header in headers)
                if not has_missing:
                    processed_rows.append(row)
            
            elif strategy == "fill_empty":
                # Fill missing values with empty string
                processed_row = {}
                for header in headers:
                    value = row.get(header, '').strip()
                    processed_row[header] = value if value else ""
                processed_rows.append(processed_