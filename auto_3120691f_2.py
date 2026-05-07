```python
#!/usr/bin/env python3
"""
HTML Report Generator for System Monitoring Data

This module processes CSV data containing system monitoring information and generates
comprehensive HTML reports with downtime statistics, response time visualizations,
and alert notifications. The reports include interactive charts and summary metrics
for daily operational insights.

Key Features:
- Parses CSV data with timestamp, service, status, and response_time columns
- Calculates downtime statistics and availability percentages
- Generates response time trend charts using SVG
- Creates alert notifications for critical incidents
- Outputs self-contained HTML reports with embedded CSS and JavaScript

Usage:
    python script.py

The script expects CSV data to be provided via stdin or can be modified to read from files.
Generated reports are written to stdout and can be redirected to HTML files.
"""

import csv
import json
import sys
import io
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from urllib.parse import quote
import re


class MonitoringReportGenerator:
    """Generates HTML reports from monitoring CSV data."""
    
    def __init__(self):
        self.data = []
        self.services = set()
        self.alerts = []
        
    def parse_csv_data(self, csv_content):
        """Parse CSV data and extract monitoring metrics."""
        try:
            csv_reader = csv.DictReader(io.StringIO(csv_content))
            for row in csv_reader:
                # Validate required columns
                if not all(key in row for key in ['timestamp', 'service', 'status', 'response_time']):
                    raise ValueError("CSV must contain: timestamp, service, status, response_time columns")
                
                # Parse and validate data
                try:
                    timestamp = datetime.fromisoformat(row['timestamp'].replace('Z', '+00:00'))
                    service = row['service'].strip()
                    status = row['status'].lower().strip()
                    response_time = float(row['response_time'])
                    
                    self.data.append({
                        'timestamp': timestamp,
                        'service': service,
                        'status': status,
                        'response_time': response_time
                    })
                    self.services.add(service)
                    
                    # Generate alerts for critical conditions
                    if status == 'down' or response_time > 5000:  # 5 second threshold
                        self.alerts.append({
                            'timestamp': timestamp,
                            'service': service,
                            'type': 'downtime' if status == 'down' else 'slow_response',
                            'details': f"Status: {status}, Response: {response_time}ms"
                        })
                        
                except (ValueError, KeyError) as e:
                    print(f"Warning: Skipping invalid row - {e}", file=sys.stderr)
                    continue
                    
        except Exception as e:
            raise Exception(f"Error parsing CSV data: {e}")
    
    def calculate_downtime_stats(self):
        """Calculate downtime statistics per service."""
        stats = {}
        
        for service in self.services:
            service_data = [d for d in self.data if d['service'] == service]
            total_records = len(service_data)
            
            if total_records == 0:
                continue
                
            down_records = len([d for d in service_data if d['status'] == 'down'])
            availability = ((total_records - down_records) / total_records) * 100
            
            # Calculate downtime duration (assuming 1-minute intervals)
            downtime_minutes = down_records * 1
            
            # Response time statistics
            response_times = [d['response_time'] for d in service_data if d['status'] == 'up']
            avg_response = sum(response_times) / len(response_times) if response_times else 0
            max_response = max(response_times) if response_times else 0
            
            stats[service] = {
                'availability': round(availability, 2),
                'downtime_minutes': downtime_minutes,
                'total_records': total_records,
                'avg_response_time': round(avg_response, 2),
                'max_response_time': round(max_response, 2),
                'incidents': len([a for a in self.alerts if a['service'] == service])
            }
            
        return stats
    
    def generate_response_time_chart_data(self):
        """Generate data for response time charts."""
        chart_data = {}
        
        for service in self.services:
            service_data = [d for d in self.data if d['service'] == service and d['status'] == 'up']
            service_data.sort(key=lambda x: x['timestamp'])
            
            chart_data[service] = {
                'timestamps': [d['timestamp'].strftime('%H:%M') for d in service_data],
                'response_times': [d['response_time'] for d in service_data]
            }
            
        return chart_data
    
    def generate_html_report(self):
        """Generate complete HTML report."""
        try:
            downtime_stats = self.calculate_downtime_stats()
            chart_data = self.generate_response_time_chart_data()
            
            # Sort alerts by timestamp
            self.alerts.sort(key=lambda x: x['timestamp'], reverse=True)
            
            html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily System Monitoring Report</title>
    <style>
        {self._get_css_styles()}
    </style>
</head>
<body>
    <header>
        <h1>Daily System Monitoring Report</h1>
        <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </header>
    
    <main>
        <section class="summary">
            <h2>Summary Statistics</h2>
            {self._generate_summary_table(downtime_stats)}
        </section>
        
        <section class="charts">
            <h2>Response Time Trends</h2>
            {self._generate_charts(chart_data)}
        </section>
        
        <section class="alerts">
            <h2>Alert Notifications</h2>
            {self._generate_alerts_table()}
        </section>
    </main>
    
    <script>
        {self._get_javascript()}
    </script>
</body>
</html>
"""
            return html_content
            
        except Exception as e:
            raise Exception(f"Error generating HTML report: {e}")
    
    def _get_css_styles(self):
        """Return CSS styles for the report."""
        return """
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        header { background: #2c3e50; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        h1 { margin: 0; font-size: 24px; }
        h2 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px; }
        .summary, .charts, .alerts { background: white; padding: 20px; margin: 20px 0; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        table { width: 100%; border-collapse: collapse; margin: 10px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #3498db; color: white; }
        .high-availability { color: #27ae60; font-weight: bold; }
        .medium-availability { color: #f39c12; font-weight: bold; }
        .low-availability { color: #e74c3c; font-weight: bold; }
        .alert-critical { background: