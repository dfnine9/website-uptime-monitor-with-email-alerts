```python
"""
Performance Optimization Recommendation Engine

This module analyzes web performance data and generates specific optimization 
suggestions including caching strategies, image compression, and CDN recommendations
based on identified bottlenecks.

The engine evaluates various performance metrics to identify bottlenecks and 
provides actionable recommendations for improving website performance.
"""

import json
import time
import statistics
from typing import Dict, List, Any, Tuple
from urllib.parse import urlparse
import re


class PerformanceAnalyzer:
    """Analyzes performance data and generates optimization recommendations."""
    
    def __init__(self):
        self.recommendations = []
        self.bottlenecks = []
        
    def analyze_performance_data(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze performance data and generate recommendations.
        
        Args:
            performance_data: Dictionary containing performance metrics
            
        Returns:
            Dictionary with analysis results and recommendations
        """
        try:
            # Analyze different aspects of performance
            self._analyze_response_times(performance_data.get('response_times', {}))
            self._analyze_resource_sizes(performance_data.get('resource_sizes', {}))
            self._analyze_cache_performance(performance_data.get('cache_metrics', {}))
            self._analyze_image_performance(performance_data.get('image_metrics', {}))
            self._analyze_network_metrics(performance_data.get('network_metrics', {}))
            
            return {
                'bottlenecks': self.bottlenecks,
                'recommendations': self.recommendations,
                'priority_score': self._calculate_priority_score()
            }
            
        except Exception as e:
            print(f"Error analyzing performance data: {e}")
            return {'error': str(e)}
    
    def _analyze_response_times(self, response_times: Dict[str, float]):
        """Analyze response time metrics."""
        try:
            if not response_times:
                return
                
            avg_response_time = statistics.mean(response_times.values())
            max_response_time = max(response_times.values())
            
            if avg_response_time > 2000:  # > 2 seconds
                self.bottlenecks.append({
                    'type': 'slow_response_time',
                    'severity': 'high',
                    'metric': f'Average response time: {avg_response_time:.2f}ms'
                })
                
                self.recommendations.extend([
                    {
                        'category': 'caching',
                        'strategy': 'Implement Redis caching',
                        'description': 'Use Redis for frequently accessed data caching',
                        'expected_improvement': '50-70% response time reduction',
                        'implementation': 'redis.set(key, value, ex=3600)  # 1 hour cache'
                    },
                    {
                        'category': 'cdn',
                        'strategy': 'CloudFront CDN deployment',
                        'description': 'Deploy CloudFront for global content distribution',
                        'expected_improvement': '30-60% faster load times globally',
                        'implementation': 'Configure CloudFront with appropriate cache behaviors'
                    }
                ])
            
            if max_response_time > 5000:  # > 5 seconds
                self.bottlenecks.append({
                    'type': 'extremely_slow_endpoints',
                    'severity': 'critical',
                    'metric': f'Max response time: {max_response_time:.2f}ms'
                })
                
                self.recommendations.append({
                    'category': 'database',
                    'strategy': 'Database query optimization',
                    'description': 'Optimize slow database queries with indexing',
                    'expected_improvement': '70-90% query speed improvement',
                    'implementation': 'CREATE INDEX idx_column ON table(column);'
                })
                
        except Exception as e:
            print(f"Error analyzing response times: {e}")
    
    def _analyze_resource_sizes(self, resource_sizes: Dict[str, int]):
        """Analyze resource size metrics."""
        try:
            if not resource_sizes:
                return
                
            total_size = sum(resource_sizes.values())
            
            # Check for large JavaScript bundles
            js_size = resource_sizes.get('javascript', 0)
            if js_size > 1000000:  # > 1MB
                self.bottlenecks.append({
                    'type': 'large_javascript_bundle',
                    'severity': 'medium',
                    'metric': f'JavaScript size: {js_size / 1000000:.2f}MB'
                })
                
                self.recommendations.extend([
                    {
                        'category': 'optimization',
                        'strategy': 'JavaScript code splitting',
                        'description': 'Split large bundles into smaller chunks',
                        'expected_improvement': '40-60% faster initial page load',
                        'implementation': 'Use dynamic imports: import("./module").then(...)'
                    },
                    {
                        'category': 'compression',
                        'strategy': 'Gzip/Brotli compression',
                        'description': 'Enable compression for JavaScript files',
                        'expected_improvement': '70-80% size reduction',
                        'implementation': 'Configure server: gzip_types application/javascript;'
                    }
                ])
            
            # Check for large CSS files
            css_size = resource_sizes.get('css', 0)
            if css_size > 500000:  # > 500KB
                self.bottlenecks.append({
                    'type': 'large_css_files',
                    'severity': 'low',
                    'metric': f'CSS size: {css_size / 1000:.0f}KB'
                })
                
                self.recommendations.append({
                    'category': 'optimization',
                    'strategy': 'CSS optimization',
                    'description': 'Minify and remove unused CSS',
                    'expected_improvement': '30-50% CSS size reduction',
                    'implementation': 'Use tools like PurgeCSS and cssnano'
                })
                
        except Exception as e:
            print(f"Error analyzing resource sizes: {e}")
    
    def _analyze_cache_performance(self, cache_metrics: Dict[str, Any]):
        """Analyze cache performance metrics."""
        try:
            if not cache_metrics:
                return
                
            hit_rate = cache_metrics.get('hit_rate', 0)
            miss_rate = cache_metrics.get('miss_rate', 0)
            
            if hit_rate < 0.7:  # < 70% hit rate
                self.bottlenecks.append({
                    'type': 'low_cache_hit_rate',
                    'severity': 'medium',
                    'metric': f'Cache hit rate: {hit_rate * 100:.1f}%'
                })
                
                self.recommendations.extend([
                    {
                        'category': 'caching',
                        'strategy': 'Optimize cache TTL',
                        'description': 'Adjust cache expiration times for better hit rates',
                        'expected_improvement': '20-40% hit rate improvement',
                        'implementation': 'Cache-Control: max-age=86400, must-revalidate'
                    },
                    {
                        'category': 'caching',
                        'strategy': 'Implement cache warming',
                        'description': 'Pre-populate cache with frequently accessed data',
                        'expected_improvement': '15-30% better cache performance',
                        'implementation': 'Scheduled cache warming jobs'
                    }
                ])
                
        except Exception as e:
            print(f"Error analyzing cache performance: {e}")
    
    def _analyze_image_performance(self, image_metrics: Dict[str, Any]):
        """Analyze image performance metrics."""
        try:
            if not image_metrics:
                return
                
            total_image_size = image_metrics.get('total_size', 0)
            unoptimized_images = image_metrics.get('unoptimized_count',