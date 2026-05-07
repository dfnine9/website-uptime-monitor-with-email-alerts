```python
"""
Job Market Data Analysis Script

This script processes scraped job data from CSV files to analyze salary statistics,
identify trending skills, and generate market demand insights. It calculates:
- Salary statistics (median, average, ranges) by skill and location
- Trending skills based on frequency and salary premiums
- Market demand patterns and geographic insights

The script is designed to work with CSV data containing job postings with fields
for skills, location, and salary information.
"""

import csv
import statistics
import re
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Optional
import sys


def parse_salary(salary_str: str) -> Optional[float]:
    """Extract numeric salary value from various string formats."""
    if not salary_str or salary_str.lower() in ['', 'n/a', 'not specified']:
        return None
    
    # Remove common prefixes/suffixes and normalize
    salary_str = re.sub(r'[\$,]', '', salary_str)
    salary_str = re.sub(r'per year|annually|/year|yr', '', salary_str, flags=re.IGNORECASE)
    salary_str = re.sub(r'per hour|hourly|/hour|hr', '', salary_str, flags=re.IGNORECASE)
    
    # Extract numbers (handle ranges by taking average)
    numbers = re.findall(r'\d+(?:\.\d+)?', salary_str)
    if not numbers:
        return None
    
    # Convert to float and handle ranges
    nums = [float(n) for n in numbers]
    
    # If it's hourly (assuming 2080 work hours/year), convert to annual
    if any(word in salary_str.lower() for word in ['hour', 'hr']):
        nums = [n * 2080 for n in nums]
    
    # Handle ranges by taking average
    if len(nums) == 2:
        return sum(nums) / 2
    elif len(nums) == 1:
        return nums[0]
    else:
        return sum(nums) / len(nums)


def parse_skills(skills_str: str) -> List[str]:
    """Parse skills from comma-separated string."""
    if not skills_str:
        return []
    
    skills = [skill.strip().lower() for skill in skills_str.split(',')]
    return [skill for skill in skills if skill and len(skill) > 1]


def normalize_location(location_str: str) -> str:
    """Normalize location strings for consistent grouping."""
    if not location_str:
        return "Unknown"
    
    location = location_str.strip()
    # Extract city, state pattern
    if ',' in location:
        parts = location.split(',')
        if len(parts) >= 2:
            city = parts[0].strip()
            state = parts[1].strip()
            return f"{city}, {state[:2].upper()}"
    
    return location


def calculate_salary_stats(salaries: List[float]) -> Dict[str, float]:
    """Calculate salary statistics for a list of salaries."""
    if not salaries:
        return {}
    
    try:
        return {
            'count': len(salaries),
            'median': statistics.median(salaries),
            'average': statistics.mean(salaries),
            'min': min(salaries),
            'max': max(salaries),
            'std_dev': statistics.stdev(salaries) if len(salaries) > 1 else 0
        }
    except Exception as e:
        print(f"Error calculating salary stats: {e}")
        return {}


def analyze_job_data(csv_file: str) -> Dict:
    """Main function to analyze job data from CSV file."""
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            # Data structures for analysis
            skill_salaries = defaultdict(list)
            location_salaries = defaultdict(list)
            skill_counts = Counter()
            location_counts = Counter()
            all_salaries = []
            skill_location_matrix = defaultdict(lambda: defaultdict(list))
            
            row_count = 0
            processed_count = 0
            
            for row in reader:
                row_count += 1
                
                # Extract and parse data
                salary = parse_salary(row.get('salary', ''))
                skills = parse_skills(row.get('skills', ''))
                location = normalize_location(row.get('location', ''))
                
                if salary and salary > 10000:  # Filter out unrealistic salaries
                    all_salaries.append(salary)
                    processed_count += 1
                    
                    # Location analysis
                    location_salaries[location].append(salary)
                    location_counts[location] += 1
                    
                    # Skills analysis
                    for skill in skills:
                        skill_salaries[skill].append(salary)
                        skill_counts[skill] += 1
                        skill_location_matrix[skill][location].append(salary)
            
            print(f"Processed {processed_count} jobs out of {row_count} total rows")
            
            return {
                'skill_salaries': dict(skill_salaries),
                'location_salaries': dict(location_salaries),
                'skill_counts': dict(skill_counts),
                'location_counts': dict(location_counts),
                'all_salaries': all_salaries,
                'skill_location_matrix': dict(skill_location_matrix)
            }
            
    except FileNotFoundError:
        print(f"Error: CSV file '{csv_file}' not found.")
        return {}
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return {}


def identify_trending_skills(skill_data: Dict, min_jobs: int = 5) -> List[Tuple[str, Dict]]:
    """Identify trending skills based on frequency and salary premiums."""
    skill_salaries = skill_data.get('skill_salaries', {})
    skill_counts = skill_data.get('skill_counts', {})
    all_salaries = skill_data.get('all_salaries', [])
    
    if not all_salaries:
        return []
    
    overall_median = statistics.median(all_salaries)
    trending_skills = []
    
    for skill, salaries in skill_salaries.items():
        if len(salaries) >= min_jobs:
            stats = calculate_salary_stats(salaries)
            if stats:
                premium = (stats['median'] - overall_median) / overall_median * 100
                trending_skills.append((skill, {
                    'count': skill_counts.get(skill, 0),
                    'salary_stats': stats,
                    'salary_premium': premium
                }))
    
    # Sort by salary premium and job count
    trending_skills.sort(key=lambda x: (x[1]['salary_premium'], x[1]['count']), reverse=True)
    return trending_skills


def generate_market_insights(data: Dict) -> None:
    """Generate and print market demand insights."""
    print("\n" + "="*60)
    print("JOB MARKET ANALYSIS REPORT")
    print("="*60)
    
    all_salaries = data.get('all_salaries', [])
    if not all_salaries:
        print("No salary data available for analysis.")
        return
    
    # Overall market statistics
    overall_stats = calculate_salary_stats(all_salaries)
    print(f"\nOVERALL MARKET STATISTICS:")
    print(f"Total Jobs Analyzed: {overall_stats.get('count', 0):,}")
    print(f"Median Salary: ${overall_stats.get('median', 0):,.0f}")
    print(f"Average Salary: ${overall_stats.get('average', 0):,.0f}")
    print(f"Salary Range: ${overall_stats.get('min', 0):,.0f} - ${overall_stats.get('max', 0):,.0f}")
    
    # Top locations by salary
    location_salaries = data.get('location_salaries', {})