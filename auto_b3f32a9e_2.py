```python
"""
Performance Report Generator

This module processes performance monitoring data and generates comprehensive HTML reports
with interactive charts showing response time trends, uptime statistics, and automated
optimization recommendations based on configurable performance thresholds.

Features:
- Response time trend analysis with statistical insights
- Uptime percentage calculations and availability reports
- Automated performance recommendations based on threshold analysis
- Self-contained HTML report generation with embedded CSS and JavaScript
- Configurable performance thresholds for different service tiers
- Error rate analysis and bottleneck identification

Usage:
    python script.py

The script generates sample performance data and creates an HTML report saved as
'performance_report.html' in the current directory.
"""

import json
import datetime
import statistics
import random
from typing import Dict, List, Any, Tuple
import sys


class PerformanceAnalyzer:
    """Analyzes performance data and generates optimization recommendations."""
    
    def __init__(self):
        self.thresholds = {
            'response_time': {
                'excellent': 100,  # ms
                'good': 300,
                'poor': 1000
            },
            'uptime': {
                'excellent': 99.9,  # %
                'good': 99.5,
                'poor': 99.0
            },
            'error_rate': {
                'excellent': 0.1,  # %
                'good': 1.0,
                'poor': 5.0
            }
        }
    
    def generate_sample_data(self, days: int = 30) -> Dict[str, Any]:
        """Generate sample performance data for demonstration."""
        try:
            base_time = datetime.datetime.now() - datetime.timedelta(days=days)
            data = {
                'metrics': [],
                'services': ['web-api', 'database', 'cache', 'auth-service'],
                'timestamp_range': {
                    'start': base_time.isoformat(),
                    'end': datetime.datetime.now().isoformat()
                }
            }
            
            # Generate hourly data points
            for i in range(days * 24):
                timestamp = base_time + datetime.timedelta(hours=i)
                
                # Simulate varying performance patterns
                hour = timestamp.hour
                base_response = 150 + (50 * (1 + 0.5 * (hour - 12) ** 2 / 144))
                
                for service in data['services']:
                    service_multiplier = random.uniform(0.8, 1.5)
                    response_time = max(50, base_response * service_multiplier + random.gauss(0, 30))
                    
                    # Simulate occasional outages
                    is_down = random.random() < 0.001
                    uptime = 0 if is_down else random.uniform(98, 100)
                    error_rate = random.uniform(10, 20) if is_down else random.uniform(0, 2)
                    
                    data['metrics'].append({
                        'timestamp': timestamp.isoformat(),
                        'service': service,
                        'response_time_ms': round(response_time, 2),
                        'uptime_percent': round(uptime, 2),
                        'error_rate_percent': round(error_rate, 3),
                        'requests_per_minute': random.randint(100, 1000),
                        'cpu_usage': random.uniform(20, 80),
                        'memory_usage': random.uniform(30, 90)
                    })
            
            return data
        except Exception as e:
            print(f"Error generating sample data: {e}")
            return {'metrics': [], 'services': []}
    
    def analyze_performance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance data and calculate statistics."""
        try:
            analysis = {
                'summary': {},
                'trends': {},
                'recommendations': []
            }
            
            metrics = data['metrics']
            if not metrics:
                return analysis
            
            # Group metrics by service
            service_metrics = {}
            for metric in metrics:
                service = metric['service']
                if service not in service_metrics:
                    service_metrics[service] = []
                service_metrics[service].append(metric)
            
            # Analyze each service
            for service, service_data in service_metrics.items():
                response_times = [m['response_time_ms'] for m in service_data]
                uptimes = [m['uptime_percent'] for m in service_data]
                error_rates = [m['error_rate_percent'] for m in service_data]
                
                analysis['summary'][service] = {
                    'avg_response_time': round(statistics.mean(response_times), 2),
                    'p95_response_time': round(self._percentile(response_times, 95), 2),
                    'p99_response_time': round(self._percentile(response_times, 99), 2),
                    'avg_uptime': round(statistics.mean(uptimes), 3),
                    'min_uptime': round(min(uptimes), 3),
                    'avg_error_rate': round(statistics.mean(error_rates), 3),
                    'max_error_rate': round(max(error_rates), 3),
                    'total_requests': sum(m['requests_per_minute'] for m in service_data)
                }
                
                # Calculate trends (last 7 days vs previous 7 days)
                mid_point = len(service_data) // 2
                recent_data = service_data[mid_point:]
                older_data = service_data[:mid_point]
                
                if recent_data and older_data:
                    recent_avg = statistics.mean([m['response_time_ms'] for m in recent_data])
                    older_avg = statistics.mean([m['response_time_ms'] for m in older_data])
                    trend = ((recent_avg - older_avg) / older_avg) * 100
                    
                    analysis['trends'][service] = {
                        'response_time_trend_percent': round(trend, 2),
                        'trend_direction': 'improving' if trend < -5 else 'degrading' if trend > 5 else 'stable'
                    }
            
            # Generate recommendations
            analysis['recommendations'] = self._generate_recommendations(analysis['summary'])
            
            return analysis
        except Exception as e:
            print(f"Error analyzing performance: {e}")
            return {'summary': {}, 'trends': {}, 'recommendations': []}
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate the nth percentile of a dataset."""
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (index - int(index)) * (upper - lower)
    
    def _generate_recommendations(self, summary: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate optimization recommendations based on performance analysis."""
        recommendations = []
        
        for service, metrics in summary.items():
            # Response time recommendations
            avg_rt = metrics['avg_response_time']
            p99_rt = metrics['p99_response_time']
            
            if avg_rt > self.thresholds['response_time']['poor']:
                recommendations.append({
                    'service': service,
                    'category': 'Response Time',
                    'severity': 'High',
                    'issue': f"Average response time ({avg_rt}ms) exceeds threshold",
                    'recommendation': "Consider database query optimization, caching implementation, or infrastructure scaling"
                })
            elif p99_rt > self.thresholds['response_time']['poor'] * 2:
                recommendations.append({
                    'service': service,
                    'category': 'Response Time',
                    'severity': 'Medium',
                    'issue