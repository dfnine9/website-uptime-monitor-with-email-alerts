```python
"""
Budget Insights Engine

A comprehensive financial analysis tool that processes spending data to:
- Analyze spending patterns and trends
- Identify unusual or anomalous expenses
- Suggest budget optimizations based on spending behavior
- Generate actionable financial recommendations

The engine uses statistical analysis to detect spending anomalies and provides
personalized recommendations for budget improvement.
"""

import json
import statistics
import datetime
from collections import defaultdict, Counter
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple
import random
import math

@dataclass
class Transaction:
    date: str
    amount: float
    category: str
    description: str
    merchant: str

class BudgetInsightsEngine:
    def __init__(self):
        self.transactions = []
        self.categories = {
            'food': ['restaurant', 'grocery', 'cafe', 'takeout', 'delivery'],
            'transportation': ['gas', 'uber', 'lyft', 'parking', 'metro', 'bus'],
            'entertainment': ['movie', 'concert', 'game', 'streaming', 'music'],
            'shopping': ['amazon', 'target', 'mall', 'clothing', 'electronics'],
            'utilities': ['electric', 'water', 'internet', 'phone', 'cable'],
            'healthcare': ['doctor', 'pharmacy', 'hospital', 'dental', 'vision'],
            'housing': ['rent', 'mortgage', 'insurance', 'maintenance'],
            'other': []
        }
    
    def generate_sample_data(self) -> List[Transaction]:
        """Generate realistic sample transaction data for demonstration"""
        merchants = {
            'food': ['Chipotle', 'Whole Foods', 'Starbucks', 'McDonalds', 'Local Deli'],
            'transportation': ['Shell Gas', 'Uber', 'Metro Card', 'Parking Meter'],
            'entertainment': ['Netflix', 'Spotify', 'AMC Theaters', 'Steam'],
            'shopping': ['Amazon', 'Target', 'Best Buy', 'Macy\'s'],
            'utilities': ['Electric Co', 'Water Dept', 'Verizon', 'Comcast'],
            'healthcare': ['CVS Pharmacy', 'Dr. Smith', 'LabCorp'],
            'housing': ['Rent Payment', 'Home Insurance', 'Repairs Inc']
        }
        
        base_amounts = {
            'food': (8, 85), 'transportation': (3, 45), 'entertainment': (5, 60),
            'shopping': (15, 200), 'utilities': (50, 300), 'healthcare': (20, 400),
            'housing': (800, 2500)
        }
        
        transactions = []
        start_date = datetime.datetime.now() - datetime.timedelta(days=90)
        
        for i in range(150):
            date = start_date + datetime.timedelta(days=random.randint(0, 90))
            category = random.choice(list(merchants.keys()))
            merchant = random.choice(merchants[category])
            
            min_amt, max_amt = base_amounts[category]
            amount = round(random.uniform(min_amt, max_amt), 2)
            
            # Add some anomalies (10% chance of unusual expense)
            if random.random() < 0.1:
                amount *= random.uniform(2.5, 4.0)
            
            transaction = Transaction(
                date=date.strftime('%Y-%m-%d'),
                amount=amount,
                category=category,
                description=f"{merchant} purchase",
                merchant=merchant
            )
            transactions.append(transaction)
        
        return sorted(transactions, key=lambda x: x.date)
    
    def load_transactions(self, transactions: List[Transaction]):
        """Load transaction data into the engine"""
        self.transactions = transactions
    
    def analyze_spending_patterns(self) -> Dict[str, Any]:
        """Analyze spending patterns across categories and time periods"""
        try:
            if not self.transactions:
                return {"error": "No transactions to analyze"}
            
            # Category analysis
            category_totals = defaultdict(float)
            category_counts = defaultdict(int)
            monthly_spending = defaultdict(float)
            daily_spending = defaultdict(float)
            
            for transaction in self.transactions:
                category_totals[transaction.category] += transaction.amount
                category_counts[transaction.category] += 1
                
                # Monthly analysis
                month_key = transaction.date[:7]  # YYYY-MM
                monthly_spending[month_key] += transaction.amount
                
                # Daily analysis
                daily_spending[transaction.date] += transaction.amount
            
            # Calculate statistics
            total_spending = sum(category_totals.values())
            avg_daily_spending = total_spending / max(len(set(t.date for t in self.transactions)), 1)
            
            # Category percentages
            category_percentages = {
                cat: (amount / total_spending * 100) if total_spending > 0 else 0
                for cat, amount in category_totals.items()
            }
            
            return {
                "total_spending": round(total_spending, 2),
                "avg_daily_spending": round(avg_daily_spending, 2),
                "category_totals": dict(category_totals),
                "category_percentages": category_percentages,
                "category_counts": dict(category_counts),
                "monthly_trends": dict(monthly_spending),
                "transaction_count": len(self.transactions)
            }
        
        except Exception as e:
            return {"error": f"Error analyzing spending patterns: {str(e)}"}
    
    def identify_unusual_expenses(self) -> List[Dict[str, Any]]:
        """Identify anomalous transactions using statistical analysis"""
        try:
            unusual_expenses = []
            
            # Group by category for anomaly detection
            category_amounts = defaultdict(list)
            for transaction in self.transactions:
                category_amounts[transaction.category].append(transaction.amount)
            
            # Find outliers in each category
            for category, amounts in category_amounts.items():
                if len(amounts) < 3:
                    continue
                
                mean_amount = statistics.mean(amounts)
                stdev_amount = statistics.stdev(amounts) if len(amounts) > 1 else 0
                
                # Use z-score to identify outliers (threshold: 2.5 standard deviations)
                threshold = 2.5
                
                for transaction in self.transactions:
                    if transaction.category == category:
                        if stdev_amount > 0:
                            z_score = abs(transaction.amount - mean_amount) / stdev_amount
                            if z_score > threshold:
                                unusual_expenses.append({
                                    "transaction": transaction.__dict__,
                                    "z_score": round(z_score, 2),
                                    "category_avg": round(mean_amount, 2),
                                    "deviation": round(transaction.amount - mean_amount, 2),
                                    "reason": f"Amount significantly above category average"
                                })
            
            # Sort by z-score descending
            unusual_expenses.sort(key=lambda x: x["z_score"], reverse=True)
            
            return unusual_expenses[:10]  # Top 10 unusual expenses
        
        except Exception as e:
            return [{"error": f"Error identifying unusual expenses: {str(e)}"}]
    
    def suggest_budget_optimizations(self, patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate budget optimization suggestions based on spending patterns"""
        try:
            suggestions = []
            
            if "category_percentages" not in patterns:
                return [{"error": "Invalid patterns data for optimization"}]
            
            category_percentages = patterns["category_percentages"]
            category_totals = patterns.get("category_totals", {})
            
            # Recommended budget allocations (as percentages)
            recommended_allocations = {
                'housing': 30, 'food': 15, 'transportation': 15,
                'utilities':