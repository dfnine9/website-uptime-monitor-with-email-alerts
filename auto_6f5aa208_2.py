```python
#!/usr/bin/env python3
"""
Simple HTML Dashboard Generator for URL Monitoring

This script generates a self-contained HTML dashboard that reads JSON log files
containing URL monitoring data and displays current status and historical uptime
information for each monitored URL.

The dashboard includes:
- Current status overview with color-coded indicators
- Historical uptime percentages
- Response time trends
- Last check timestamps
- Interactive filtering and sorting

Usage:
    python script.py

The script looks for 'monitoring_log.json' in the current directory and generates
'dashboard.html' with the monitoring dashboard.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from collections import defaultdict
import html


def load_monitoring_data(log_file='monitoring_log.json'):
    """Load monitoring data from JSON log file with error handling."""
    try:
        if not os.path.exists(log_file):
            print(f"Warning: Log file '{log_file}' not found. Creating sample data...")
            return create_sample_data()
        
        with open(log_file, 'r') as f:
            data = []
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    data.append(entry)
                except json.JSONDecodeError as e:
                    print(f"Warning: Invalid JSON on line {line_num}: {e}")
                    continue
            return data
    except Exception as e:
        print(f"Error loading monitoring data: {e}")
        return create_sample_data()


def create_sample_data():
    """Create sample monitoring data for demonstration."""
    sample_data = []
    urls = ['https://example.com', 'https://google.com', 'https://github.com']
    
    for i in range(100):
        timestamp = datetime.now() - timedelta(hours=i)
        for url in urls:
            # Simulate some failures
            status_code = 200 if i % 10 != 0 else 500
            response_time = 150 + (i % 50) if status_code == 200 else 0
            
            entry = {
                'timestamp': timestamp.isoformat(),
                'url': url,
                'status_code': status_code,
                'response_time': response_time,
                'success': status_code == 200
            }
            sample_data.append(entry)
    
    return sample_data


def calculate_uptime_stats(data):
    """Calculate uptime statistics for each URL."""
    url_stats = defaultdict(lambda: {
        'total_checks': 0,
        'successful_checks': 0,
        'last_check': None,
        'last_status': 'Unknown',
        'avg_response_time': 0,
        'response_times': []
    })
    
    for entry in data:
        url = entry['url']
        stats = url_stats[url]
        
        stats['total_checks'] += 1
        if entry.get('success', False):
            stats['successful_checks'] += 1
            if entry.get('response_time'):
                stats['response_times'].append(entry['response_time'])
        
        # Update last check info
        entry_time = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00').replace('+00:00', ''))
        if not stats['last_check'] or entry_time > stats['last_check']:
            stats['last_check'] = entry_time
            stats['last_status'] = 'UP' if entry.get('success', False) else 'DOWN'
    
    # Calculate averages
    for url, stats in url_stats.items():
        if stats['response_times']:
            stats['avg_response_time'] = sum(stats['response_times']) / len(stats['response_times'])
        stats['uptime_percentage'] = (stats['successful_checks'] / stats['total_checks']) * 100 if stats['total_checks'] > 0 else 0
    
    return dict(url_stats)


def generate_html_dashboard(stats_data, output_file='dashboard.html'):
    """Generate HTML dashboard from statistics data."""
    
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>URL Monitoring Dashboard</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            padding: 30px;
        }
        .url-card {
            border: 1px solid #e1e1e1;
            border-radius: 8px;
            padding: 20px;
            background: #fafafa;
            transition: transform 0.2s;
        }
        .url-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .url-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .url-name {
            font-weight: 600;
            color: #333;
            font-size: 1.1em;
            word-break: break-all;
        }
        .status-indicator {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: 600;
            text-transform: uppercase;
        }
        .status-up {
            background: #d4edda;
            color: #155724;
        }
        .status-down {
            background: #f8d7da;
            color: #721c24;
        }
        .status-unknown {
            background: #fff3cd;
            color: #856404;
        }
        .metric {
            display: flex;
            justify-content: space-between;
            margin: 8px 0;
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }
        .metric:last-child {
            border-bottom: none;
        }
        .metric-label {
            color: #666;
            font-size: 0.9em;
        }
        .metric-value {
            font-weight: 600;
            color: #333;
        }
        .uptime-bar {
            width: 100%;
            height: 8px;
            background: #e9ecef;
            border-radius: 4px;
            margin: 10px 0;
            overflow: hidden;
        }
        .uptime-fill {
            height: 100%;
            background: linear-gradient(90deg, #28a745, #20c997);
            transition: width 0.3s;
        }
        .footer {
            text-align: center;
            padding: 20px;
            color: #666;
            background: #f