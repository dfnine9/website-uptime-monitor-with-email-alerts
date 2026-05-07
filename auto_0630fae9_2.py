```python
#!/usr/bin/env python3
"""
Website Uptime Report Generator

This module analyzes CSV log files containing website monitoring data and generates
comprehensive uptime reports. It calculates daily uptime percentages, average response
times, and identifies downtime incidents for each monitored website.

The script processes CSV files with columns: timestamp, website, status_code, response_time
and outputs detailed HTML reports with statistics and visualizations.

Usage: python script.py
"""

import csv
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import statistics


class UptimeReportGenerator:
    """Generates uptime reports from CSV monitoring logs."""
    
    def __init__(self, csv_file_path: str = "monitoring_logs.csv"):
        """
        Initialize the report generator.
        
        Args:
            csv_file_path: Path to the CSV file containing monitoring logs
        """
        self.csv_file_path = csv_file_path
        self.data = []
        self.websites = set()
        
    def load_csv_data(self) -> bool:
        """
        Load and parse CSV monitoring data.
        
        Returns:
            bool: True if data loaded successfully, False otherwise
        """
        try:
            if not os.path.exists(self.csv_file_path):
                print(f"Creating sample CSV file: {self.csv_file_path}")
                self._create_sample_csv()
            
            with open(self.csv_file_path, 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    try:
                        # Parse timestamp
                        timestamp = datetime.fromisoformat(row['timestamp'].replace('Z', '+00:00'))
                        
                        # Parse data
                        entry = {
                            'timestamp': timestamp,
                            'website': row['website'],
                            'status_code': int(row['status_code']),
                            'response_time': float(row['response_time'])
                        }
                        
                        self.data.append(entry)
                        self.websites.add(row['website'])
                        
                    except (ValueError, KeyError) as e:
                        print(f"Warning: Skipping invalid row: {row}. Error: {e}")
                        continue
                        
            print(f"Loaded {len(self.data)} monitoring entries for {len(self.websites)} websites")
            return len(self.data) > 0
            
        except Exception as e:
            print(f"Error loading CSV data: {e}")
            return False
    
    def _create_sample_csv(self):
        """Create a sample CSV file for demonstration."""
        sample_data = [
            ['timestamp', 'website', 'status_code', 'response_time'],
            ['2024-01-01T00:00:00Z', 'example.com', '200', '0.150'],
            ['2024-01-01T00:05:00Z', 'example.com', '200', '0.175'],
            ['2024-01-01T00:10:00Z', 'example.com', '500', '5.000'],
            ['2024-01-01T00:15:00Z', 'example.com', '200', '0.145'],
            ['2024-01-01T00:00:00Z', 'test-site.org', '200', '0.220'],
            ['2024-01-01T00:05:00Z', 'test-site.org', '200', '0.185'],
            ['2024-01-01T00:10:00Z', 'test-site.org', '200', '0.195'],
            ['2024-01-01T00:15:00Z', 'test-site.org', '404', '0.100'],
            ['2024-01-02T00:00:00Z', 'example.com', '200', '0.160'],
            ['2024-01-02T00:05:00Z', 'example.com', '200', '0.140'],
            ['2024-01-02T00:10:00Z', 'example.com', '200', '0.155'],
            ['2024-01-02T00:15:00Z', 'example.com', '200', '0.165'],
        ]
        
        with open(self.csv_file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(sample_data)
    
    def calculate_daily_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Calculate daily statistics for each website.
        
        Returns:
            Dict containing daily stats for each website
        """
        daily_stats = defaultdict(lambda: defaultdict(list))
        
        # Group data by website and date
        for entry in self.data:
            website = entry['website']
            date = entry['timestamp'].date()
            daily_stats[website][date].append(entry)
        
        # Calculate statistics for each website/date combination
        results = {}
        for website, dates in daily_stats.items():
            results[website] = {}
            for date, entries in dates.items():
                total_checks = len(entries)
                successful_checks = sum(1 for e in entries if 200 <= e['status_code'] < 300)
                uptime_percentage = (successful_checks / total_checks) * 100 if total_checks > 0 else 0
                
                response_times = [e['response_time'] for e in entries]
                avg_response_time = statistics.mean(response_times) if response_times else 0
                
                downtime_incidents = self._identify_downtime_incidents(entries)
                
                results[website][date] = {
                    'total_checks': total_checks,
                    'successful_checks': successful_checks,
                    'uptime_percentage': uptime_percentage,
                    'avg_response_time': avg_response_time,
                    'downtime_incidents': downtime_incidents,
                    'failed_checks': total_checks - successful_checks
                }
        
        return results
    
    def _identify_downtime_incidents(self, entries: List[Dict]) -> List[Dict]:
        """
        Identify downtime incidents from entries.
        
        Args:
            entries: List of monitoring entries for a specific day
            
        Returns:
            List of downtime incidents with start/end times and duration
        """
        incidents = []
        current_incident = None
        
        sorted_entries = sorted(entries, key=lambda x: x['timestamp'])
        
        for entry in sorted_entries:
            is_down = not (200 <= entry['status_code'] < 300)
            
            if is_down and current_incident is None:
                # Start of new incident
                current_incident = {
                    'start_time': entry['timestamp'],
                    'end_time': entry['timestamp'],
                    'status_code': entry['status_code'],
                    'duration_minutes': 0
                }
            elif is_down and current_incident is not None:
                # Continue existing incident
                current_incident['end_time'] = entry['timestamp']
            elif not is_down and current_incident is not None:
                # End of incident
                current_incident['duration_minutes'] = (
                    current_incident['end_time'] - current_incident['start_time']
                ).total_seconds() / 60
                incidents.append(current_incident)
                current_incident = None
        
        # Handle ongoing incident at end of day
        if current_incident is not None:
            current_incident['duration_minutes'] = (
                current_incident['end_time'] - current_incident['start_time']
            ).total_seconds() / 60
            incidents.append(current_incident)
        
        return incidents
    
    def generate_html_report(self, stats: Dict[str, Dict[str, Any]]) -> str:
        """
        Generate HTML report from statistics.
        
        Args:
            stats: Dictionary containing daily statistics
            
        Returns:
            HTML report string
        """
        html_template = """
<!DOCTYPE html>