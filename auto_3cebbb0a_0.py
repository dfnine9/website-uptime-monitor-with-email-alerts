```python
#!/usr/bin/env python3
"""
HackerNews Tech Digest Generator

This module fetches the latest tech articles from HackerNews API and generates
a summarized HTML digest file with key headlines and brief descriptions.

Features:
- Fetches top stories from HackerNews API
- Generates clean HTML digest with article summaries
- Self-contained with minimal dependencies
- Comprehensive error handling
- Outputs results to stdout

Usage:
    python script.py

Dependencies:
    - httpx (for HTTP requests)
    - Standard library modules (json, html, datetime, sys)
"""

import json
import html
import sys
from datetime import datetime
from typing import List, Dict, Optional
try:
    import httpx
except ImportError:
    print("Error: httpx not installed. Install with: pip install httpx")
    sys.exit(1)

class HackerNewsDigest:
    """Fetches and processes HackerNews articles into an HTML digest."""
    
    BASE_URL = "https://hacker-news.firebaseio.com/v0"
    TIMEOUT = 30
    MAX_STORIES = 20
    
    def __init__(self):
        self.client = httpx.Client(timeout=self.TIMEOUT)
    
    def fetch_top_story_ids(self) -> List[int]:
        """Fetch list of top story IDs from HackerNews API."""
        try:
            response = self.client.get(f"{self.BASE_URL}/topstories.json")
            response.raise_for_status()
            story_ids = response.json()
            return story_ids[:self.MAX_STORIES]
        except Exception as e:
            print(f"Error fetching top stories: {e}", file=sys.stderr)
            return []
    
    def fetch_story_details(self, story_id: int) -> Optional[Dict]:
        """Fetch detailed information for a specific story ID."""
        try:
            response = self.client.get(f"{self.BASE_URL}/item/{story_id}.json")
            response.raise_for_status()
            story_data = response.json()
            
            # Filter for stories with URLs (skip Ask HN, Show HN without links)
            if story_data and story_data.get('url') and story_data.get('title'):
                return {
                    'title': story_data['title'],
                    'url': story_data['url'],
                    'score': story_data.get('score', 0),
                    'by': story_data.get('by', 'Unknown'),
                    'time': story_data.get('time', 0),
                    'descendants': story_data.get('descendants', 0)
                }
        except Exception as e:
            print(f"Error fetching story {story_id}: {e}", file=sys.stderr)
        return None
    
    def generate_story_summary(self, story: Dict) -> str:
        """Generate a brief description for a story based on title and metadata."""
        title = story['title']
        domain = self.extract_domain(story['url'])
        score = story['score']
        comments = story['descendants']
        
        # Simple heuristic-based summary
        summary_parts = []
        
        if 'startup' in title.lower() or 'company' in title.lower():
            summary_parts.append("Business/Startup news")
        elif any(tech in title.lower() for tech in ['ai', 'ml', 'python', 'javascript', 'react', 'api']):
            summary_parts.append("Technology development")
        elif 'security' in title.lower() or 'hack' in title.lower():
            summary_parts.append("Security/Privacy topic")
        elif any(word in title.lower() for word in ['release', 'launch', 'announce']):
            summary_parts.append("Product announcement")
        else:
            summary_parts.append("Tech industry discussion")
        
        summary_parts.append(f"from {domain}")
        summary_parts.append(f"({score} points, {comments} comments)")
        
        return " ".join(summary_parts)
    
    def extract_domain(self, url: str) -> str:
        """Extract domain name from URL."""
        try:
            if url.startswith('http'):
                domain = url.split('/')[2]
                if domain.startswith('www.'):
                    domain = domain[4:]
                return domain
        except:
            pass
        return "Unknown"
    
    def generate_html_digest(self, stories: List[Dict]) -> str:
        """Generate HTML digest from story data."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HackerNews Tech Digest - {timestamp}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .story {{ margin-bottom: 25px; padding: 15px; border-left: 3px solid #ff6600; background: #f9f9f9; }}
        .story-title {{ font-size: 18px; font-weight: bold; margin-bottom: 8px; }}
        .story-title a {{ color: #333; text-decoration: none; }}
        .story-title a:hover {{ text-decoration: underline; }}
        .story-meta {{ color: #666; font-size: 14px; margin-bottom: 8px; }}
        .story-summary {{ color: #555; font-size: 14px; line-height: 1.4; }}
        .footer {{ text-align: center; margin-top: 30px; color: #999; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 HackerNews Tech Digest</h1>
        <p>Generated on {timestamp}</p>
    </div>
"""
        
        for story in stories:
            escaped_title = html.escape(story['title'])
            escaped_url = html.escape(story['url'])
            summary = html.escape(self.generate_story_summary(story))
            
            html_content += f"""
    <div class="story">
        <div class="story-title">
            <a href="{escaped_url}" target="_blank">{escaped_title}</a>
        </div>
        <div class="story-meta">
            By {html.escape(story['by'])} | Score: {story['score']} | Comments: {story['descendants']}
        </div>
        <div class="story-summary">
            {summary}
        </div>
    </div>
"""
        
        html_content += """
    <div class="footer">
        <p>Data sourced from HackerNews API | Generated automatically</p>
    </div>
</body>
</html>
"""
        return html_content
    
    def run(self) -> bool:
        """Main execution method."""
        try:
            print("🔍 Fetching HackerNews top stories...")
            story_ids = self.fetch_top_story_ids()
            
            if not story_ids:
                print("❌ Failed to fetch story IDs", file=sys.stderr)
                return False
            
            print(f"📄 Processing {len(story_ids)} stories...")
            stories = []
            
            for story_id in story_ids:
                story = self.fetch_story_details(story_id)
                if story:
                    stories.append(story)
                    if len(stories) >= 15:  # Limit to top 15 valid stories
                        break
            
            if not stories:
                print("❌ No valid stories found", file=sys.stderr)
                return False
            
            print(f"✅ Successfully processed {len(stories)} stories")
            print("🏗