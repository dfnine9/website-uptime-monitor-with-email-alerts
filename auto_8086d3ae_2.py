```python
#!/usr/bin/env python3
"""
Digest Generator Script

This script creates an automated newsletter digest by:
1. Fetching articles from RSS feeds or web sources
2. Generating AI summaries using Anthropic's Claude API
3. Formatting content into a styled HTML email template
4. Outputting the complete newsletter to stdout

Dependencies: httpx (HTTP client), anthropic (AI API)
Usage: python script.py
"""

import json
import re
import sys
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse
import xml.etree.ElementTree as ET

try:
    import httpx
    import anthropic
except ImportError as e:
    print(f"Missing required dependency: {e}", file=sys.stderr)
    print("Install with: pip install httpx anthropic", file=sys.stderr)
    sys.exit(1)


class DigestGenerator:
    def __init__(self, anthropic_api_key: Optional[str] = None):
        """Initialize the digest generator with API credentials."""
        self.client = httpx.Client(timeout=30.0)
        self.anthropic_client = None
        
        if anthropic_api_key:
            self.anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)
    
    def fetch_rss_feed(self, url: str) -> List[Dict]:
        """Fetch and parse RSS feed, returning list of articles."""
        try:
            response = self.client.get(url)
            response.raise_for_status()
            
            root = ET.fromstring(response.text)
            articles = []
            
            # Handle RSS 2.0
            for item in root.findall('.//item'):
                title = item.find('title')
                link = item.find('link')
                description = item.find('description')
                pub_date = item.find('pubDate')
                
                if title is not None and link is not None:
                    articles.append({
                        'title': title.text,
                        'url': link.text,
                        'description': description.text if description is not None else '',
                        'pub_date': pub_date.text if pub_date is not None else ''
                    })
            
            # Handle Atom feeds
            if not articles:
                for entry in root.findall('.//{http://www.w3.org/2005/Atom}entry'):
                    title = entry.find('{http://www.w3.org/2005/Atom}title')
                    link = entry.find('{http://www.w3.org/2005/Atom}link')
                    summary = entry.find('{http://www.w3.org/2005/Atom}summary')
                    updated = entry.find('{http://www.w3.org/2005/Atom}updated')
                    
                    if title is not None and link is not None:
                        articles.append({
                            'title': title.text,
                            'url': link.get('href', ''),
                            'description': summary.text if summary is not None else '',
                            'pub_date': updated.text if updated is not None else ''
                        })
            
            return articles[:10]  # Limit to 10 articles
            
        except Exception as e:
            print(f"Error fetching RSS feed {url}: {e}", file=sys.stderr)
            return []
    
    def fetch_article_content(self, url: str) -> str:
        """Fetch full article content from URL."""
        try:
            response = self.client.get(url)
            response.raise_for_status()
            
            # Basic HTML content extraction
            content = response.text
            # Remove script and style tags
            content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
            content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)
            # Extract text between p tags (simple approach)
            paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', content, flags=re.DOTALL)
            
            # Clean HTML tags and join paragraphs
            clean_paragraphs = []
            for p in paragraphs:
                clean_p = re.sub(r'<[^>]+>', '', p).strip()
                if len(clean_p) > 50:  # Filter out short/empty paragraphs
                    clean_paragraphs.append(clean_p)
            
            return ' '.join(clean_paragraphs[:5])  # First 5 meaningful paragraphs
            
        except Exception as e:
            print(f"Error fetching article content from {url}: {e}", file=sys.stderr)
            return ""
    
    def generate_ai_summary(self, title: str, content: str) -> str:
        """Generate AI summary using Anthropic Claude."""
        if not self.anthropic_client:
            return content[:200] + "..." if len(content) > 200 else content
        
        try:
            prompt = f"""
            Please provide a concise 2-3 sentence summary of this article:
            
            Title: {title}
            Content: {content}
            
            Focus on the key points and main takeaways. Keep it under 150 words.
            """
            
            message = self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return message.content[0].text.strip()
            
        except Exception as e:
            print(f"Error generating AI summary: {e}", file=sys.stderr)
            # Fallback to truncated content
            return content[:200] + "..." if len(content) > 200 else content
    
    def create_html_template(self, articles: List[Dict], digest_title: str = "Daily Tech Digest") -> str:
        """Create styled HTML email template with articles."""
        current_date = datetime.now().strftime("%B %d, %Y")
        
        # Build article HTML
        article_html = ""
        for i, article in enumerate(articles, 1):
            article_html += f"""
            <div class="article">
                <h2 class="article-title">
                    <a href="{article['url']}" target="_blank">{article['title']}</a>
                </h2>
                <p class="article-summary">{article['summary']}</p>
                <div class="article-meta">
                    <span class="read-more">
                        <a href="{article['url']}" target="_blank">Read Full Article →</a>
                    </span>
                    {f"<span class='pub-date'>{article['pub_date']}</span>" if article['pub_date'] else ""}
                </div>
            </div>
            """
        
        html_template = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{digest_title}</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f8f9fa;
                }}
                
                .container {{
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    overflow: hidden;
                }}
                
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px 20px;
                    text-align: center;