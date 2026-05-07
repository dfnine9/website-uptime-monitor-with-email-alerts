```python
#!/usr/bin/env python3
"""
Job-Resume Matching Algorithm with ATS Optimization

This module implements a comprehensive job-resume matching system that:
1. Extracts and analyzes job requirements from job descriptions
2. Parses resume content to identify skills, experience, and qualifications
3. Compares job requirements against resume content using keyword matching
4. Generates tailored content suggestions to improve ATS (Applicant Tracking System) compatibility
5. Provides ATS keyword optimization recommendations

The algorithm uses natural language processing techniques including:
- Keyword extraction and frequency analysis
- Semantic similarity matching
- Skills gap identification
- ATS-friendly formatting suggestions

Usage: python script.py
"""

import re
import json
import sys
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict
import math


@dataclass
class JobRequirement:
    """Represents a parsed job requirement"""
    category: str
    keywords: List[str]
    priority: str
    description: str


@dataclass
class ResumeSection:
    """Represents a section of a resume"""
    section_type: str
    content: str
    keywords: List[str]


@dataclass
class MatchResult:
    """Represents the result of matching job requirements against resume"""
    match_score: float
    matched_keywords: List[str]
    missing_keywords: List[str]
    suggestions: List[str]
    ats_recommendations: List[str]


class JobRequirementExtractor:
    """Extracts and categorizes job requirements from job descriptions"""
    
    def __init__(self):
        self.skill_patterns = [
            r'\b(?:python|java|javascript|c\+\+|sql|html|css|react|angular|vue)\b',
            r'\b(?:machine learning|ai|artificial intelligence|deep learning|nlp)\b',
            r'\b(?:aws|azure|gcp|docker|kubernetes|jenkins|git)\b',
            r'\b(?:agile|scrum|waterfall|devops|ci/cd)\b'
        ]
        
        self.experience_patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)',
            r'(?:minimum|min|at least)\s*(\d+)\s*(?:years?|yrs?)',
            r'(\d+)-(\d+)\s*(?:years?|yrs?)\s*(?:experience|exp)'
        ]
        
        self.education_patterns = [
            r'\b(?:bachelor|bs|ba|master|ms|ma|phd|doctorate)\b',
            r'\b(?:computer science|engineering|mathematics|statistics)\b'
        ]
        
        self.priority_keywords = {
            'high': ['required', 'must have', 'essential', 'mandatory', 'critical'],
            'medium': ['preferred', 'desired', 'nice to have', 'plus', 'advantage'],
            'low': ['bonus', 'optional', 'additional']
        }

    def extract_requirements(self, job_description: str) -> List[JobRequirement]:
        """Extract structured requirements from job description"""
        requirements = []
        job_desc_lower = job_description.lower()
        
        try:
            # Extract technical skills
            tech_skills = self._extract_technical_skills(job_desc_lower)
            if tech_skills:
                requirements.append(JobRequirement(
                    category='technical_skills',
                    keywords=tech_skills,
                    priority='high',
                    description='Technical skills and programming languages'
                ))
            
            # Extract experience requirements
            experience = self._extract_experience_requirements(job_desc_lower)
            if experience:
                requirements.append(JobRequirement(
                    category='experience',
                    keywords=experience,
                    priority='high',
                    description='Years of experience and domain expertise'
                ))
            
            # Extract education requirements
            education = self._extract_education_requirements(job_desc_lower)
            if education:
                requirements.append(JobRequirement(
                    category='education',
                    keywords=education,
                    priority='medium',
                    description='Educational background and degrees'
                ))
            
            # Extract soft skills and methodologies
            soft_skills = self._extract_soft_skills(job_desc_lower)
            if soft_skills:
                requirements.append(JobRequirement(
                    category='soft_skills',
                    keywords=soft_skills,
                    priority='medium',
                    description='Soft skills and methodologies'
                ))
                
        except Exception as e:
            print(f"Error extracting requirements: {e}", file=sys.stderr)
            
        return requirements

    def _extract_technical_skills(self, text: str) -> List[str]:
        """Extract technical skills from job description"""
        skills = set()
        for pattern in self.skill_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            skills.update(matches)
        return list(skills)

    def _extract_experience_requirements(self, text: str) -> List[str]:
        """Extract experience requirements"""
        experience = []
        for pattern in self.experience_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    experience.extend(match)
                else:
                    experience.append(match)
        return [f"{exp} years experience" for exp in experience if exp.isdigit()]

    def _extract_education_requirements(self, text: str) -> List[str]:
        """Extract education requirements"""
        education = set()
        for pattern in self.education_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            education.update(matches)
        return list(education)

    def _extract_soft_skills(self, text: str) -> List[str]:
        """Extract soft skills and methodologies"""
        soft_skills_patterns = [
            r'\b(?:communication|leadership|teamwork|collaboration)\b',
            r'\b(?:problem solving|analytical|critical thinking)\b',
            r'\b(?:project management|time management|organization)\b'
        ]
        
        skills = set()
        for pattern in soft_skills_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            skills.update(matches)
        return list(skills)


class ResumeParser:
    """Parses resume content and extracts relevant information"""
    
    def __init__(self):
        self.section_headers = {
            'experience': ['experience', 'work history', 'employment', 'professional experience'],
            'education': ['education', 'academic background', 'qualifications'],
            'skills': ['skills', 'technical skills', 'competencies', 'expertise'],
            'projects': ['projects', 'portfolio', 'work samples'],
            'certifications': ['certifications', 'certificates', 'credentials']
        }

    def parse_resume(self, resume_text: str) -> List[ResumeSection]:
        """Parse resume into structured sections"""
        sections = []
        resume_lower = resume_text.lower()
        
        try:
            # Split resume into sections based on headers
            section_splits = self._identify_sections(resume_text)
            
            for section_type, content in section_splits.items():
                keywords = self._extract_keywords_from_section(content, section_type)
                sections.append(ResumeSection(
                    section_type=section_type,
                    content=content,
                    keywords=keywords
                ))
                
        except Exception as e:
            print(f"Error parsing resume: {e}", file=sys.stderr)
            
        return sections

    def _identify_sections(self, resume_text: str) -> Dict[str, str]:
        """Identify and extract different sections of the resume"""
        sections = {}
        lines = resume_text.split('\n')
        current_section = 'general'
        current_content = []
        
        for line in lines:
            line_lower = line.lower().strip()
            section_found = False
            
            for section_type