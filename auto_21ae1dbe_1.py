```python
"""
Data Quality Visualization Module

This module provides comprehensive visualization capabilities for data quality analysis.
It generates various charts and graphs to help identify data quality issues including:
- Missing value heatmaps
- Duplicate distribution plots
- Outlier box plots
- Data type summary charts

The module is designed to work with pandas DataFrames and uses matplotlib and seaborn
for creating publication-ready visualizations that complement data quality analysis.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, Dict, Any, List, Tuple
import warnings
warnings.filterwarnings('ignore')

class DataQualityVisualizer:
    """
    A comprehensive visualization toolkit for data quality analysis.
    
    This class provides methods to generate various charts and graphs that help
    identify and visualize data quality issues in datasets.
    """
    
    def __init__(self, figsize: Tuple[int, int] = (12, 8), style: str = 'whitegrid'):
        """
        Initialize the DataQualityVisualizer.
        
        Args:
            figsize: Default figure size for plots
            style: Seaborn style to use for plots
        """
        self.figsize = figsize
        plt.style.use('default')
        sns.set_style(style)
        
    def create_missing_value_heatmap(self, df: pd.DataFrame, title: Optional[str] = None) -> None:
        """
        Create a heatmap showing missing values across the dataset.
        
        Args:
            df: Input DataFrame
            title: Optional title for the plot
        """
        try:
            if df.empty:
                print("Warning: DataFrame is empty, cannot create missing value heatmap")
                return
                
            # Calculate missing values
            missing_data = df.isnull()
            
            if not missing_data.any().any():
                print("No missing values found in the dataset")
                return
                
            plt.figure(figsize=self.figsize)
            
            # Create heatmap
            sns.heatmap(missing_data, 
                       yticklabels=False, 
                       cbar=True, 
                       cmap='viridis',
                       cbar_kws={'label': 'Missing Values'})
            
            plt.title(title or 'Missing Values Heatmap')
            plt.xlabel('Columns')
            plt.ylabel('Rows')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.show()
            
            # Print summary statistics
            missing_counts = df.isnull().sum()
            missing_percentages = (missing_counts / len(df)) * 100
            
            print("\nMissing Value Summary:")
            print("-" * 40)
            for col in missing_counts[missing_counts > 0].index:
                count = missing_counts[col]
                percentage = missing_percentages[col]
                print(f"{col}: {count} ({percentage:.2f}%)")
                
        except Exception as e:
            print(f"Error creating missing value heatmap: {str(e)}")
    
    def create_duplicate_distribution_plot(self, df: pd.DataFrame, title: Optional[str] = None) -> None:
        """
        Create plots showing duplicate record distribution.
        
        Args:
            df: Input DataFrame
            title: Optional title for the plot
        """
        try:
            if df.empty:
                print("Warning: DataFrame is empty, cannot create duplicate distribution plot")
                return
                
            # Find duplicates
            duplicated_mask = df.duplicated(keep=False)
            duplicate_count = duplicated_mask.sum()
            unique_count = len(df) - duplicate_count
            
            if duplicate_count == 0:
                print("No duplicate records found in the dataset")
                return
                
            # Create subplots
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Pie chart showing overall distribution
            labels = ['Unique Records', 'Duplicate Records']
            sizes = [unique_count, duplicate_count]
            colors = ['lightblue', 'lightcoral']
            
            ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax1.set_title('Overall Record Distribution')
            
            # Bar chart showing duplicate frequency by occurrence
            duplicate_counts = df[duplicated_mask].groupby(df.columns.tolist()).size()
            duplicate_freq = duplicate_counts.value_counts().sort_index()
            
            ax2.bar(duplicate_freq.index, duplicate_freq.values, color='lightcoral')
            ax2.set_xlabel('Number of Occurrences')
            ax2.set_ylabel('Number of Duplicate Groups')
            ax2.set_title('Duplicate Frequency Distribution')
            
            plt.suptitle(title or 'Duplicate Records Analysis')
            plt.tight_layout()
            plt.show()
            
            # Print summary
            print(f"\nDuplicate Records Summary:")
            print("-" * 40)
            print(f"Total records: {len(df)}")
            print(f"Unique records: {unique_count}")
            print(f"Duplicate records: {duplicate_count}")
            print(f"Duplicate percentage: {(duplicate_count/len(df))*100:.2f}%")
            
        except Exception as e:
            print(f"Error creating duplicate distribution plot: {str(e)}")
    
    def create_outlier_box_plots(self, df: pd.DataFrame, title: Optional[str] = None, max_cols: int = 10) -> None:
        """
        Create box plots to visualize outliers in numerical columns.
        
        Args:
            df: Input DataFrame
            title: Optional title for the plot
            max_cols: Maximum number of columns to plot
        """
        try:
            if df.empty:
                print("Warning: DataFrame is empty, cannot create outlier box plots")
                return
                
            # Get numerical columns
            numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if not numerical_cols:
                print("No numerical columns found for outlier analysis")
                return
                
            # Limit number of columns to plot
            if len(numerical_cols) > max_cols:
                print(f"Too many numerical columns ({len(numerical_cols)}). Showing first {max_cols}.")
                numerical_cols = numerical_cols[:max_cols]
            
            # Calculate number of rows and columns for subplots
            n_cols = min(3, len(numerical_cols))
            n_rows = (len(numerical_cols) + n_cols - 1) // n_cols
            
            fig, axes = plt.subplots(n_rows, n_cols, figsize=(5*n_cols, 4*n_rows))
            
            # Handle case where we have only one subplot
            if len(numerical_cols) == 1:
                axes = [axes]
            elif n_rows == 1:
                axes = axes if isinstance(axes, (list, np.ndarray)) else [axes]
            else:
                axes = axes.flatten()
            
            # Create box plots
            for i, col in enumerate(numerical_cols):
                try:
                    # Calculate outliers using IQR method
                    Q1 = df[col].quantile(0.25)
                    Q3 = df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    
                    outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)][col]
                    outlier_count = len(outliers)
                    
                    # Create box plot
                    axes[i].boxplot(df[col].dropna(), patch_artist=True,
                                  boxprops=dict(facecolor='lightblue', alpha=0.7))
                    axes[i].set_title