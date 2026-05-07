```python
#!/usr/bin/env python3
"""
Website Performance Dashboard Generator

This module creates an automated HTML dashboard that monitors website performance,
visualizes trends with charts, displays current metrics, and provides actionable
optimization recommendations. It performs HTTP requests to test response times,
analyzes performance patterns, and generates a comprehensive dashboard view.

Dependencies: httpx, anthropic (+ standard library)
Usage: python script.py
"""

import asyncio
import json
import time
import statistics
from datetime import datetime, timedelta
from typing import List, Dict, Any
import httpx

# Sample websites to monitor
WEBSITES = [
    "https://httpbin.org/delay/1",
    "https://httpbin.org/delay/2", 
    "https://jsonplaceholder.typicode.com/posts/1",
    "https://api.github.com/zen"
]

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}
        self.historical_data = {}
    
    async def test_website_performance(self, url: str) -> Dict[str, Any]:
        """Test a single website's performance metrics"""
        try:
            start_time = time.time()
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000  # Convert to ms
                
                return {
                    "url": url,
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "content_length": len(response.content),
                    "timestamp": datetime.now().isoformat(),
                    "success": response.status_code < 400
                }
        except Exception as e:
            return {
                "url": url,
                "status_code": 0,
                "response_time": 0,
                "content_length": 0,
                "timestamp": datetime.now().isoformat(),
                "success": False,
                "error": str(e)
            }
    
    async def collect_metrics(self) -> Dict[str, List[Dict[str, Any]]]:
        """Collect performance metrics for all monitored websites"""
        tasks = [self.test_website_performance(url) for url in WEBSITES]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        metrics = {}
        for result in results:
            if isinstance(result, dict):
                url = result["url"]
                if url not in metrics:
                    metrics[url] = []
                metrics[url].append(result)
        
        return metrics
    
    def generate_recommendations(self, url: str, metrics: List[Dict[str, Any]]) -> List[str]:
        """Generate actionable optimization recommendations based on metrics"""
        recommendations = []
        
        if not metrics or not any(m.get("success", False) for m in metrics):
            recommendations.append("❌ Service is unreachable - check server status and DNS configuration")
            return recommendations
        
        successful_metrics = [m for m in metrics if m.get("success", False)]
        if not successful_metrics:
            return recommendations
        
        avg_response_time = statistics.mean([m["response_time"] for m in successful_metrics])
        avg_content_size = statistics.mean([m["content_length"] for m in successful_metrics])
        
        if avg_response_time > 2000:
            recommendations.append("🚨 High response time detected - consider CDN implementation or server optimization")
        elif avg_response_time > 1000:
            recommendations.append("⚠️ Moderate response time - optimize database queries and enable caching")
        else:
            recommendations.append("✅ Good response time performance")
        
        if avg_content_size > 1024 * 1024:  # 1MB
            recommendations.append("📦 Large content size - implement compression and optimize assets")
        elif avg_content_size > 512 * 1024:  # 512KB
            recommendations.append("📦 Consider asset optimization and lazy loading")
        
        error_rate = 1 - (len(successful_metrics) / len(metrics))
        if error_rate > 0.1:
            recommendations.append("⚠️ High error rate detected - investigate server stability")
        elif error_rate > 0:
            recommendations.append("ℹ️ Some errors detected - monitor for patterns")
        else:
            recommendations.append("✅ No errors detected")
        
        return recommendations

def generate_html_dashboard(metrics: Dict[str, List[Dict[str, Any]]], monitor: PerformanceMonitor) -> str:
    """Generate HTML dashboard with performance visualizations"""
    
    # Prepare chart data
    chart_data = {}
    for url, url_metrics in metrics.items():
        chart_data[url] = {
            "response_times": [m["response_time"] for m in url_metrics if m.get("success", False)],
            "timestamps": [m["timestamp"] for m in url_metrics if m.get("success", False)],
            "success_rate": len([m for m in url_metrics if m.get("success", False)]) / len(url_metrics) * 100
        }
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Website Performance Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .header h1 {{ color: #2c3e50; margin: 0; }}
        .header p {{ color: #7f8c8d; margin: 5px 0; }}
        .dashboard {{ display: grid; gap: 20px; max-width: 1400px; margin: 0 auto; }}
        .metric-cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .card {{ background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .card h3 {{ margin: 0 0 15px 0; color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        .metric {{ display: flex; justify-content: space-between; margin: 10px 0; padding: 8px 0; border-bottom: 1px solid #ecf0f1; }}
        .metric:last-child {{ border-bottom: none; }}
        .metric-label {{ font-weight: 500; color: #34495e; }}
        .metric-value {{ font-weight: bold; }}
        .success {{ color: #27ae60; }}
        .warning {{ color: #f39c12; }}
        .error {{ color: #e74c3c; }}
        .recommendations {{ background: #fff; border-radius: 8px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .recommendations h3 {{ margin: 0 0 15px 0; color: #2c3e50; }}
        .recommendations ul {{ list-style: none; padding: 0; margin: 0; }}
        .recommendations li {{ padding: 8px 0; border-bottom: 1px solid #ecf0f1; }}
        .recommendations li:last-child {{ border-bottom: none; }}
        .chart-container {{ background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin: