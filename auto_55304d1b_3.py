```python
"""
CSV Category Analyzer CLI
========================

A command-line tool for analyzing and categorizing CSV data with customizable rules.
Features include data validation, category assignment, summary statistics, and report generation.

Usage:
    python script.py <csv_file> [options]

Example:
    python script.py data.csv --category-column "department" --rules "sales:revenue>1000,marketing:budget<5000"
    python script.py data.csv --output summary --rules "high:value>100,low:value<=100"
"""

import csv
import argparse
import sys
import os
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter


class CSVCategoryAnalyzer:
    """Main analyzer class for processing CSV data with category rules."""
    
    def __init__(self):
        self.data: List[Dict[str, str]] = []
        self.rules: Dict[str, str] = {}
        self.categories: Dict[str, str] = {}
        
    def load_csv(self, filepath: str) -> None:
        """Load CSV data from file with error handling."""
        try:
            with open(filepath, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                self.data = list(reader)
                if not self.data:
                    raise ValueError("CSV file is empty or has no data rows")
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file not found: {filepath}")
        except csv.Error as e:
            raise ValueError(f"Invalid CSV format: {e}")
    
    def parse_rules(self, rules_string: str) -> None:
        """Parse category rules from string format."""
        try:
            if not rules_string:
                return
            
            for rule_pair in rules_string.split(','):
                if ':' not in rule_pair:
                    continue
                category, condition = rule_pair.split(':', 1)
                self.rules[category.strip()] = condition.strip()
        except Exception as e:
            raise ValueError(f"Invalid rules format: {e}")
    
    def evaluate_condition(self, condition: str, row: Dict[str, str]) -> bool:
        """Evaluate a single condition against a data row."""
        try:
            # Handle different condition formats
            operators = ['>=', '<=', '!=', '==', '>', '<', '=']
            
            for op in operators:
                if op in condition:
                    field, value = condition.split(op, 1)
                    field = field.strip()
                    value = value.strip()
                    
                    if field not in row:
                        return False
                    
                    row_value = row[field].strip()
                    
                    # Try numeric comparison first
                    try:
                        row_num = float(row_value)
                        comp_num = float(value)
                        
                        if op == '>': return row_num > comp_num
                        elif op == '<': return row_num < comp_num
                        elif op == '>=': return row_num >= comp_num
                        elif op == '<=': return row_num <= comp_num
                        elif op == '==' or op == '=': return row_num == comp_num
                        elif op == '!=': return row_num != comp_num
                        
                    except ValueError:
                        # Fall back to string comparison
                        if op == '==' or op == '=': return row_value == value
                        elif op == '!=': return row_value != value
                        else: return False
            
            # If no operator found, treat as equality check
            field_value = condition.split('=')
            if len(field_value) == 2:
                field, value = field_value
                return row.get(field.strip(), '').strip() == value.strip()
            
            return False
            
        except Exception:
            return False
    
    def categorize_data(self, category_column: Optional[str] = None) -> None:
        """Apply category rules to data or use existing category column."""
        for i, row in enumerate(self.data):
            category = 'uncategorized'
            
            if category_column and category_column in row:
                category = row[category_column]
            else:
                # Apply custom rules
                for cat_name, condition in self.rules.items():
                    if self.evaluate_condition(condition, row):
                        category = cat_name
                        break
            
            self.categories[i] = category
    
    def generate_summary_report(self) -> str:
        """Generate summary statistics report."""
        if not self.data:
            return "No data to analyze"
        
        report = []
        report.append("=== CSV CATEGORY ANALYSIS REPORT ===\n")
        
        # Basic statistics
        report.append(f"Total rows: {len(self.data)}")
        report.append(f"Total columns: {len(self.data[0])}")
        report.append(f"Column names: {', '.join(self.data[0].keys())}\n")
        
        # Category distribution
        category_counts = Counter(self.categories.values())
        report.append("Category Distribution:")
        for category, count in category_counts.most_common():
            percentage = (count / len(self.data)) * 100
            report.append(f"  {category}: {count} ({percentage:.1f}%)")
        
        return '\n'.join(report)
    
    def generate_detailed_report(self) -> str:
        """Generate detailed report with categorized data."""
        if not self.data:
            return "No data to analyze"
        
        report = []
        report.append("=== DETAILED CATEGORY REPORT ===\n")
        
        # Group by categories
        categorized_data = defaultdict(list)
        for i, category in self.categories.items():
            categorized_data[category].append((i, self.data[i]))
        
        for category, items in categorized_data.items():
            report.append(f"\n--- {category.upper()} ({len(items)} items) ---")
            for idx, row in items[:5]:  # Show first 5 items per category
                row_summary = ', '.join([f"{k}: {v}" for k, v in list(row.items())[:3]])
                report.append(f"  Row {idx}: {row_summary}")
            if len(items) > 5:
                report.append(f"  ... and {len(items) - 5} more items")
        
        return '\n'.join(report)
    
    def export_categorized_csv(self, output_file: str) -> None:
        """Export data with categories to new CSV file."""
        try:
            fieldnames = list(self.data[0].keys()) + ['category']
            
            with open(output_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                
                for i, row in enumerate(self.data):
                    row_with_category = row.copy()
                    row_with_category['category'] = self.categories.get(i, 'uncategorized')
                    writer.writerow(row_with_category)
                    
            print(f"Categorized data exported to: {output_file}")
            
        except Exception as e:
            raise RuntimeError(f"Failed to export CSV: {e}")


def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Analyze CSV files with customizable category rules",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python script.py data.csv
  python script.py data.csv --rules "high:amount>1000,low:amount<=1000"
  python script.py data.csv --category-column "status" --output detailed
  python script.py data.csv --rules "premium:price>100" --export results.csv
        """
    )
    
    parser.add_argument('csv_file', help='Input CSV file path')
    
    parser