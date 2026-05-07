```python
"""
Website Health Metrics HTML Report Generator

This module generates comprehensive HTML reports for website health monitoring.
It creates self-contained HTML files with:
- Color-coded status indicators for website health
- Tables showing detailed metrics (response time, status codes, uptime)
- Interactive charts for response time trends over time
- Responsive design that works on desktop and mobile

The module uses only standard library components plus httpx for HTTP requests
and includes built-in CSS and JavaScript for a complete standalone report.

Usage:
    python script.py

The script will generate sample data and create an HTML report saved to 'website_health_report.html'
"""

import json
import datetime
import random
import html
from typing import Dict, List, Tuple, Any
import sys

try:
    import httpx
except ImportError:
    print("Error: httpx not found. Install with: pip install httpx")
    sys.exit(1)

class WebsiteHealthReporter:
    """Generates HTML reports for website health monitoring."""
    
    def __init__(self):
        self.metrics_data = []
        self.trend_data = []
    
    def add_website_metrics(self, url: str, response_time: float, status_code: int, 
                          uptime_percent: float, last_check: str) -> None:
        """Add website metrics data for the report."""
        try:
            self.metrics_data.append({
                'url': html.escape(url),
                'response_time': float(response_time),
                'status_code': int(status_code),
                'uptime_percent': float(uptime_percent),
                'last_check': html.escape(last_check),
                'status': self._get_status_from_metrics(response_time, status_code, uptime_percent)
            })
        except (ValueError, TypeError) as e:
            print(f"Warning: Invalid metrics data for {url}: {e}")
    
    def add_trend_data(self, url: str, timestamp: str, response_time: float) -> None:
        """Add response time trend data for charts."""
        try:
            self.trend_data.append({
                'url': html.escape(url),
                'timestamp': html.escape(timestamp),
                'response_time': float(response_time)
            })
        except (ValueError, TypeError) as e:
            print(f"Warning: Invalid trend data: {e}")
    
    def _get_status_from_metrics(self, response_time: float, status_code: int, uptime: float) -> str:
        """Determine overall status based on metrics."""
        if status_code >= 500 or uptime < 95.0:
            return 'critical'
        elif status_code >= 400 or response_time > 3000 or uptime < 98.0:
            return 'warning'
        elif status_code == 200 and response_time < 1000 and uptime >= 99.0:
            return 'excellent'
        else:
            return 'good'
    
    def _get_status_color(self, status: str) -> str:
        """Get color code for status indicator."""
        colors = {
            'excellent': '#28a745',
            'good': '#17a2b8',
            'warning': '#ffc107',
            'critical': '#dc3545'
        }
        return colors.get(status, '#6c757d')
    
    def _generate_css(self) -> str:
        """Generate CSS styles for the report."""
        return """
        <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f8f9fa;
            padding: 20px;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .content {
            padding: 30px;
        }
        
        .section {
            margin-bottom: 40px;
        }
        
        .section h2 {
            color: #333;
            margin-bottom: 20px;
            font-size: 1.8em;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        
        .metrics-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .metrics-table th {
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }
        
        .metrics-table td {
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
        }
        
        .metrics-table tr:hover {
            background-color: #f8f9fa;
        }
        
        .status-indicator {
            display: inline-block;
            padding: 6px 12px;
            border-radius: 20px;
            color: white;
            font-weight: 600;
            font-size: 0.9em;
            text-transform: uppercase;
        }
        
        .chart-container {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        
        .chart {
            width: 100%;
            height: 300px;
            position: relative;
        }
        
        .summary-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .summary-card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .summary-card h3 {
            color: #667eea;
            margin-bottom: 10px;
        }
        
        .summary-card .value {
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }
        
        @media (max-width: 768px) {
            .container {
                margin: 10px;
                border-radius: 0;
            }
            
            .header {
                padding: 20px;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .content {
                padding: 20px;
            }
            
            .metrics-table {
                font-size: 0.9em;
            }
            
            .metrics-table th,
            .metrics-table td {
                padding: 10px 8px;
            }
        }
        </style>
        """
    
    def _generate_javascript(self) -> str:
        """Generate JavaScript for interactive charts."""