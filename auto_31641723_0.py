```python
"""
Job Data Web Scraper and Database Manager

This module provides a comprehensive solution for extracting job data from web sources
and storing it in a structured SQLite database. It includes rate limiting, error handling,
and data validation to ensure reliable job data collection.

Features:
- Web scraping with rate limiting and retry logic
- SQLite database creation and management
- Data validation and cleaning
- Comprehensive error handling
- Command-line interface for easy execution

Usage:
    python script.py

Dependencies:
    - httpx: HTTP client library
    - sqlite3: Built-in database interface
    - json, time, urllib: Standard library modules
"""

import json
import sqlite3
import time
import urllib.parse
from typing import Dict, List, Optional, Tuple
import httpx


class JobScraper:
    """Web scraper for job data with rate limiting and error handling."""
    
    def __init__(self, delay: float = 1.0):
        self.delay = delay
        self.session = httpx.Client(
            timeout=30.0,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
    
    def scrape_jobs(self, query: str, location: str = "", max_results: int = 50) -> List[Dict]:
        """
        Scrape job data from web sources.
        
        Args:
            query: Job search query
            location: Location filter
            max_results: Maximum number of results to return
            
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        # Simulate job data extraction (replace with actual API calls)
        sample_jobs = self._generate_sample_jobs(query, location, max_results)
        
        for job_data in sample_jobs:
            try:
                processed_job = self._process_job_data(job_data)
                if processed_job:
                    jobs.append(processed_job)
                    print(f"Scraped job: {processed_job['title']} at {processed_job['company']}")
                
                time.sleep(self.delay)  # Rate limiting
                
            except Exception as e:
                print(f"Error processing job data: {e}")
                continue
        
        return jobs
    
    def _generate_sample_jobs(self, query: str, location: str, count: int) -> List[Dict]:
        """Generate sample job data for demonstration."""
        companies = ["TechCorp", "InnovateLab", "DataSystems", "CloudTech", "AI Solutions"]
        titles = ["Software Engineer", "Data Scientist", "DevOps Engineer", "Product Manager", "ML Engineer"]
        
        jobs = []
        for i in range(min(count, 25)):  # Limit to 25 for demo
            job = {
                "id": f"job_{i+1}",
                "title": f"{titles[i % len(titles)]}",
                "company": f"{companies[i % len(companies)]}",
                "location": location or "Remote",
                "salary_min": 60000 + (i * 5000),
                "salary_max": 80000 + (i * 7000),
                "description": f"We are seeking a talented {titles[i % len(titles)]} to join our team. Exciting opportunity to work with {query} technologies.",
                "posted_date": f"2024-01-{(i % 28) + 1:02d}",
                "url": f"https://example.com/jobs/{i+1}",
                "remote": i % 3 == 0,
                "experience_level": ["Entry", "Mid", "Senior"][i % 3]
            }
            jobs.append(job)
        
        return jobs
    
    def _process_job_data(self, raw_data: Dict) -> Optional[Dict]:
        """Process and validate job data."""
        try:
            processed = {
                'job_id': str(raw_data.get('id', '')),
                'title': str(raw_data.get('title', '')).strip(),
                'company': str(raw_data.get('company', '')).strip(),
                'location': str(raw_data.get('location', '')).strip(),
                'salary_min': self._parse_salary(raw_data.get('salary_min')),
                'salary_max': self._parse_salary(raw_data.get('salary_max')),
                'description': str(raw_data.get('description', '')).strip()[:1000],  # Limit description length
                'posted_date': str(raw_data.get('posted_date', '')),
                'url': str(raw_data.get('url', '')),
                'remote': bool(raw_data.get('remote', False)),
                'experience_level': str(raw_data.get('experience_level', 'Not specified'))
            }
            
            # Validate required fields
            if not all([processed['job_id'], processed['title'], processed['company']]):
                return None
                
            return processed
            
        except Exception as e:
            print(f"Error processing job data: {e}")
            return None
    
    def _parse_salary(self, salary_value) -> Optional[int]:
        """Parse salary value to integer."""
        if salary_value is None:
            return None
        try:
            return int(float(salary_value))
        except (ValueError, TypeError):
            return None
    
    def close(self):
        """Close the HTTP session."""
        self.session.close()


class JobDatabase:
    """SQLite database manager for job data."""
    
    def __init__(self, db_path: str = "jobs.db"):
        self.db_path = db_path
        self.conn = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """Connect to SQLite database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            print(f"Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            raise
    
    def _create_tables(self):
        """Create database tables if they don't exist."""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    company TEXT NOT NULL,
                    location TEXT,
                    salary_min INTEGER,
                    salary_max INTEGER,
                    description TEXT,
                    posted_date TEXT,
                    url TEXT,
                    remote BOOLEAN,
                    experience_level TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_job_id ON jobs(job_id);
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_company ON jobs(company);
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_location ON jobs(location);
            ''')
            
            self.conn.commit()
            print("Database tables created/verified")
            
        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")
            raise
    
    def insert_jobs(self, jobs: List[Dict]) -> int:
        """Insert jobs into database."""
        inserted_count = 0
        cursor = self.conn.cursor()
        
        for job in jobs:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO jobs (
                        job_id, title, company, location, salary_min, salary_max,
                        description, posted_date, url, remote, experience_level
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    job['job_id'], job['title'], job['company'], job['location'],
                    job['salary_