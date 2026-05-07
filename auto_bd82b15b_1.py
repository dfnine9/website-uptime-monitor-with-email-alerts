```python
"""
System Monitoring Report Generator

This module creates formatted HTML and plain text email templates for system monitoring data.
It generates status summaries, performance alerts, and trend indicators based on mock
monitoring data. The module is designed to be self-contained and easily integrated
into existing monitoring systems.

Features:
- HTML email template generation with embedded CSS
- Plain text email template for compatibility
- Performance alert detection and categorization
- Trend analysis with visual indicators
- Status summary dashboard
- Error handling and logging
"""

import json
import datetime
import statistics
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class AlertLevel(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"
    SUCCESS = "success"


class TrendDirection(Enum):
    """Trend direction indicators"""
    UP = "↗"
    DOWN = "↘"
    STABLE = "→"
    VOLATILE = "↕"


@dataclass
class MetricData:
    """Container for metric data points"""
    name: str
    current_value: float
    historical_values: List[float]
    unit: str
    threshold_warning: float
    threshold_critical: float
    
    def get_alert_level(self) -> AlertLevel:
        """Determine alert level based on thresholds"""
        if self.current_value >= self.threshold_critical:
            return AlertLevel.CRITICAL
        elif self.current_value >= self.threshold_warning:
            return AlertLevel.WARNING
        else:
            return AlertLevel.SUCCESS
    
    def get_trend(self) -> TrendDirection:
        """Calculate trend direction from historical data"""
        if len(self.historical_values) < 2:
            return TrendDirection.STABLE
        
        recent_avg = statistics.mean(self.historical_values[-3:])
        older_avg = statistics.mean(self.historical_values[:-3]) if len(self.historical_values) > 3 else self.historical_values[0]
        
        change_percent = ((recent_avg - older_avg) / older_avg * 100) if older_avg != 0 else 0
        
        if abs(change_percent) < 5:
            return TrendDirection.STABLE
        elif change_percent > 15:
            return TrendDirection.UP
        elif change_percent < -15:
            return TrendDirection.DOWN
        else:
            return TrendDirection.VOLATILE


class MonitoringReporter:
    """Main class for generating monitoring reports"""
    
    def __init__(self):
        self.timestamp = datetime.datetime.now()
        self.metrics: List[MetricData] = []
    
    def add_metric(self, metric: MetricData) -> None:
        """Add a metric to the report"""
        self.metrics.append(metric)
    
    def generate_mock_data(self) -> None:
        """Generate mock monitoring data for demonstration"""
        mock_metrics = [
            MetricData(
                name="CPU Usage",
                current_value=85.3,
                historical_values=[72.1, 68.9, 75.2, 78.4, 82.1, 85.3],
                unit="%",
                threshold_warning=80.0,
                threshold_critical=95.0
            ),
            MetricData(
                name="Memory Usage",
                current_value=67.8,
                historical_values=[65.2, 66.1, 68.9, 69.2, 67.5, 67.8],
                unit="%",
                threshold_warning=80.0,
                threshold_critical=90.0
            ),
            MetricData(
                name="Disk I/O",
                current_value=234.7,
                historical_values=[180.2, 195.1, 210.3, 225.8, 230.1, 234.7],
                unit="MB/s",
                threshold_warning=200.0,
                threshold_critical=300.0
            ),
            MetricData(
                name="Network Latency",
                current_value=45.2,
                historical_values=[42.1, 38.9, 41.2, 44.8, 46.1, 45.2],
                unit="ms",
                threshold_warning=50.0,
                threshold_critical=100.0
            ),
            MetricData(
                name="Error Rate",
                current_value=0.12,
                historical_values=[0.05, 0.03, 0.08, 0.10, 0.11, 0.12],
                unit="%",
                threshold_warning=0.10,
                threshold_critical=0.50
            )
        ]
        
        self.metrics.extend(mock_metrics)
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Generate overall status summary"""
        try:
            alert_counts = {level: 0 for level in AlertLevel}
            
            for metric in self.metrics:
                alert_level = metric.get_alert_level()
                alert_counts[alert_level] += 1
            
            total_metrics = len(self.metrics)
            health_score = (alert_counts[AlertLevel.SUCCESS] / total_metrics * 100) if total_metrics > 0 else 0
            
            # Determine overall status
            if alert_counts[AlertLevel.CRITICAL] > 0:
                overall_status = "CRITICAL"
            elif alert_counts[AlertLevel.WARNING] > 0:
                overall_status = "WARNING"
            else:
                overall_status = "HEALTHY"
            
            return {
                "overall_status": overall_status,
                "health_score": round(health_score, 1),
                "total_metrics": total_metrics,
                "critical_alerts": alert_counts[AlertLevel.CRITICAL],
                "warning_alerts": alert_counts[AlertLevel.WARNING],
                "healthy_metrics": alert_counts[AlertLevel.SUCCESS],
                "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
        
        except Exception as e:
            print(f"Error generating status summary: {e}")
            return {
                "overall_status": "UNKNOWN",
                "health_score": 0,
                "total_metrics": 0,
                "critical_alerts": 0,
                "warning_alerts": 0,
                "healthy_metrics": 0,
                "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def get_performance_alerts(self) -> List[Dict[str, Any]]:
        """Get list of performance alerts"""
        alerts = []
        
        try:
            for metric in self.metrics:
                alert_level = metric.get_alert_level()
                if alert_level in [AlertLevel.WARNING, AlertLevel.CRITICAL]:
                    trend = metric.get_trend()
                    alerts.append({
                        "metric_name": metric.name,
                        "current_value": metric.current_value,
                        "unit": metric.unit,
                        "alert_level": alert_level.value,
                        "threshold": metric.threshold_critical if alert_level == AlertLevel.CRITICAL else metric.threshold_warning,
                        "trend": trend.value,
                        "message": self._generate_alert_message(metric, alert_level, trend)
                    })
            
            # Sort by severity (critical first)
            alerts.sort(key=lambda x: x["alert_level"] == "critical", reverse=True)
            
        except Exception as e:
            print(f"Error generating performance alerts: {e}")
        
        return alerts
    
    def _generate_alert_message(self, metric: MetricData, alert_level: AlertLevel, trend: TrendDirection) -> str:
        """Generate descriptive alert message"""
        try:
            severity = "CRITICAL" if alert_level == AlertLevel.CRITICAL else "WARNING"
            trend_desc = {
                TrendDirection.UP: "increasing",
                TrendDirection.DOWN: "decreasing", 
                TrendDirection.STABLE: "stable",
                TrendDirection.VOLATILE: "volatile