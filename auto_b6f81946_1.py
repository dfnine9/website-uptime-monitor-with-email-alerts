```python
#!/usr/bin/env python3
"""
Financial Data Visualization Module

This module reads JSON summary statistics and generates interactive charts for financial data analysis.
It creates:
- Pie charts for category breakdown of expenses
- Line graphs for spending trends over time
- Bar charts for monthly spending comparisons

The module uses matplotlib for visualization and includes comprehensive error handling.
All charts are saved as PNG files and optionally displayed interactively.

Usage: python script.py

Requirements:
- Python 3.6+
- matplotlib (installed automatically if missing)
- JSON data file with financial statistics
"""

import json
import sys
import subprocess
import importlib
from datetime import datetime
from typing import Dict, List, Any, Optional

def install_package(package: str) -> bool:
    """Install a package using pip if it's not available."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def import_with_fallback(package: str, install_name: Optional[str] = None):
    """Import a package, installing it if necessary."""
    install_name = install_name or package
    try:
        return importlib.import_module(package)
    except ImportError:
        print(f"Installing {install_name}...")
        if install_package(install_name):
            return importlib.import_module(package)
        else:
            raise ImportError(f"Failed to install {install_name}")

# Import required packages
plt = import_with_fallback("matplotlib.pyplot", "matplotlib")
np = import_with_fallback("numpy", "numpy")

class FinancialDataVisualizer:
    """Handles creation of financial data visualizations."""
    
    def __init__(self):
        """Initialize the visualizer with default settings."""
        plt.style.use('seaborn-v0_8' if hasattr(plt.style, 'seaborn-v0_8') else 'default')
        self.colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8']
    
    def load_json_data(self, filename: str) -> Dict[str, Any]:
        """Load JSON data from file with error handling."""
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                data = json.load(file)
                print(f"Successfully loaded data from {filename}")
                return data
        except FileNotFoundError:
            print(f"Error: File {filename} not found.")
            return self.generate_sample_data()
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON format in {filename}: {e}")
            return self.generate_sample_data()
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            return self.generate_sample_data()
    
    def generate_sample_data(self) -> Dict[str, Any]:
        """Generate sample financial data for demonstration."""
        print("Generating sample data for demonstration...")
        return {
            "categories": {
                "Food": 1250.50,
                "Transportation": 450.75,
                "Utilities": 320.25,
                "Entertainment": 280.00,
                "Healthcare": 180.50,
                "Shopping": 520.80,
                "Other": 150.25
            },
            "monthly_spending": {
                "2024-01": 1850.25,
                "2024-02": 2100.50,
                "2024-03": 1950.75,
                "2024-04": 2250.00,
                "2024-05": 2050.25,
                "2024-06": 2180.50
            },
            "trends": {
                "2024-01-01": 450.25,
                "2024-01-15": 520.50,
                "2024-02-01": 480.75,
                "2024-02-15": 510.25,
                "2024-03-01": 590.50,
                "2024-03-15": 520.75,
                "2024-04-01": 620.25,
                "2024-04-15": 580.50
            },
            "summary": {
                "total_spending": 12432.05,
                "average_monthly": 2072.01,
                "top_category": "Food"
            }
        }
    
    def create_pie_chart(self, data: Dict[str, float], title: str, filename: str) -> None:
        """Create a pie chart for category breakdown."""
        try:
            plt.figure(figsize=(10, 8))
            
            # Prepare data
            labels = list(data.keys())
            sizes = list(data.values())
            colors = self.colors[:len(labels)]
            
            # Create pie chart
            wedges, texts, autotexts = plt.pie(
                sizes, 
                labels=labels, 
                colors=colors,
                autopct='%1.1f%%',
                startangle=90,
                explode=[0.05 if size == max(sizes) else 0 for size in sizes]
            )
            
            # Enhance appearance
            plt.setp(autotexts, size=10, weight="bold")
            plt.setp(texts, size=11)
            
            plt.title(title, fontsize=16, fontweight='bold', pad=20)
            plt.axis('equal')
            
            # Add legend
            plt.legend(wedges, [f"{label}: ${size:,.2f}" for label, size in zip(labels, sizes)],
                      title="Categories", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
            
            plt.tight_layout()
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"Pie chart saved as {filename}")
            plt.close()
            
        except Exception as e:
            print(f"Error creating pie chart: {e}")
    
    def create_line_chart(self, data: Dict[str, float], title: str, filename: str) -> None:
        """Create a line chart for spending trends over time."""
        try:
            plt.figure(figsize=(12, 6))
            
            # Prepare data
            dates = list(data.keys())
            values = list(data.values())
            
            # Convert dates to datetime objects for better formatting
            try:
                datetime_dates = [datetime.strptime(date, "%Y-%m-%d") for date in dates]
            except ValueError:
                try:
                    datetime_dates = [datetime.strptime(date, "%Y-%m") for date in dates]
                except ValueError:
                    datetime_dates = range(len(dates))
            
            # Create line chart
            plt.plot(datetime_dates, values, marker='o', linewidth=2, markersize=8, color='#4ECDC4')
            
            # Fill area under the curve
            plt.fill_between(datetime_dates, values, alpha=0.3, color='#4ECDC4')
            
            plt.title(title, fontsize=16, fontweight='bold', pad=20)
            plt.xlabel('Date', fontsize=12)
            plt.ylabel('Amount ($)', fontsize=12)
            plt.grid(True, alpha=0.3)
            
            # Format y-axis to show currency
            plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
            
            # Rotate x-axis labels for better readability
            plt.xticks(rotation=45)
            
            plt.tight_layout()
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"Line chart saved as {filename}")
            plt.close()
            
        except Exception as e:
            print(f"Error creating line chart: {e}")
    
    def create_bar_chart(self, data: Dict[str, float], title: str, filename: str) -> None