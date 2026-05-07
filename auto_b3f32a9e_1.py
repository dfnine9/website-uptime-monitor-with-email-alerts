```python
"""
Performance Data Analyzer

This module analyzes CSV performance data to calculate metrics and detect anomalies
for monitored websites. It processes response times, uptime percentages, identifies
trends, and detects outages without requiring external dependencies beyond the
Python standard library.

Usage: python script.py

Expected CSV format:
timestamp,website,response_time_ms,status_code,error_message
2024-01-01T00:00:00Z,example.com,150,200,
2024-01-01T00:05:00Z,example.com,0,0,Connection timeout
"""

import csv
import sys
from datetime import datetime
from collections import defaultdict, Counter
import statistics
import io

def parse_timestamp(timestamp_str):
    """Parse ISO format timestamp string to datetime object."""
    try:
        return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    except ValueError:
        try:
            return datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return None

def calculate_uptime_percentage(status_codes):
    """Calculate uptime percentage based on successful status codes."""
    if not status_codes:
        return 0.0
    successful = sum(1 for code in status_codes if 200 <= code < 400)
    return (successful / len(status_codes)) * 100

def detect_anomalies(response_times, threshold_multiplier=2.0):
    """Detect anomalies using standard deviation method."""
    if len(response_times) < 3:
        return []
    
    valid_times = [rt for rt in response_times if rt > 0]
    if not valid_times:
        return []
    
    mean_time = statistics.mean(valid_times)
    if len(valid_times) == 1:
        return []
    
    std_dev = statistics.stdev(valid_times)
    threshold = mean_time + (threshold_multiplier * std_dev)
    
    anomalies = []
    for i, rt in enumerate(response_times):
        if rt > threshold:
            anomalies.append((i, rt))
    
    return anomalies

def identify_trends(response_times, timestamps):
    """Identify performance trends using simple linear regression."""
    if len(response_times) < 2:
        return "Insufficient data"
    
    valid_data = [(t, rt) for t, rt in zip(timestamps, response_times) if rt > 0 and t]
    if len(valid_data) < 2:
        return "Insufficient valid data"
    
    # Convert timestamps to numeric values (hours from first timestamp)
    first_time = valid_data[0][0]
    numeric_times = [(t - first_time).total_seconds() / 3600 for t, _ in valid_data]
    numeric_responses = [rt for _, rt in valid_data]
    
    if len(numeric_times) < 2:
        return "Insufficient data points"
    
    # Simple linear regression
    n = len(numeric_times)
    sum_x = sum(numeric_times)
    sum_y = sum(numeric_responses)
    sum_xy = sum(x * y for x, y in zip(numeric_times, numeric_responses))
    sum_x2 = sum(x * x for x in numeric_times)
    
    if n * sum_x2 - sum_x * sum_x == 0:
        return "No trend (constant time values)"
    
    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
    
    if abs(slope) < 0.1:
        return "Stable"
    elif slope > 0:
        return "Degrading" if slope > 1 else "Slightly degrading"
    else:
        return "Improving" if slope < -1 else "Slightly improving"

def detect_outages(status_codes, timestamps, consecutive_failures=3):
    """Detect outages based on consecutive failures."""
    if len(status_codes) < consecutive_failures:
        return []
    
    outages = []
    failure_start = None
    failure_count = 0
    
    for i, (status_code, timestamp) in enumerate(zip(status_codes, timestamps)):
        is_failure = status_code == 0 or status_code >= 400
        
        if is_failure:
            if failure_count == 0:
                failure_start = timestamp
            failure_count += 1
        else:
            if failure_count >= consecutive_failures and failure_start:
                outages.append({
                    'start': failure_start,
                    'end': timestamps[i-1] if i > 0 else failure_start,
                    'duration_points': failure_count
                })
            failure_count = 0
            failure_start = None
    
    # Check if outage continues to the end
    if failure_count >= consecutive_failures and failure_start:
        outages.append({
            'start': failure_start,
            'end': timestamps[-1] if timestamps else failure_start,
            'duration_points': failure_count
        })
    
    return outages

def analyze_performance_data():
    """Main function to analyze performance data from CSV."""
    # Sample CSV data for demonstration
    sample_data = """timestamp,website,response_time_ms,status_code,error_message
2024-01-01T00:00:00Z,example.com,150,200,
2024-01-01T00:05:00Z,example.com,145,200,
2024-01-01T00:10:00Z,example.com,0,0,Connection timeout
2024-01-01T00:15:00Z,example.com,0,0,Connection timeout
2024-01-01T00:20:00Z,example.com,0,0,Connection timeout
2024-01-01T00:25:00Z,example.com,160,200,
2024-01-01T00:30:00Z,example.com,800,200,
2024-01-01T00:35:00Z,example.com,155,200,
2024-01-01T00:40:00Z,test.org,120,200,
2024-01-01T00:45:00Z,test.org,125,200,
2024-01-01T00:50:00Z,test.org,0,500,Internal server error
2024-01-01T00:55:00Z,test.org,130,200,"""
    
    try:
        # Parse CSV data
        csv_reader = csv.DictReader(io.StringIO(sample_data))
        
        # Group data by website
        website_data = defaultdict(lambda: {
            'response_times': [],
            'status_codes': [],
            'timestamps': [],
            'errors': []
        })
        
        for row in csv_reader:
            website = row['website']
            response_time = int(row['response_time_ms']) if row['response_time_ms'] else 0
            status_code = int(row['status_code']) if row['status_code'] else 0
            timestamp = parse_timestamp(row['timestamp'])
            error_msg = row.get('error_message', '').strip()
            
            website_data[website]['response_times'].append(response_time)
            website_data[website]['status_codes'].append(status_code)
            website_data[website]['timestamps'].append(timestamp)
            if error_msg:
                website_data[website]['errors'].append(error_msg)
        
        if not website_data:
            print("No data found to analyze.")
            return
        
        print("=" * 60)
        print("WEBSITE PERFORMANCE ANALYSIS REPORT")
        print("=" * 60)
        
        for website, data in website_data.items():
            print(f"\n{'='*50}")
            print(f"WEBSITE: {website}")
            print(f"{'='*50}")
            
            response_times = data['response_times']
            status_codes = data['status_codes']
            timestamps = data['timestamps']
            errors = data['errors']