```python
#!/usr/bin/env python3
"""
Financial Insights Engine

A comprehensive spending analysis tool that processes financial transaction data to:
- Identify spending anomalies using statistical methods
- Calculate monthly spending averages and trends
- Detect unusual spending spikes above normal patterns
- Generate actionable financial recommendations based on patterns

Uses statistical analysis including standard deviation, z-scores, and percentile-based
outlier detection to provide meaningful insights into spending behavior.

Usage: python script.py
"""

import json
import statistics
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Tuple, Any
import math


class SpendingInsightsEngine:
    def __init__(self):
        self.transactions = []
        self.monthly_data = defaultdict(list)
        self.category_data = defaultdict(list)
        
    def load_sample_data(self) -> None:
        """Generate sample transaction data for analysis"""
        try:
            import random
            
            categories = ['Food', 'Transport', 'Entertainment', 'Utilities', 'Shopping', 'Healthcare', 'Insurance']
            base_amounts = {'Food': 50, 'Transport': 30, 'Entertainment': 80, 'Utilities': 120, 
                          'Shopping': 100, 'Healthcare': 200, 'Insurance': 150}
            
            # Generate 6 months of sample data
            start_date = datetime(2024, 1, 1)
            
            for i in range(180):  # 6 months of daily possibilities
                current_date = start_date + timedelta(days=i)
                
                # Random number of transactions per day (0-3)
                daily_transactions = random.randint(0, 3)
                
                for _ in range(daily_transactions):
                    category = random.choice(categories)
                    base_amount = base_amounts[category]
                    
                    # Normal spending with some variation
                    if random.random() < 0.95:  # 95% normal spending
                        amount = base_amount * random.uniform(0.5, 1.8)
                    else:  # 5% anomalous spending
                        amount = base_amount * random.uniform(3.0, 8.0)
                    
                    transaction = {
                        'date': current_date.strftime('%Y-%m-%d'),
                        'amount': round(amount, 2),
                        'category': category,
                        'description': f'{category} purchase'
                    }
                    self.transactions.append(transaction)
                    
        except Exception as e:
            print(f"Error generating sample data: {e}")
            raise
    
    def process_transactions(self) -> None:
        """Process transactions into monthly and category groupings"""
        try:
            for transaction in self.transactions:
                date_obj = datetime.strptime(transaction['date'], '%Y-%m-%d')
                month_key = date_obj.strftime('%Y-%m')
                
                self.monthly_data[month_key].append(transaction['amount'])
                self.category_data[transaction['category']].append(transaction['amount'])
                
        except Exception as e:
            print(f"Error processing transactions: {e}")
            raise
    
    def calculate_monthly_averages(self) -> Dict[str, float]:
        """Calculate average spending per month"""
        try:
            monthly_averages = {}
            
            for month, amounts in self.monthly_data.items():
                monthly_averages[month] = {
                    'average': statistics.mean(amounts),
                    'total': sum(amounts),
                    'transaction_count': len(amounts),
                    'median': statistics.median(amounts)
                }
                
            return monthly_averages
            
        except Exception as e:
            print(f"Error calculating monthly averages: {e}")
            return {}
    
    def detect_anomalies(self, threshold: float = 2.0) -> List[Dict]:
        """Detect spending anomalies using z-score analysis"""
        try:
            anomalies = []
            
            for category, amounts in self.category_data.items():
                if len(amounts) < 3:  # Need minimum data points
                    continue
                    
                mean_amount = statistics.mean(amounts)
                std_dev = statistics.stdev(amounts) if len(amounts) > 1 else 0
                
                if std_dev == 0:
                    continue
                
                for i, amount in enumerate(amounts):
                    z_score = abs((amount - mean_amount) / std_dev)
                    
                    if z_score > threshold:
                        # Find corresponding transaction
                        category_transactions = [t for t in self.transactions if t['category'] == category]
                        if i < len(category_transactions):
                            transaction = category_transactions[i]
                            anomalies.append({
                                'transaction': transaction,
                                'z_score': round(z_score, 2),
                                'category_average': round(mean_amount, 2),
                                'deviation_percent': round(((amount - mean_amount) / mean_amount) * 100, 1)
                            })
            
            return sorted(anomalies, key=lambda x: x['z_score'], reverse=True)
            
        except Exception as e:
            print(f"Error detecting anomalies: {e}")
            return []
    
    def detect_spending_spikes(self) -> List[Dict]:
        """Detect unusual spending spikes by comparing to historical patterns"""
        try:
            spikes = []
            monthly_averages = self.calculate_monthly_averages()
            
            if len(monthly_averages) < 2:
                return spikes
            
            # Calculate overall average monthly spending
            total_averages = [data['total'] for data in monthly_averages.values()]
            overall_mean = statistics.mean(total_averages)
            overall_std = statistics.stdev(total_averages) if len(total_averages) > 1 else 0
            
            for month, data in monthly_averages.items():
                if overall_std > 0:
                    z_score = (data['total'] - overall_mean) / overall_std
                    
                    if z_score > 1.5:  # Spike threshold
                        spikes.append({
                            'month': month,
                            'total_spending': round(data['total'], 2),
                            'average_spending': round(overall_mean, 2),
                            'spike_percentage': round(((data['total'] - overall_mean) / overall_mean) * 100, 1),
                            'z_score': round(z_score, 2)
                        })
            
            return sorted(spikes, key=lambda x: x['z_score'], reverse=True)
            
        except Exception as e:
            print(f"Error detecting spending spikes: {e}")
            return []
    
    def generate_recommendations(self, monthly_averages: Dict, anomalies: List, spikes: List) -> List[str]:
        """Generate actionable financial recommendations based on analysis"""
        try:
            recommendations = []
            
            # Overall spending trend analysis
            if len(monthly_averages) >= 3:
                months = sorted(monthly_averages.keys())
                recent_months = months[-3:]
                early_months = months[:3]
                
                recent_avg = statistics.mean([monthly_averages[m]['total'] for m in recent_months])
                early_avg = statistics.mean([monthly_averages[m]['total'] for m in early_months])
                
                trend_change = ((recent_avg - early_avg) / early_avg) * 100
                
                if trend_change > 15:
                    recommendations.append(f"⚠️  Spending has increased by {trend_change:.1f}% over recent months. Consider reviewing your budget.")
                elif trend_change < -15:
                    recommendations.append(f"✅ Great job! Spending has decreased by {abs(trend_change):.1f}% recently.")
            
            # Anomaly-based recommendations
            if len(anomalies) > 5:
                top_anomaly_categories = {}
                for anomaly in anomalies[:10]: