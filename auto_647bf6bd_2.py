```python
"""
Log Analysis and Report Generation Script

This script reads CSV logs containing system availability data, calculates uptime percentages,
identifies downtime periods, and generates daily HTML reports with charts showing response
times and availability statistics.

Features:
- Parses CSV logs with timestamp, status, and response time data
- Calculates uptime/downtime percentages
- Identifies continuous downtime periods
- Generates HTML reports with embedded charts (using HTML5 Canvas and JavaScript)
- Self-contained with minimal dependencies

Usage: python script.py
"""

import csv
import json
import datetime
from collections import defaultdict
import os
import sys
from typing import List, Dict, Tuple, Optional

def read_csv_logs(filename: str) -> List[Dict]:
    """Read and parse CSV log file."""
    logs = []
    try:
        with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    # Parse timestamp
                    timestamp = datetime.datetime.fromisoformat(row['timestamp'].replace('Z', '+00:00'))
                    logs.append({
                        'timestamp': timestamp,
                        'status': row['status'].lower().strip(),
                        'response_time': float(row.get('response_time', 0))
                    })
                except (ValueError, KeyError) as e:
                    print(f"Warning: Skipping invalid row: {row} - Error: {e}")
                    continue
    except FileNotFoundError:
        print(f"Error: CSV file '{filename}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        sys.exit(1)
    
    return logs

def calculate_uptime_stats(logs: List[Dict]) -> Dict:
    """Calculate uptime statistics from logs."""
    if not logs:
        return {'uptime_percentage': 0, 'total_checks': 0, 'up_checks': 0, 'down_checks': 0}
    
    total_checks = len(logs)
    up_checks = sum(1 for log in logs if log['status'] in ['up', 'online', 'ok', 'success'])
    down_checks = total_checks - up_checks
    uptime_percentage = (up_checks / total_checks) * 100 if total_checks > 0 else 0
    
    return {
        'uptime_percentage': uptime_percentage,
        'total_checks': total_checks,
        'up_checks': up_checks,
        'down_checks': down_checks
    }

def identify_downtime_periods(logs: List[Dict]) -> List[Tuple[datetime.datetime, datetime.datetime, int]]:
    """Identify continuous downtime periods."""
    downtime_periods = []
    current_downtime_start = None
    
    for i, log in enumerate(logs):
        is_down = log['status'] not in ['up', 'online', 'ok', 'success']
        
        if is_down and current_downtime_start is None:
            current_downtime_start = log['timestamp']
        elif not is_down and current_downtime_start is not None:
            duration_minutes = (log['timestamp'] - current_downtime_start).total_seconds() / 60
            downtime_periods.append((current_downtime_start, log['timestamp'], int(duration_minutes)))
            current_downtime_start = None
    
    # Handle case where logs end during downtime
    if current_downtime_start is not None and logs:
        duration_minutes = (logs[-1]['timestamp'] - current_downtime_start).total_seconds() / 60
        downtime_periods.append((current_downtime_start, logs[-1]['timestamp'], int(duration_minutes)))
    
    return downtime_periods

def calculate_response_time_stats(logs: List[Dict]) -> Dict:
    """Calculate response time statistics."""
    response_times = [log['response_time'] for log in logs if log['response_time'] > 0]
    
    if not response_times:
        return {'avg': 0, 'min': 0, 'max': 0, 'count': 0}
    
    return {
        'avg': sum(response_times) / len(response_times),
        'min': min(response_times),
        'max': max(response_times),
        'count': len(response_times)
    }

def group_logs_by_day(logs: List[Dict]) -> Dict[str, List[Dict]]:
    """Group logs by day."""
    daily_logs = defaultdict(list)
    for log in logs:
        day_key = log['timestamp'].strftime('%Y-%m-%d')
        daily_logs[day_key].append(log)
    return dict(daily_logs)

def generate_html_report(date: str, logs: List[Dict], stats: Dict, downtime_periods: List, response_stats: Dict) -> str:
    """Generate HTML report for a specific date."""
    
    # Prepare data for charts
    hourly_data = defaultdict(lambda: {'up': 0, 'down': 0, 'total_response_time': 0, 'count': 0})
    
    for log in logs:
        hour = log['timestamp'].hour
        if log['status'] in ['up', 'online', 'ok', 'success']:
            hourly_data[hour]['up'] += 1
        else:
            hourly_data[hour]['down'] += 1
        
        if log['response_time'] > 0:
            hourly_data[hour]['total_response_time'] += log['response_time']
            hourly_data[hour]['count'] += 1
    
    # Calculate hourly averages
    hourly_uptime = []
    hourly_response = []
    
    for hour in range(24):
        total = hourly_data[hour]['up'] + hourly_data[hour]['down']
        uptime_pct = (hourly_data[hour]['up'] / total * 100) if total > 0 else 100
        avg_response = (hourly_data[hour]['total_response_time'] / hourly_data[hour]['count']) if hourly_data[hour]['count'] > 0 else 0
        
        hourly_uptime.append(uptime_pct)
        hourly_response.append(avg_response)
    
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Availability Report - {date}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
            .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
            .stat-box {{ background-color: #e8f4f8; padding: 15px; border-radius: 5px; text-align: center; }}
            .chart-container {{ margin: 20px 0; }}
            canvas {{ border: 1px solid #ddd; }}
            .downtime-list {{ background-color: #ffe6e6; padding: 15px; border-radius: 5px; }}
            .uptime-good {{ color: green; font-weight: bold; }}
            .uptime-warning {{ color: orange; font-weight: bold; }}
            .uptime-critical {{ color: red; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>System Availability Report</h1>
            <h2>Date: {date}</h2>
            <p>Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>

        <div class="stats">
            <div class="stat-box">
                <h3>Overall Uptime</h3>
                <p class="{'uptime-good' if stats['uptime_percentage'] >= 99 else 'uptime-warning' if stats['