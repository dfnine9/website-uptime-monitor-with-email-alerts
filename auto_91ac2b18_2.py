```python
#!/usr/bin/env python3
"""
Database Report Generation Script

This script queries an SQLite database to generate comprehensive system monitoring reports.
It calculates uptime percentages, identifies downtime periods, analyzes response time trends,
and exports formatted reports in both HTML and JSON formats.

Features:
- Uptime percentage calculations
- Downtime period identification
- Response time trend analysis
- HTML and JSON report export
- Error handling and logging

Usage: python script.py
"""

import sqlite3
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import statistics


class DatabaseReportGenerator:
    def __init__(self, db_path: str = "monitoring.db"):
        """Initialize the report generator with database path."""
        self.db_path = db_path
        self.conn = None
        
    def connect_db(self) -> bool:
        """Establish database connection."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            return True
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            return False
            
    def close_db(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            
    def create_sample_data(self):
        """Create sample monitoring data for demonstration."""
        try:
            cursor = self.conn.cursor()
            
            # Create monitoring table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS monitoring_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    service_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    response_time REAL,
                    error_message TEXT
                )
            """)
            
            # Check if data already exists
            cursor.execute("SELECT COUNT(*) FROM monitoring_data")
            if cursor.fetchone()[0] > 0:
                return
                
            # Generate sample data for last 30 days
            base_time = datetime.now() - timedelta(days=30)
            services = ['web-api', 'database', 'cache-service', 'auth-service']
            
            sample_data = []
            for i in range(8640):  # 30 days * 24 hours * 12 (5-minute intervals)
                timestamp = base_time + timedelta(minutes=i * 5)
                for service in services:
                    # 95% uptime simulation
                    is_up = i % 100 != 0 or (i % 500 == 0 and service == 'database')
                    status = 'UP' if is_up else 'DOWN'
                    response_time = None if not is_up else max(50, statistics.normalvariate(200, 50))
                    error_msg = None if is_up else 'Connection timeout'
                    
                    sample_data.append((
                        timestamp.isoformat(),
                        service,
                        status,
                        response_time,
                        error_msg
                    ))
            
            cursor.executemany("""
                INSERT INTO monitoring_data (timestamp, service_name, status, response_time, error_message)
                VALUES (?, ?, ?, ?, ?)
            """, sample_data)
            
            self.conn.commit()
            print(f"Created sample data: {len(sample_data)} records")
            
        except sqlite3.Error as e:
            print(f"Error creating sample data: {e}")
            
    def calculate_uptime_percentage(self, service_name: Optional[str] = None, 
                                  days: int = 30) -> Dict[str, float]:
        """Calculate uptime percentage for services."""
        try:
            cursor = self.conn.cursor()
            
            # Base query
            base_query = """
                SELECT service_name, status, COUNT(*) as count
                FROM monitoring_data
                WHERE timestamp >= datetime('now', '-{} days')
            """.format(days)
            
            if service_name:
                base_query += " AND service_name = ?"
                cursor.execute(base_query + " GROUP BY service_name, status", (service_name,))
            else:
                cursor.execute(base_query + " GROUP BY service_name, status")
            
            results = cursor.fetchall()
            
            # Calculate uptime percentages
            service_stats = {}
            for row in results:
                service = row['service_name']
                status = row['status']
                count = row['count']
                
                if service not in service_stats:
                    service_stats[service] = {'UP': 0, 'DOWN': 0}
                service_stats[service][status] = count
            
            uptime_percentages = {}
            for service, stats in service_stats.items():
                total = stats['UP'] + stats['DOWN']
                uptime_pct = (stats['UP'] / total * 100) if total > 0 else 0
                uptime_percentages[service] = round(uptime_pct, 2)
                
            return uptime_percentages
            
        except sqlite3.Error as e:
            print(f"Error calculating uptime: {e}")
            return {}
            
    def identify_downtime_periods(self, service_name: str, min_duration: int = 10) -> List[Dict]:
        """Identify downtime periods longer than min_duration minutes."""
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("""
                SELECT timestamp, status, error_message
                FROM monitoring_data
                WHERE service_name = ? AND status = 'DOWN'
                ORDER BY timestamp
            """, (service_name,))
            
            downtime_events = cursor.fetchall()
            downtime_periods = []
            
            if not downtime_events:
                return downtime_periods
                
            current_period = {
                'start': downtime_events[0]['timestamp'],
                'end': downtime_events[0]['timestamp'],
                'duration_minutes': 0,
                'error_message': downtime_events[0]['error_message']
            }
            
            for i in range(1, len(downtime_events)):
                prev_time = datetime.fromisoformat(downtime_events[i-1]['timestamp'])
                curr_time = datetime.fromisoformat(downtime_events[i]['timestamp'])
                
                # If gap is less than 10 minutes, consider it same downtime period
                if (curr_time - prev_time).total_seconds() / 60 <= 10:
                    current_period['end'] = downtime_events[i]['timestamp']
                else:
                    # Calculate duration and add to periods if meets minimum
                    start_time = datetime.fromisoformat(current_period['start'])
                    end_time = datetime.fromisoformat(current_period['end'])
                    duration = (end_time - start_time).total_seconds() / 60
                    
                    if duration >= min_duration:
                        current_period['duration_minutes'] = round(duration, 2)
                        downtime_periods.append(current_period.copy())
                    
                    # Start new period
                    current_period = {
                        'start': downtime_events[i]['timestamp'],
                        'end': downtime_events[i]['timestamp'],
                        'duration_minutes': 0,
                        'error_message': downtime_events[i]['error_message']
                    }
            
            # Don't forget the last period
            start_time = datetime.fromisoformat(current_period['start'])
            end_time = datetime.fromisoformat(current_period['end'])
            duration = (end_time - start_time).total_seconds() / 60
            
            if duration >= min_duration:
                current_period['duration_minutes'] = round(duration, 2)
                downtime_periods.append(current_period)
                
            return downtime_periods
            
        except (sqlite3.Error, ValueError) as e:
            print(f"Error identifying downtime periods: {e}")
            return []
            
    def analyze_response_time_trends(self, service_name: str, days: