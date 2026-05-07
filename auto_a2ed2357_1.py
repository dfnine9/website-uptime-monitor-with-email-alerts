```python
#!/usr/bin/env python3
"""
Historical Performance Data Analyzer

This module reads JSON data files containing performance metrics, calculates
trends for response times and uptime, and generates comprehensive reports in
both HTML and CSV formats with embedded charts and statistical analysis.

Features:
- Reads multiple JSON files from a specified directory
- Calculates rolling averages, percentiles, and trend analysis
- Generates HTML reports with embedded charts using Chart.js CDN
- Exports CSV summaries for further analysis
- Handles missing data and provides error recovery
- Self-contained with minimal dependencies

Usage:
    python script.py [data_directory]

Expected JSON format:
    {
        "timestamp": "2024-01-01T12:00:00Z",
        "response_time_ms": 150.5,
        "uptime": true,
        "endpoint": "/api/health",
        "status_code": 200
    }
"""

import json
import csv
import os
import sys
from datetime import datetime, timedelta
from statistics import mean, median, stdev
from pathlib import Path
import re


class PerformanceAnalyzer:
    """Analyzes historical performance data and generates reports."""
    
    def __init__(self, data_dir="./data"):
        self.data_dir = Path(data_dir)
        self.raw_data = []
        self.processed_data = {}
        
    def load_json_files(self):
        """Load all JSON files from the data directory."""
        try:
            if not self.data_dir.exists():
                print(f"Warning: Data directory {self.data_dir} does not exist")
                return
                
            json_files = list(self.data_dir.glob("*.json"))
            if not json_files:
                print(f"Warning: No JSON files found in {self.data_dir}")
                return
                
            for file_path in json_files:
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            self.raw_data.extend(data)
                        else:
                            self.raw_data.append(data)
                    print(f"Loaded {file_path.name}")
                except (json.JSONDecodeError, IOError) as e:
                    print(f"Error loading {file_path}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error accessing data directory: {e}")
    
    def process_data(self):
        """Process raw data and calculate metrics."""
        try:
            if not self.raw_data:
                print("No data to process")
                return
                
            # Sort by timestamp
            sorted_data = []
            for entry in self.raw_data:
                try:
                    timestamp = datetime.fromisoformat(entry.get('timestamp', '').replace('Z', '+00:00'))
                    response_time = float(entry.get('response_time_ms', 0))
                    uptime = bool(entry.get('uptime', True))
                    endpoint = entry.get('endpoint', 'unknown')
                    
                    sorted_data.append({
                        'timestamp': timestamp,
                        'response_time': response_time,
                        'uptime': uptime,
                        'endpoint': endpoint
                    })
                except (ValueError, TypeError) as e:
                    print(f"Skipping invalid entry: {e}")
                    continue
            
            sorted_data.sort(key=lambda x: x['timestamp'])
            
            # Calculate daily aggregates
            daily_stats = {}
            for entry in sorted_data:
                date_key = entry['timestamp'].date()
                if date_key not in daily_stats:
                    daily_stats[date_key] = {
                        'response_times': [],
                        'uptime_events': [],
                        'total_requests': 0
                    }
                
                daily_stats[date_key]['response_times'].append(entry['response_time'])
                daily_stats[date_key]['uptime_events'].append(entry['uptime'])
                daily_stats[date_key]['total_requests'] += 1
            
            # Process daily statistics
            for date, stats in daily_stats.items():
                try:
                    avg_response = mean(stats['response_times']) if stats['response_times'] else 0
                    median_response = median(stats['response_times']) if stats['response_times'] else 0
                    p95_response = self._percentile(stats['response_times'], 95) if stats['response_times'] else 0
                    uptime_pct = (sum(stats['uptime_events']) / len(stats['uptime_events']) * 100) if stats['uptime_events'] else 0
                    
                    self.processed_data[date] = {
                        'avg_response_time': avg_response,
                        'median_response_time': median_response,
                        'p95_response_time': p95_response,
                        'uptime_percentage': uptime_pct,
                        'total_requests': stats['total_requests']
                    }
                except Exception as e:
                    print(f"Error processing data for {date}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error in data processing: {e}")
    
    def _percentile(self, data, percentile):
        """Calculate percentile value."""
        try:
            sorted_data = sorted(data)
            index = (percentile / 100) * (len(sorted_data) - 1)
            if index == int(index):
                return sorted_data[int(index)]
            else:
                lower = sorted_data[int(index)]
                upper = sorted_data[int(index) + 1]
                return lower + (upper - lower) * (index - int(index))
        except (IndexError, ValueError):
            return 0
    
    def generate_html_report(self, output_file="performance_report.html"):
        """Generate HTML report with embedded charts."""
        try:
            if not self.processed_data:
                print("No processed data available for HTML report")
                return
                
            dates = sorted(self.processed_data.keys())
            response_times = [self.processed_data[d]['avg_response_time'] for d in dates]
            uptime_pcts = [self.processed_data[d]['uptime_percentage'] for d in dates]
            date_labels = [d.strftime('%Y-%m-%d') for d in dates]
            
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Performance Analysis Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .chart-container {{ width: 80%; margin: 20px auto; }}
        .stats-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        .stats-table th, .stats-table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        .stats-table th {{ background-color: #f2f2f2; }}
        .summary {{ background-color: #f9f9f9; padding: 15px; margin: 20px 0; border-radius: 5px; }}
    </style>
</head>
<body>
    <h1>Performance Analysis Report</h1>
    <div class="summary">
        <h2>Summary Statistics</h2>
        <p><strong>Analysis Period:</strong> {dates[0].strftime('%Y-%m-%d')} to {dates[-1].strftime('%Y-%m-%d')}</p>
        <p><strong>Total Days:</strong> {len(dates)}</p>
        <p><strong>Average Response Time:</strong> {mean(response_times):.2f} ms</p>
        <p><strong>Average Uptime:</strong> {mean(uptime_pcts):.2f}%</p>
    </div>
    
    <div class="chart-container">
        <canvas id="