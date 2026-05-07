```python
"""
System Uptime and Performance Reporting Module

This module analyzes historical CSV data to calculate uptime percentages and performance metrics.
It processes CSV files containing system monitoring data with timestamps, status codes, and response times,
then generates comprehensive HTML reports with statistics and basic ASCII charts.

CSV Format Expected:
timestamp,status_code,response_time_ms
2024-01-01 00:00:00,200,150
2024-01-01 01:00:00,500,3000
...

Features:
- Daily and weekly uptime percentage calculations
- Average response time analysis
- HTML report generation with embedded CSS
- Error handling for malformed data
- Self-contained implementation using only standard library
"""

import csv
import json
import os
import sys
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from statistics import mean, median
from typing import Dict, List, Tuple, Optional
import traceback

class UptimeReporter:
    """Main class for processing uptime data and generating reports."""
    
    def __init__(self):
        self.data = []
        self.daily_stats = defaultdict(list)
        self.weekly_stats = defaultdict(list)
        
    def load_csv_data(self, filepath: str) -> bool:
        """Load and parse CSV data from file."""
        try:
            with open(filepath, 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    try:
                        timestamp = datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S')
                        status_code = int(row['status_code'])
                        response_time = float(row['response_time_ms'])
                        
                        self.data.append({
                            'timestamp': timestamp,
                            'status_code': status_code,
                            'response_time': response_time,
                            'is_up': status_code < 400
                        })
                    except (ValueError, KeyError) as e:
                        print(f"Skipping malformed row: {row} - Error: {e}")
                        continue
                        
            print(f"Loaded {len(self.data)} data points from {filepath}")
            return len(self.data) > 0
            
        except FileNotFoundError:
            print(f"Error: File {filepath} not found")
            return False
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return False
    
    def generate_sample_data(self, filename: str = "sample_data.csv") -> str:
        """Generate sample CSV data for demonstration."""
        try:
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['timestamp', 'status_code', 'response_time_ms'])
                
                start_date = datetime.now() - timedelta(days=30)
                
                for i in range(2160):  # 30 days * 24 hours * 3 checks per hour
                    timestamp = start_date + timedelta(minutes=i*20)
                    
                    # Simulate 95% uptime
                    if i % 20 == 0:  # 5% downtime
                        status_code = 500
                        response_time = 5000
                    else:
                        status_code = 200
                        response_time = 150 + (i % 100)  # Vary response times
                    
                    writer.writerow([
                        timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        status_code,
                        response_time
                    ])
            
            print(f"Generated sample data file: {filename}")
            return filename
            
        except Exception as e:
            print(f"Error generating sample data: {e}")
            return ""
    
    def calculate_daily_stats(self):
        """Calculate daily uptime and performance statistics."""
        for entry in self.data:
            date_key = entry['timestamp'].strftime('%Y-%m-%d')
            self.daily_stats[date_key].append(entry)
    
    def calculate_weekly_stats(self):
        """Calculate weekly uptime and performance statistics."""
        for entry in self.data:
            # Get Monday of the week
            monday = entry['timestamp'] - timedelta(days=entry['timestamp'].weekday())
            week_key = monday.strftime('%Y-%m-%d')
            self.weekly_stats[week_key].append(entry)
    
    def get_uptime_percentage(self, entries: List[Dict]) -> float:
        """Calculate uptime percentage for a list of entries."""
        if not entries:
            return 0.0
        
        up_count = sum(1 for entry in entries if entry['is_up'])
        return (up_count / len(entries)) * 100
    
    def get_avg_response_time(self, entries: List[Dict]) -> float:
        """Calculate average response time for a list of entries."""
        if not entries:
            return 0.0
        
        up_entries = [entry for entry in entries if entry['is_up']]
        if not up_entries:
            return 0.0
        
        return mean(entry['response_time'] for entry in up_entries)
    
    def create_ascii_chart(self, data: Dict[str, float], title: str, max_width: int = 50) -> str:
        """Create a simple ASCII bar chart."""
        if not data:
            return f"{title}\nNo data available\n"
        
        chart = f"\n{title}\n" + "=" * len(title) + "\n"
        
        max_value = max(data.values()) if data.values() else 1
        
        for key, value in list(data.items())[-10:]:  # Show last 10 entries
            bar_length = int((value / max_value) * max_width)
            bar = "█" * bar_length
            chart += f"{key[:10]:<10} |{bar:<{max_width}} {value:.1f}\n"
        
        return chart + "\n"
    
    def generate_html_report(self, output_file: str = "uptime_report.html"):
        """Generate comprehensive HTML report."""
        try:
            # Calculate statistics
            self.calculate_daily_stats()
            self.calculate_weekly_stats()
            
            # Prepare data for charts
            daily_uptime = {}
            daily_response = {}
            weekly_uptime = {}
            weekly_response = {}
            
            for date, entries in self.daily_stats.items():
                daily_uptime[date] = self.get_uptime_percentage(entries)
                daily_response[date] = self.get_avg_response_time(entries)
            
            for week, entries in self.weekly_stats.items():
                weekly_uptime[week] = self.get_uptime_percentage(entries)
                weekly_response[week] = self.get_avg_response_time(entries)
            
            # Overall statistics
            overall_uptime = self.get_uptime_percentage(self.data)
            overall_avg_response = self.get_avg_response_time(self.data)
            total_checks = len(self.data)
            
            # Status code distribution
            status_codes = Counter(entry['status_code'] for entry in self.data)
            
            # Generate HTML
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>System Uptime Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                    .container {{ background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    h1 {{ color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }}
                    h2 {{ color: #555; margin-top: 30px; }}
                    .metric {{ background: #f8f9fa; padding: 15px; margin: