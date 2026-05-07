```python
#!/usr/bin/env python3
"""
Monthly Budget Insights Generator

A self-contained Python script that analyzes spending patterns against predefined budgets.
Generates automated insights including variance analysis and data visualizations.

Features:
- Compares actual spending vs budget limits across categories
- Calculates variance percentages and identifies over/under-budget items
- Creates visual charts using matplotlib
- Provides actionable budget insights and recommendations

Usage: python script.py
"""

import json
import random
from datetime import datetime, timedelta
import sys

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available. Visual charts will be skipped.")

class BudgetAnalyzer:
    def __init__(self):
        self.budget_data = {
            "budget_limits": {
                "Housing": 1500,
                "Food": 600,
                "Transportation": 400,
                "Entertainment": 200,
                "Utilities": 150,
                "Healthcare": 250,
                "Shopping": 300,
                "Miscellaneous": 100
            },
            "actual_spending": {}
        }
        self.insights = []
        
    def generate_sample_data(self):
        """Generate realistic sample spending data for demonstration"""
        try:
            # Generate spending data with some variance
            for category, budget in self.budget_data["budget_limits"].items():
                # Add realistic variance (-30% to +40% of budget)
                variance_factor = random.uniform(0.7, 1.4)
                actual = round(budget * variance_factor, 2)
                self.budget_data["actual_spending"][category] = actual
            
            print("✓ Sample spending data generated successfully")
            
        except Exception as e:
            print(f"Error generating sample data: {e}")
            sys.exit(1)
    
    def calculate_variances(self):
        """Calculate variance percentages for each budget category"""
        try:
            variances = {}
            
            for category in self.budget_data["budget_limits"]:
                budget = self.budget_data["budget_limits"][category]
                actual = self.budget_data["actual_spending"].get(category, 0)
                
                # Calculate variance percentage
                variance = ((actual - budget) / budget) * 100
                variances[category] = {
                    "budget": budget,
                    "actual": actual,
                    "variance_pct": round(variance, 1),
                    "variance_amount": round(actual - budget, 2),
                    "status": "over" if variance > 0 else "under"
                }
            
            print("✓ Variance calculations completed")
            return variances
            
        except Exception as e:
            print(f"Error calculating variances: {e}")
            return {}
    
    def generate_insights(self, variances):
        """Generate actionable budget insights"""
        try:
            insights = []
            total_budget = sum(self.budget_data["budget_limits"].values())
            total_actual = sum(self.budget_data["actual_spending"].values())
            overall_variance = ((total_actual - total_budget) / total_budget) * 100
            
            # Overall budget performance
            if overall_variance > 10:
                insights.append(f"🚨 ALERT: Overall spending is {abs(overall_variance):.1f}% over budget")
            elif overall_variance > 0:
                insights.append(f"⚠️  CAUTION: Overall spending is {overall_variance:.1f}% over budget")
            else:
                insights.append(f"✅ GOOD: Overall spending is {abs(overall_variance):.1f}% under budget")
            
            # Category-specific insights
            over_budget = [(cat, data) for cat, data in variances.items() if data["variance_pct"] > 0]
            under_budget = [(cat, data) for cat, data in variances.items() if data["variance_pct"] < 0]
            
            if over_budget:
                over_budget.sort(key=lambda x: x[1]["variance_pct"], reverse=True)
                worst_category, worst_data = over_budget[0]
                insights.append(f"📈 Highest overspend: {worst_category} (+{worst_data['variance_pct']}%, ${worst_data['variance_amount']})")
            
            if under_budget:
                under_budget.sort(key=lambda x: x[1]["variance_pct"])
                best_category, best_data = under_budget[0]
                insights.append(f"💰 Best savings: {best_category} ({best_data['variance_pct']}%, ${abs(best_data['variance_amount'])} saved)")
            
            # Recommendations
            if len(over_budget) >= 3:
                insights.append("💡 RECOMMENDATION: Review spending habits in multiple categories")
            
            if any(data["variance_pct"] > 50 for _, data in over_budget):
                insights.append("🎯 ACTION ITEM: Set up spending alerts for high-variance categories")
            
            self.insights = insights
            print("✓ Budget insights generated")
            return insights
            
        except Exception as e:
            print(f"Error generating insights: {e}")
            return []
    
    def create_visualizations(self, variances):
        """Create budget visualization charts"""
        if not MATPLOTLIB_AVAILABLE:
            print("⚠️  Skipping visualizations - matplotlib not available")
            return
        
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('Monthly Budget Analysis Dashboard', fontsize=16, fontweight='bold')
            
            # Chart 1: Budget vs Actual Spending (Bar Chart)
            categories = list(variances.keys())
            budgets = [variances[cat]["budget"] for cat in categories]
            actuals = [variances[cat]["actual"] for cat in categories]
            
            x_pos = range(len(categories))
            width = 0.35
            
            bars1 = ax1.bar([x - width/2 for x in x_pos], budgets, width, 
                           label='Budget', color='lightblue', alpha=0.7)
            bars2 = ax1.bar([x + width/2 for x in x_pos], actuals, width,
                           label='Actual', color='lightcoral', alpha=0.7)
            
            ax1.set_xlabel('Categories')
            ax1.set_ylabel('Amount ($)')
            ax1.set_title('Budget vs Actual Spending')
            ax1.set_xticks(x_pos)
            ax1.set_xticklabels(categories, rotation=45, ha='right')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Chart 2: Variance Percentages (Horizontal Bar Chart)
            variance_pcts = [variances[cat]["variance_pct"] for cat in categories]
            colors = ['red' if v > 0 else 'green' for v in variance_pcts]
            
            y_pos = range(len(categories))
            bars = ax2.barh(y_pos, variance_pcts, color=colors, alpha=0.7)
            
            ax2.set_ylabel('Categories')
            ax2.set_xlabel('Variance Percentage (%)')
            ax2.set_title('Budget Variance by Category')
            ax2.set_yticks(y_pos)
            ax2.set_yticklabels(categories)
            ax2.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
            ax2.grid(True, alpha=0.3)
            
            # Add percentage labels on bars
            for i, (bar, pct) in enumerate(zip(bars, variance_pcts)):
                ax2.text(pct + (1 if pct > 0 else -1), i, f'{pct:.1f}%',