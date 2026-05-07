```python
#!/usr/bin/env python3
"""
Report Generator for System Monitoring Analysis

This module analyzes JSON log files to generate comprehensive system monitoring reports.
It calculates key metrics including uptime percentages, average response times, and 
identifies downtime incidents from system monitoring logs.

Features:
- Parses JSON log files with system monitoring data
- Calculates uptime percentages based on successful responses
- Computes average response times for performance analysis
- Identifies and reports downtime incidents with duration
- Handles various log formats and missing data gracefully
- Generates human-readable reports with actionable insights

Usage:
    python script.py

The script automatically discovers JSON log files in the current directory
and generates a comprehensive monitoring report to stdout.
"""

import json
import os
import glob
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import statistics

def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
    """Parse various timestamp formats commonly found in log files."""
    formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%S.%f',
        '%Y-%m-%dT%H:%M:%SZ',
        '%Y-%m-%dT%H:%M:%S.%fZ',
        '%d/%m/%Y %H:%M:%S',
        '%m/%d/%Y %H:%M:%S'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(timestamp_str, fmt)
        except ValueError:
            continue
    
    # Try parsing as Unix timestamp
    try:
        return datetime.fromtimestamp(float(timestamp_str))
    except (ValueError, TypeError):
        return None

def load_log_files() -> List[Dict]:
    """Load and parse all JSON log files in the current directory."""
    log_entries = []
    json_files = glob.glob("*.json")
    
    if not json_files:
        print("No JSON log files found in current directory")
        return log_entries
    
    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                
                # Handle both single JSON objects and JSONL format
                if content.startswith('['):
                    # JSON array format
                    data = json.loads(content)
                    if isinstance(data, list):
                        log_entries.extend(data)
                    else:
                        log_entries.append(data)
                else:
                    # JSONL format or single JSON object
                    for line in content.split('\n'):
                        if line.strip():
                            try:
                                entry = json.loads(line)
                                log_entries.append(entry)
                            except json.JSONDecodeError:
                                continue
                                
        except (json.JSONDecodeError, FileNotFoundError, IOError) as e:
            print(f"Error reading {file_path}: {e}")
            continue
    
    return log_entries

def normalize_log_entry(entry: Dict) -> Dict:
    """Normalize log entry fields to standard format."""
    normalized = {}
    
    # Extract timestamp
    for timestamp_field in ['timestamp', 'time', 'datetime', '@timestamp', 'created_at']:
        if timestamp_field in entry:
            normalized['timestamp'] = parse_timestamp(str(entry[timestamp_field]))
            break
    
    # Extract status/success indicator
    if 'status' in entry:
        status = entry['status']
        if isinstance(status, int):
            normalized['success'] = 200 <= status < 400
        else:
            normalized['success'] = str(status).lower() in ['success', 'ok', 'up', 'true', '200']
    elif 'success' in entry:
        normalized['success'] = bool(entry['success'])
    elif 'error' in entry:
        normalized['success'] = not bool(entry['error'])
    elif 'state' in entry:
        normalized['success'] = str(entry['state']).lower() in ['up', 'online', 'running', 'ok']
    else:
        normalized['success'] = True  # Default assumption
    
    # Extract response time
    for response_field in ['response_time', 'duration', 'latency', 'elapsed_time', 'time_ms']:
        if response_field in entry:
            try:
                normalized['response_time'] = float(entry[response_field])
                break
            except (ValueError, TypeError):
                continue
    
    # Extract service/endpoint name
    for name_field in ['service', 'endpoint', 'url', 'name', 'host']:
        if name_field in entry:
            normalized['service'] = str(entry[name_field])
            break
    else:
        normalized['service'] = 'unknown'
    
    return normalized

def calculate_uptime(entries: List[Dict]) -> Dict[str, float]:
    """Calculate uptime percentage by service."""
    service_stats = {}
    
    for entry in entries:
        service = entry.get('service', 'unknown')
        if service not in service_stats:
            service_stats[service] = {'total': 0, 'successful': 0}
        
        service_stats[service]['total'] += 1
        if entry.get('success', True):
            service_stats[service]['successful'] += 1
    
    uptime_percentages = {}
    for service, stats in service_stats.items():
        if stats['total'] > 0:
            uptime_percentages[service] = (stats['successful'] / stats['total']) * 100
        else:
            uptime_percentages[service] = 0.0
    
    return uptime_percentages

def calculate_response_times(entries: List[Dict]) -> Dict[str, Dict]:
    """Calculate response time statistics by service."""
    service_times = {}
    
    for entry in entries:
        service = entry.get('service', 'unknown')
        response_time = entry.get('response_time')
        
        if response_time is not None:
            if service not in service_times:
                service_times[service] = []
            service_times[service].append(response_time)
    
    response_stats = {}
    for service, times in service_times.items():
        if times:
            response_stats[service] = {
                'average': statistics.mean(times),
                'median': statistics.median(times),
                'min': min(times),
                'max': max(times),
                'count': len(times)
            }
    
    return response_stats

def identify_downtime_incidents(entries: List[Dict]) -> List[Dict]:
    """Identify periods of downtime from log entries."""
    # Sort entries by timestamp and service
    valid_entries = [e for e in entries if e.get('timestamp')]
    valid_entries.sort(key=lambda x: (x.get('service', 'unknown'), x['timestamp']))
    
    incidents = []
    current_incident = None
    
    for entry in valid_entries:
        if not entry.get('success', True):
            if current_incident is None:
                # Start new incident
                current_incident = {
                    'service': entry.get('service', 'unknown'),
                    'start_time': entry['timestamp'],
                    'end_time': entry['timestamp'],
                    'duration_minutes': 0
                }
            else:
                # Extend current incident
                if entry.get('service') == current_incident['service']:
                    current_incident['end_time'] = entry['timestamp']
        else:
            # Service is up, close any current incident
            if current_incident is not None:
                duration = current_incident['end_time'] - current_incident['start_time']
                current_incident['duration_minutes'] = duration.total_seconds() / 60
                incidents.append(current_incident)
                current_incident = None
    
    # Close any remaining incident
    if current_incident is not None:
        duration = current_incident['end_time'] - current_incident['start_time']
        current_incident['duration_minutes'] = duration.total