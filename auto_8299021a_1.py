```python
#!/usr/bin/env python3
"""
Server Monitoring Data Analysis Script

This script analyzes JSON logs from server monitoring systems to provide insights into:
- Uptime percentages for monitored endpoints
- Average response times across all requests
- Identification of failing endpoints (non-2xx status codes)
- SSL certificate expiration warnings (certificates expiring within 30 days)

The script reads JSON log files, processes the data, and outputs a comprehensive
analysis report to stdout. It handles various log formats and provides robust
error handling for malformed data.

Usage: python script.py
"""

import json
import os
import sys
from datetime import datetime, timedelta
from collections import defaultdict
from statistics import mean
import re
import ssl
import socket
from urllib.parse import urlparse


def parse_timestamp(timestamp_str):
    """Parse various timestamp formats to datetime object."""
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%fZ"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(timestamp_str.replace('Z', ''), fmt.replace('Z', ''))
        except ValueError:
            continue
    
    # Try parsing Unix timestamp
    try:
        return datetime.fromtimestamp(float(timestamp_str))
    except (ValueError, TypeError):
        return None


def check_ssl_expiration(hostname, port=443):
    """Check SSL certificate expiration for a given hostname."""
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                expiry_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                days_until_expiry = (expiry_date - datetime.now()).days
                return expiry_date, days_until_expiry
    except Exception:
        return None, None


def extract_hostname_from_url(url):
    """Extract hostname from URL string."""
    try:
        parsed = urlparse(url)
        return parsed.hostname
    except Exception:
        return None


def find_json_files():
    """Find JSON log files in current directory and subdirectories."""
    json_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith(('.json', '.log', '.jsonl')):
                json_files.append(os.path.join(root, file))
    return json_files


def parse_log_entry(entry):
    """Parse a single log entry and extract relevant monitoring data."""
    data = {
        'timestamp': None,
        'url': None,
        'status_code': None,
        'response_time': None,
        'success': None
    }
    
    # Common field mappings
    timestamp_fields = ['timestamp', 'time', 'datetime', 'date', '@timestamp']
    url_fields = ['url', 'endpoint', 'target', 'host', 'service']
    status_fields = ['status_code', 'status', 'http_status', 'code', 'response_code']
    response_time_fields = ['response_time', 'duration', 'latency', 'time_ms', 'elapsed']
    success_fields = ['success', 'status', 'result', 'healthy', 'up']
    
    # Extract timestamp
    for field in timestamp_fields:
        if field in entry and entry[field]:
            data['timestamp'] = parse_timestamp(str(entry[field]))
            if data['timestamp']:
                break
    
    # Extract URL
    for field in url_fields:
        if field in entry and entry[field]:
            data['url'] = str(entry[field])
            break
    
    # Extract status code
    for field in status_fields:
        if field in entry and entry[field] is not None:
            try:
                data['status_code'] = int(entry[field])
                break
            except (ValueError, TypeError):
                continue
    
    # Extract response time
    for field in response_time_fields:
        if field in entry and entry[field] is not None:
            try:
                data['response_time'] = float(entry[field])
                break
            except (ValueError, TypeError):
                continue
    
    # Extract success status
    for field in success_fields:
        if field in entry and entry[field] is not None:
            if isinstance(entry[field], bool):
                data['success'] = entry[field]
                break
            elif isinstance(entry[field], str):
                success_indicators = ['success', 'ok', 'up', 'healthy', 'true', '200']
                data['success'] = entry[field].lower() in success_indicators
                break
            elif isinstance(entry[field], int):
                data['success'] = 200 <= entry[field] < 300
                break
    
    # Infer success from status code if not explicitly provided
    if data['success'] is None and data['status_code'] is not None:
        data['success'] = 200 <= data['status_code'] < 300
    
    return data


def analyze_logs():
    """Main function to analyze monitoring logs."""
    print("=" * 60)
    print("SERVER MONITORING DATA ANALYSIS REPORT")
    print("=" * 60)
    print()
    
    # Find and process log files
    json_files = find_json_files()
    if not json_files:
        print("No JSON log files found in current directory or subdirectories.")
        return
    
    print(f"Found {len(json_files)} log file(s) to analyze:")
    for file in json_files:
        print(f"  - {file}")
    print()
    
    # Data containers
    all_entries = []
    endpoint_stats = defaultdict(lambda: {'total': 0, 'success': 0, 'response_times': []})
    ssl_hosts = set()
    
    # Process each file
    for file_path in json_files:
        print(f"Processing {file_path}...")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                
                # Try parsing as JSON array first
                try:
                    data = json.loads(content)
                    if isinstance(data, list):
                        entries = data
                    else:
                        entries = [data]
                except json.JSONDecodeError:
                    # Try parsing as JSONL (one JSON object per line)
                    entries = []
                    for line_num, line in enumerate(content.split('\n'), 1):
                        line = line.strip()
                        if line:
                            try:
                                entries.append(json.loads(line))
                            except json.JSONDecodeError as e:
                                print(f"  Warning: Skipping malformed JSON on line {line_num}: {e}")
                                continue
                
                # Parse each entry
                for entry in entries:
                    try:
                        parsed = parse_log_entry(entry)
                        if parsed['url'] or parsed['status_code'] is not None:
                            all_entries.append(parsed)
                            
                            # Update endpoint statistics
                            endpoint = parsed['url'] or 'unknown'
                            endpoint_stats[endpoint]['total'] += 1
                            if parsed['success']:
                                endpoint_stats[endpoint]['success'] += 1
                            if parsed['response_time'] is not None:
                                endpoint_stats[endpoint]['response_times'].append(parsed['response_time'])
                            
                            # Collect SSL hosts
                            if parsed['url']:
                                hostname = extract_hostname_from_url(parsed['url'])
                                if hostname:
                                    ssl_hosts.add(hostname)
                                    
                    except Exception as e:
                        print(f"  Warning: