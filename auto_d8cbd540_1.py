```python
"""
Performance Data Analysis Script

This script analyzes CSV performance data to identify statistical trends and anomalies.
It calculates key metrics including averages, percentiles, and degradation patterns
using pandas and numpy for comprehensive performance monitoring.

Features:
- Reads CSV performance data from file or generates sample data
- Calculates statistical trends (mean, median, percentiles)
- Identifies performance degradation patterns
- Detects anomalies using statistical methods
- Outputs comprehensive analysis results

Usage: python script.py
"""

import csv
import json
import statistics
import math
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
import random


class PerformanceAnalyzer:
    """Analyzes performance metrics and identifies trends and anomalies."""
    
    def __init__(self):
        self.data = []
        self.metrics = {}
        
    def generate_sample_data(self, filename: str = "performance_data.csv") -> None:
        """Generate sample CSV performance data for testing."""
        try:
            with open(filename, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['timestamp', 'response_time', 'cpu_usage', 'memory_usage', 'throughput', 'error_rate'])
                
                base_time = datetime.now() - timedelta(days=30)
                for i in range(1000):
                    timestamp = (base_time + timedelta(hours=i/30)).isoformat()
                    # Simulate gradual degradation with some noise
                    degradation_factor = 1 + (i / 5000)
                    response_time = max(50, 100 * degradation_factor + random.gauss(0, 20))
                    cpu_usage = min(100, 30 + (i / 100) + random.gauss(0, 10))
                    memory_usage = min(100, 40 + (i / 80) + random.gauss(0, 8))
                    throughput = max(10, 100 - (i / 50) + random.gauss(0, 15))
                    error_rate = min(10, (i / 500) + random.gauss(0, 1))
                    
                    writer.writerow([timestamp, response_time, cpu_usage, memory_usage, throughput, error_rate])
                    
            print(f"Generated sample data in {filename}")
        except Exception as e:
            print(f"Error generating sample data: {e}")
            raise
    
    def read_csv_data(self, filename: str) -> None:
        """Read performance data from CSV file."""
        try:
            with open(filename, 'r') as file:
                reader = csv.DictReader(file)
                self.data = []
                for row in reader:
                    # Convert numeric columns
                    numeric_row = {'timestamp': row['timestamp']}
                    for key in ['response_time', 'cpu_usage', 'memory_usage', 'throughput', 'error_rate']:
                        try:
                            numeric_row[key] = float(row[key])
                        except (ValueError, KeyError):
                            numeric_row[key] = 0.0
                    self.data.append(numeric_row)
                    
            print(f"Loaded {len(self.data)} records from {filename}")
        except FileNotFoundError:
            print(f"File {filename} not found. Generating sample data...")
            self.generate_sample_data(filename)
            self.read_csv_data(filename)
        except Exception as e:
            print(f"Error reading CSV data: {e}")
            raise
    
    def calculate_percentile(self, values: List[float], percentile: float) -> float:
        """Calculate the specified percentile of a list of values."""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        k = (len(sorted_values) - 1) * (percentile / 100)
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return sorted_values[int(k)]
        return sorted_values[int(f)] * (c - k) + sorted_values[int(c)] * (k - f)
    
    def detect_anomalies(self, values: List[float], metric_name: str) -> List[int]:
        """Detect anomalies using statistical methods (IQR and Z-score)."""
        if len(values) < 4:
            return []
            
        try:
            mean_val = statistics.mean(values)
            stdev_val = statistics.stdev(values) if len(values) > 1 else 0
            
            q1 = self.calculate_percentile(values, 25)
            q3 = self.calculate_percentile(values, 75)
            iqr = q3 - q1
            
            anomalies = []
            for i, value in enumerate(values):
                # Z-score method (values beyond 2 standard deviations)
                z_score = abs((value - mean_val) / stdev_val) if stdev_val > 0 else 0
                
                # IQR method (values beyond 1.5 * IQR from quartiles)
                iqr_outlier = value < (q1 - 1.5 * iqr) or value > (q3 + 1.5 * iqr)
                
                if z_score > 2 or iqr_outlier:
                    anomalies.append(i)
                    
            return anomalies
        except Exception as e:
            print(f"Error detecting anomalies for {metric_name}: {e}")
            return []
    
    def calculate_degradation_trend(self, values: List[float]) -> Dict[str, Any]:
        """Calculate degradation trend using linear regression approximation."""
        if len(values) < 2:
            return {'slope': 0, 'trend': 'insufficient_data'}
            
        try:
            n = len(values)
            x_values = list(range(n))
            
            # Calculate slope using least squares method
            sum_x = sum(x_values)
            sum_y = sum(values)
            sum_xy = sum(x * y for x, y in zip(x_values, values))
            sum_x2 = sum(x * x for x in x_values)
            
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            
            # Determine trend direction
            if abs(slope) < 0.01:
                trend = 'stable'
            elif slope > 0:
                trend = 'degrading' if 'response_time' in str(values) or 'error_rate' in str(values) else 'improving'
            else:
                trend = 'improving' if 'response_time' in str(values) or 'error_rate' in str(values) else 'degrading'
                
            return {
                'slope': slope,
                'trend': trend,
                'change_rate': abs(slope) * 100  # Percentage change per unit time
            }
        except Exception as e:
            print(f"Error calculating degradation trend: {e}")
            return {'slope': 0, 'trend': 'error'}
    
    def analyze_metrics(self) -> None:
        """Calculate comprehensive statistical analysis for all metrics."""
        if not self.data:
            print("No data available for analysis")
            return
            
        metrics = ['response_time', 'cpu_usage', 'memory_usage', 'throughput', 'error_rate']
        
        for metric in metrics:
            try:
                values = [row[metric] for row in self.data if metric in row]
                if not values:
                    continue
                    
                # Basic statistics
                mean_val = statistics.mean(values)
                median_val = statistics.median(values)
                std_dev = statistics.stdev(values) if len(values) > 1 else 0
                
                # Percentiles
                p95 = self.calculate_percentile(