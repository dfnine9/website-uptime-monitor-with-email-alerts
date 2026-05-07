```python
"""
Resume Parser Module

This module provides functionality to parse resume content and identify key sections
including skills, experience, and education for targeted optimization. It uses
pattern matching and keyword recognition to extract and categorize resume sections.

The parser can handle various resume formats and provides structured output
for further optimization and analysis.

Usage:
    python script.py

Features:
    - Identifies Skills, Experience, and Education sections
    - Extracts key information from each section
    - Provides suggestions for optimization
    - Handles various resume formats and structures
"""

import re
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class ResumeSection:
    """Data class to represent a resume section"""
    title: str
    content: str
    keywords: List[str]
    optimization_suggestions: List[str]


@dataclass
class ParsedResume:
    """Data class to represent a fully parsed resume"""
    skills: Optional[ResumeSection]
    experience: Optional[ResumeSection]
    education: Optional[ResumeSection]
    other_sections: List[ResumeSection]
    raw_content: str


class ResumeParser:
    """Main resume parsing class"""
    
    def __init__(self):
        self.skill_keywords = [
            'python', 'java', 'javascript', 'react', 'node', 'sql', 'aws', 'docker',
            'kubernetes', 'git', 'agile', 'scrum', 'machine learning', 'ai',
            'data analysis', 'project management', 'leadership', 'communication'
        ]
        
        self.experience_indicators = [
            'experience', 'work history', 'employment', 'professional experience',
            'career history', 'work experience', 'professional background'
        ]
        
        self.education_indicators = [
            'education', 'academic background', 'qualifications', 'degrees',
            'certifications', 'academic history', 'learning'
        ]
        
        self.skills_indicators = [
            'skills', 'technical skills', 'core competencies', 'expertise',
            'technologies', 'proficiencies', 'capabilities', 'tools'
        ]
    
    def extract_sections(self, content: str) -> Dict[str, List[str]]:
        """Extract sections from resume content based on common patterns"""
        try:
            sections = {}
            lines = content.split('\n')
            current_section = None
            current_content = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check if line is a section header
                section_match = self._identify_section_header(line)
                if section_match:
                    # Save previous section
                    if current_section and current_content:
                        sections[current_section] = current_content
                    
                    current_section = section_match
                    current_content = []
                else:
                    if current_section:
                        current_content.append(line)
                    else:
                        # If no section identified yet, try to categorize the line
                        inferred_section = self._infer_section_from_content(line)
                        if inferred_section:
                            if inferred_section not in sections:
                                sections[inferred_section] = []
                            sections[inferred_section].append(line)
            
            # Save the last section
            if current_section and current_content:
                sections[current_section] = current_content
            
            return sections
            
        except Exception as e:
            print(f"Error extracting sections: {e}")
            return {}
    
    def _identify_section_header(self, line: str) -> Optional[str]:
        """Identify if a line is a section header"""
        line_lower = line.lower().strip()
        
        # Remove common formatting characters
        cleaned_line = re.sub(r'[^\w\s]', '', line_lower).strip()
        
        # Check for exact matches or close matches
        if any(indicator in cleaned_line for indicator in self.skills_indicators):
            return 'skills'
        elif any(indicator in cleaned_line for indicator in self.experience_indicators):
            return 'experience'
        elif any(indicator in cleaned_line for indicator in self.education_indicators):
            return 'education'
        
        # Check if line looks like a header (short, possibly all caps, etc.)
        if len(line.split()) <= 3 and (line.isupper() or line.istitle()):
            return 'other'
        
        return None
    
    def _infer_section_from_content(self, line: str) -> Optional[str]:
        """Infer section type from content when no clear header exists"""
        line_lower = line.lower()
        
        # Look for date patterns (likely experience or education)
        date_pattern = r'\b\d{4}\b|\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b'
        if re.search(date_pattern, line_lower):
            if any(word in line_lower for word in ['university', 'college', 'degree', 'bachelor', 'master', 'phd']):
                return 'education'
            elif any(word in line_lower for word in ['company', 'inc', 'corp', 'llc', 'manager', 'developer', 'analyst']):
                return 'experience'
        
        # Look for skill-like content
        skill_count = sum(1 for skill in self.skill_keywords if skill in line_lower)
        if skill_count >= 2:
            return 'skills'
        
        return None
    
    def extract_keywords(self, content: str, section_type: str) -> List[str]:
        """Extract relevant keywords from section content"""
        try:
            keywords = []
            content_lower = content.lower()
            
            if section_type == 'skills':
                keywords = [skill for skill in self.skill_keywords if skill in content_lower]
                
                # Also extract custom skills (words that appear to be technologies/tools)
                tech_pattern = r'\b[A-Z][a-zA-Z]*(?:\.[a-zA-Z]+)*\b|\.NET|\+\+'
                tech_matches = re.findall(tech_pattern, content)
                keywords.extend([match for match in tech_matches if len(match) > 2])
            
            elif section_type == 'experience':
                # Extract job titles, companies, action verbs
                action_verbs = ['managed', 'developed', 'created', 'implemented', 'designed', 
                               'led', 'improved', 'optimized', 'built', 'delivered']
                keywords = [verb for verb in action_verbs if verb in content_lower]
                
                # Extract numbers/metrics
                metrics = re.findall(r'\d+%|\$\d+|\d+\+', content)
                keywords.extend(metrics)
            
            elif section_type == 'education':
                # Extract degrees, institutions, fields of study
                degree_keywords = ['bachelor', 'master', 'phd', 'doctorate', 'certificate', 'diploma']
                keywords = [degree for degree in degree_keywords if degree in content_lower]
            
            return list(set(keywords))  # Remove duplicates
            
        except Exception as e:
            print(f"Error extracting keywords for {section_type}: {e}")
            return []
    
    def generate_optimization_suggestions(self, section: str, content: str, keywords: List[str]) -> List[str]:
        """Generate optimization suggestions for a section"""
        try:
            suggestions = []
            
            if section == 'skills':
                if len(keywords) < 5:
                    suggestions.append("Consider adding more technical skills relevant to your target role")
                if not any(skill in ['python', 'java', 'javascript'] for skill in keywords):
                    suggestions.append("Consider adding popular programming languages if applicable")
                suggestions.append("Group skills by category (e.g., Programming Languages, Frameworks, Tools)")
                
            elif section == 'experience':
                if not re.search(r'\d+', content):