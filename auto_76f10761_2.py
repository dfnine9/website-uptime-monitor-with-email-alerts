```python
#!/usr/bin/env python3
"""
Performance Report Generator

This module analyzes CSV log data to generate weekly performance reports including:
- Uptime percentages
- Average response times  
- Downtime incident analysis

The script expects CSV data with columns: timestamp, status, response_time
Status codes: 200 (up), 500+ (down), response_time in milliseconds

Usage: python script.py
"""

import csv
import sys
from datetime import datetime, timedelta
from collections import defaultdict
import statistics
from io import StringIO

def parse_timestamp(timestamp_str):
    """Parse timestamp string to datetime object"""
    formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M:%S.%f',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%S.%f',
        '%Y/%m/%d %H:%M:%S'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(timestamp_str.strip(), fmt)
        except ValueError:
            continue
    
    raise ValueError(f"Unable to parse timestamp: {timestamp_str}")

def is_service_up(status_code):
    """Determine if service is up based on status code"""
    try:
        code = int(status_code)
        return 200 <= code < 400
    except (ValueError, TypeError):
        return False

def get_week_start(dt):
    """Get the start of the week (Monday) for a given datetime"""
    days_since_monday = dt.weekday()
    return (dt - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)

def analyze_csv_data(csv_content):
    """Analyze CSV log data and return performance metrics"""
    try:
        reader = csv.DictReader(StringIO(csv_content))
        
        # Group data by week
        weekly_data = defaultdict(list)
        
        for row in reader:
            try:
                timestamp = parse_timestamp(row.get('timestamp', ''))
                status = row.get('status', '')
                response_time = float(row.get('response_time', 0))
                
                week_start = get_week_start(timestamp)
                weekly_data[week_start].append({
                    'timestamp': timestamp,
                    'status': status,
                    'response_time': response_time,
                    'is_up': is_service_up(status)
                })
                
            except (ValueError, TypeError) as e:
                print(f"Warning: Skipping invalid row - {e}")
                continue
    
    except Exception as e:
        raise Exception(f"Error reading CSV data: {e}")
    
    return weekly_data

def calculate_uptime_percentage(entries):
    """Calculate uptime percentage for a list of entries"""
    if not entries:
        return 0.0
    
    up_count = sum(1 for entry in entries if entry['is_up'])
    return (up_count / len(entries)) * 100

def calculate_average_response_time(entries):
    """Calculate average response time for up entries only"""
    up_entries = [entry for entry in entries if entry['is_up']]
    if not up_entries:
        return 0.0
    
    response_times = [entry['response_time'] for entry in up_entries]
    return statistics.mean(response_times)

def find_downtime_incidents(entries):
    """Find and analyze downtime incidents"""
    incidents = []
    current_incident = None
    
    for entry in sorted(entries, key=lambda x: x['timestamp']):
        if not entry['is_up']:
            if current_incident is None:
                current_incident = {
                    'start': entry['timestamp'],
                    'end': entry['timestamp'],
                    'duration': timedelta(0),
                    'status_codes': [entry['status']]
                }
            else:
                current_incident['end'] = entry['timestamp']
                current_incident['status_codes'].append(entry['status'])
        else:
            if current_incident is not None:
                current_incident['duration'] = current_incident['end'] - current_incident['start']
                incidents.append(current_incident)
                current_incident = None
    
    # Handle case where data ends during a downtime
    if current_incident is not None:
        current_incident['duration'] = current_incident['end'] - current_incident['start']
        incidents.append(current_incident)
    
    return incidents

def generate_report(weekly_data):
    """Generate and print the performance report"""
    print("=" * 80)
    print("WEEKLY PERFORMANCE REPORT")
    print("=" * 80)
    print()
    
    if not weekly_data:
        print("No data available for analysis.")
        return
    
    total_uptime = 0
    total_entries = 0
    total_response_time = 0
    total_up_entries = 0
    all_incidents = []
    
    for week_start in sorted(weekly_data.keys()):
        entries = weekly_data[week_start]
        week_end = week_start + timedelta(days=6)
        
        uptime_pct = calculate_uptime_percentage(entries)
        avg_response = calculate_average_response_time(entries)
        incidents = find_downtime_incidents(entries)
        
        print(f"Week: {week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}")
        print(f"  Total Requests: {len(entries)}")
        print(f"  Uptime: {uptime_pct:.2f}%")
        print(f"  Average Response Time: {avg_response:.2f}ms")
        print(f"  Downtime Incidents: {len(incidents)}")
        
        if incidents:
            print("  Incident Details:")
            for i, incident in enumerate(incidents, 1):
                duration_seconds = incident['duration'].total_seconds()
                unique_codes = set(incident['status_codes'])
                print(f"    {i}. {incident['start'].strftime('%Y-%m-%d %H:%M:%S')} - "
                      f"{incident['end'].strftime('%Y-%m-%d %H:%M:%S')} "
                      f"({duration_seconds:.0f}s) Status: {', '.join(map(str, unique_codes))}")
        
        print()
        
        # Aggregate totals
        total_uptime += uptime_pct * len(entries)
        total_entries += len(entries)
        up_entries = [e for e in entries if e['is_up']]
        if up_entries:
            total_response_time += avg_response * len(up_entries)
            total_up_entries += len(up_entries)
        all_incidents.extend(incidents)
    
    # Summary statistics
    print("-" * 80)
    print("SUMMARY STATISTICS")
    print("-" * 80)
    
    if total_entries > 0:
        overall_uptime = total_uptime / total_entries
        print(f"Overall Uptime: {overall_uptime:.2f}%")
    
    if total_up_entries > 0:
        overall_avg_response = total_response_time / total_up_entries
        print(f"Overall Average Response Time: {overall_avg_response:.2f}ms")
    
    print(f"Total Downtime Incidents: {len(all_incidents)}")
    
    if all_incidents:
        total_downtime = sum(incident['duration'].total_seconds() for incident in all_incidents)
        avg_incident_duration = total_downtime / len(all_incidents)
        print(f"Total Downtime Duration: {total_downtime:.0f} seconds")
        print(f"Average Incident Duration: {avg_incident_duration:.0f} seconds")

def main():
    """Main function to run the performance report generator"""
    
    # Sample CSV data for demonstration
    sample_data = """timestamp,status,response_time
2024-01-