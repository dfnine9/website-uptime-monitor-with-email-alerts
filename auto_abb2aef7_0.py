```python
"""
Job Posting Scraper and Skills Extractor

This module scrapes job posting URLs and extracts key requirements, skills, and qualifications
using web scraping and basic natural language processing techniques. It identifies common
technical skills, soft skills, education requirements, and experience levels from job descriptions.

The script uses only standard libraries plus httpx for HTTP requests and basic text processing
for skill extraction without external NLP dependencies.

Usage:
    python script.py

The script will scrape predefined job posting URLs and extract:
- Technical skills (programming languages, frameworks, tools)
- Soft skills (communication, leadership, etc.)
- Education requirements
- Experience levels
- Key qualifications
"""

import re
import json
import asyncio
from urllib.parse import urljoin, urlparse
from collections import Counter
import httpx
from html.parser import HTMLParser


class JobTextExtractor(HTMLParser):
    """Custom HTML parser to extract text content from job postings"""
    
    def __init__(self):
        super().__init__()
        self.text_content = []
        self.current_tag = None
        
    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        
    def handle_data(self, data):
        if self.current_tag not in ['script', 'style', 'meta', 'link']:
            clean_text = data.strip()
            if clean_text:
                self.text_content.append(clean_text)
    
    def get_text(self):
        return ' '.join(self.text_content)


class SkillsExtractor:
    """Extract skills and qualifications from job posting text"""
    
    def __init__(self):
        # Technical skills patterns
        self.technical_skills = {
            'programming_languages': [
                'python', 'javascript', 'java', 'c++', 'c#', 'ruby', 'php', 'go', 'rust', 
                'swift', 'kotlin', 'typescript', 'scala', 'r', 'matlab', 'sql', 'html', 'css'
            ],
            'frameworks': [
                'react', 'angular', 'vue', 'django', 'flask', 'spring', 'express', 'rails',
                'laravel', 'symfony', 'asp.net', '.net', 'node.js', 'tensorflow', 'pytorch'
            ],
            'databases': [
                'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'oracle',
                'sqlite', 'cassandra', 'dynamodb', 'mariadb'
            ],
            'cloud_platforms': [
                'aws', 'azure', 'gcp', 'google cloud', 'kubernetes', 'docker', 'terraform',
                'ansible', 'jenkins', 'gitlab', 'github actions'
            ],
            'tools': [
                'git', 'jira', 'confluence', 'slack', 'figma', 'photoshop', 'illustrator',
                'sketch', 'tableau', 'power bi', 'excel', 'salesforce'
            ]
        }
        
        # Soft skills
        self.soft_skills = [
            'communication', 'leadership', 'teamwork', 'problem solving', 'analytical thinking',
            'creativity', 'adaptability', 'time management', 'project management', 'collaboration',
            'critical thinking', 'attention to detail', 'customer service', 'presentation skills'
        ]
        
        # Education patterns
        self.education_patterns = [
            r"bachelor['\s]*s?\s*(?:degree|of|in)",
            r"master['\s]*s?\s*(?:degree|of|in)",
            r"phd|doctorate|doctoral",
            r"associate['\s]*s?\s*degree",
            r"high school|diploma|ged"
        ]
        
        # Experience patterns
        self.experience_patterns = [
            r"(\d+)\+?\s*(?:to\s*\d+\s*)?years?\s*(?:of\s*)?experience",
            r"(\d+)\+?\s*(?:to\s*\d+\s*)?years?\s*in",
            r"minimum\s*(?:of\s*)?(\d+)\s*years?",
            r"at least\s*(\d+)\s*years?"
        ]
    
    def extract_technical_skills(self, text):
        """Extract technical skills from text"""
        text_lower = text.lower()
        found_skills = {}
        
        for category, skills in self.technical_skills.items():
            category_skills = []
            for skill in skills:
                if skill in text_lower:
                    category_skills.append(skill)
            if category_skills:
                found_skills[category] = category_skills
        
        return found_skills
    
    def extract_soft_skills(self, text):
        """Extract soft skills from text"""
        text_lower = text.lower()
        found_skills = []
        
        for skill in self.soft_skills:
            if skill in text_lower:
                found_skills.append(skill)
        
        return found_skills
    
    def extract_education(self, text):
        """Extract education requirements from text"""
        text_lower = text.lower()
        education_reqs = []
        
        for pattern in self.education_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            if matches:
                education_reqs.extend(matches)
        
        return education_reqs
    
    def extract_experience(self, text):
        """Extract experience requirements from text"""
        text_lower = text.lower()
        experience_reqs = []
        
        for pattern in self.experience_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            if matches:
                experience_reqs.extend(matches)
        
        return experience_reqs
    
    def extract_all(self, text):
        """Extract all skills and requirements from text"""
        return {
            'technical_skills': self.extract_technical_skills(text),
            'soft_skills': self.extract_soft_skills(text),
            'education_requirements': self.extract_education(text),
            'experience_requirements': self.extract_experience(text)
        }


class JobScraper:
    """Main job scraping class"""
    
    def __init__(self):
        self.extractor = SkillsExtractor()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    async def fetch_job_posting(self, url, client):
        """Fetch a single job posting"""
        try:
            response = await client.get(url, headers=self.headers, timeout=10.0)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
            return None
    
    def extract_text_from_html(self, html):
        """Extract clean text from HTML"""
        try:
            parser = JobTextExtractor()
            parser.feed(html)
            return parser.get_text()
        except Exception as e:
            print(f"Error parsing HTML: {str(e)}")
            return ""
    
    async def scrape_jobs(self, urls):
        """Scrape multiple job postings concurrently"""
        results = []
        
        async with httpx.AsyncClient() as client:
            tasks = [self.fetch_job_posting(url, client) for url in urls]
            html_contents = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, html in enumerate(html_contents):
                if html and not isinstance(html, Exception):
                    try:
                        text = self.extract_text_from_html(html)
                        if text:
                            skills = self.extractor.extract_all(text)
                            results.append({