```python
#!/usr/bin/env python3
"""
Website Monitoring Dashboard Generator

This module reads CSV log data containing website monitoring information and generates
a comprehensive HTML dashboard report with the following features:

- Calculates uptime percentages for each monitored URL
- Identifies downtime periods and their durations
- Creates a responsive HTML dashboard with:
  * Summary statistics table
  * Visual charts showing uptime/downtime distribution
  * Alert notifications for URLs with >5% downtime
  * Detailed downtime incident reports

The script is self-contained and requires only standard library modules.
It reads from 'monitoring_log.csv' and outputs 'uptime_dashboard.html'.

CSV Format Expected:
timestamp,url,status_code,response_time,error_message

Usage: python script.py
"""

import csv
import json
import datetime
from collections import defaultdict, namedtuple
from typing import Dict, List, Tuple, Any
import os
import sys

# Data structures
LogEntry = namedtuple('LogEntry', ['timestamp', 'url', 'status_code', 'response_time', 'error_message'])
DowntimeIncident = namedtuple('DowntimeIncident', ['start_time', 'end_time', 'duration', 'error'])

class UptimeAnalyzer:
    """Analyzes website monitoring data and generates uptime reports."""
    
    def __init__(self, csv_file: str = 'monitoring_log.csv'):
        self.csv_file = csv_file
        self.log_data: List[LogEntry] = []
        self.url_stats: Dict[str, Dict] = defaultdict(lambda: {
            'total_checks': 0,
            'successful_checks': 0,
            'failed_checks': 0,
            'uptime_percentage': 0.0,
            'downtime_incidents': [],
            'avg_response_time': 0.0,
            'last_check': None
        })
    
    def load_csv_data(self) -> bool:
        """Load and parse CSV monitoring data."""
        try:
            if not os.path.exists(self.csv_file):
                print(f"Error: CSV file '{self.csv_file}' not found.")
                return False
            
            with open(self.csv_file, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    try:
                        entry = LogEntry(
                            timestamp=datetime.datetime.fromisoformat(row['timestamp'].replace('Z', '+00:00')),
                            url=row['url'].strip(),
                            status_code=int(row['status_code']) if row['status_code'].isdigit() else 0,
                            response_time=float(row['response_time']) if row['response_time'] else 0.0,
                            error_message=row.get('error_message', '').strip()
                        )
                        self.log_data.append(entry)
                    except (ValueError, KeyError) as e:
                        print(f"Warning: Skipping invalid row: {row}. Error: {e}")
                        continue
            
            print(f"Loaded {len(self.log_data)} log entries from {self.csv_file}")
            return len(self.log_data) > 0
            
        except Exception as e:
            print(f"Error loading CSV data: {e}")
            return False
    
    def analyze_uptime(self) -> None:
        """Analyze uptime statistics for each URL."""
        # Sort data by URL and timestamp
        self.log_data.sort(key=lambda x: (x.url, x.timestamp))
        
        for entry in self.log_data:
            url = entry.url
            stats = self.url_stats[url]
            
            stats['total_checks'] += 1
            stats['last_check'] = entry.timestamp
            
            # Consider status codes 200-299 as successful
            is_successful = 200 <= entry.status_code < 300
            
            if is_successful:
                stats['successful_checks'] += 1
            else:
                stats['failed_checks'] += 1
        
        # Calculate percentages and response times
        for url, stats in self.url_stats.items():
            if stats['total_checks'] > 0:
                stats['uptime_percentage'] = (stats['successful_checks'] / stats['total_checks']) * 100
            
            # Calculate average response time for successful requests
            successful_entries = [e for e in self.log_data if e.url == url and 200 <= e.status_code < 300]
            if successful_entries:
                stats['avg_response_time'] = sum(e.response_time for e in successful_entries) / len(successful_entries)
    
    def identify_downtime_periods(self) -> None:
        """Identify continuous downtime periods for each URL."""
        for url in self.url_stats.keys():
            url_entries = [e for e in self.log_data if e.url == url]
            url_entries.sort(key=lambda x: x.timestamp)
            
            downtime_incidents = []
            current_incident_start = None
            
            for entry in url_entries:
                is_down = not (200 <= entry.status_code < 300)
                
                if is_down and current_incident_start is None:
                    # Start of downtime
                    current_incident_start = entry.timestamp
                elif not is_down and current_incident_start is not None:
                    # End of downtime
                    duration = entry.timestamp - current_incident_start
                    incident = DowntimeIncident(
                        start_time=current_incident_start,
                        end_time=entry.timestamp,
                        duration=duration,
                        error=entry.error_message or f"HTTP {entry.status_code}"
                    )
                    downtime_incidents.append(incident)
                    current_incident_start = None
            
            # Handle ongoing downtime
            if current_incident_start is not None and url_entries:
                duration = url_entries[-1].timestamp - current_incident_start
                incident = DowntimeIncident(
                    start_time=current_incident_start,
                    end_time=url_entries[-1].timestamp,
                    duration=duration,
                    error="Ongoing downtime"
                )
                downtime_incidents.append(incident)
            
            self.url_stats[url]['downtime_incidents'] = downtime_incidents
    
    def get_alerts(self) -> List[Dict[str, Any]]:
        """Get URLs with >5% downtime for alerts."""
        alerts = []
        for url, stats in self.url_stats.items():
            if stats['uptime_percentage'] < 95.0:  # >5% downtime
                downtime_percentage = 100 - stats['uptime_percentage']
                alerts.append({
                    'url': url,
                    'uptime_percentage': stats['uptime_percentage'],
                    'downtime_percentage': downtime_percentage,
                    'total_incidents': len(stats['downtime_incidents']),
                    'severity': 'critical' if downtime_percentage > 20 else 'warning'
                })
        return sorted(alerts, key=lambda x: x['downtime_percentage'], reverse=True)
    
    def generate_html_report(self, output_file: str = 'uptime_dashboard.html') -> bool:
        """Generate comprehensive HTML dashboard report."""
        try:
            alerts = self.get_alerts()
            
            # Generate chart data
            chart_data = {
                'urls': list(self.url_stats.keys()),
                'uptime_percentages': [stats['uptime_percentage'] for stats in self.url_stats.values()],
                'response_times': [stats['avg_response_time'] for stats in self.url_stats.values()]
            }
            
            html_content = self._generate_html_template(alerts, chart_data)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"HTML dashboard generated: {output_file}")