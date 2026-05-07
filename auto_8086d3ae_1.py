```python
#!/usr/bin/env python3
"""
Article Summarization Module

This module extracts full text content from URLs and generates concise summaries
using the OpenAI API. It handles web scraping, text extraction, and AI-powered
summarization in a self-contained script.

Dependencies: httpx, openai
Usage: python script.py
"""

import re
import json
import sys
from urllib.parse import urljoin, urlparse
try:
    import httpx
    from openai import OpenAI
except ImportError as e:
    print(f"Missing required dependency: {e}")
    print("Install with: pip install httpx openai")
    sys.exit(1)


class ArticleSummarizer:
    def __init__(self, api_key=None):
        """Initialize with OpenAI API key."""
        self.client = OpenAI(api_key=api_key) if api_key else None
        self.session = httpx.Client(
            headers={'User-Agent': 'Mozilla/5.0 (compatible; ArticleSummarizer)'},
            timeout=30.0
        )
    
    def extract_text_from_html(self, html_content):
        """Extract readable text from HTML content."""
        try:
            # Remove script and style elements
            html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
            html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
            
            # Extract title
            title_match = re.search(r'<title[^>]*>(.*?)</title>', html_content, re.IGNORECASE | re.DOTALL)
            title = title_match.group(1).strip() if title_match else ""
            
            # Extract main content (prioritize article, main, content divs)
            content_patterns = [
                r'<article[^>]*>(.*?)</article>',
                r'<main[^>]*>(.*?)</main>',
                r'<div[^>]*(?:class|id)="[^"]*(?:content|article|post)[^"]*"[^>]*>(.*?)</div>',
                r'<div[^>]*(?:class|id)="[^"]*(?:entry|body)[^"]*"[^>]*>(.*?)</div>'
            ]
            
            content = ""
            for pattern in content_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE | re.DOTALL)
                if matches:
                    content = ' '.join(matches)
                    break
            
            # Fallback: extract from body
            if not content:
                body_match = re.search(r'<body[^>]*>(.*?)</body>', html_content, re.IGNORECASE | re.DOTALL)
                content = body_match.group(1) if body_match else html_content
            
            # Remove HTML tags
            text = re.sub(r'<[^>]+>', ' ', content)
            # Clean whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            
            return {"title": title, "content": text}
            
        except Exception as e:
            raise Exception(f"Text extraction failed: {str(e)}")
    
    def fetch_url_content(self, url):
        """Fetch and extract text content from URL."""
        try:
            response = self.session.get(url, follow_redirects=True)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type:
                raise Exception(f"Unsupported content type: {content_type}")
            
            return self.extract_text_from_html(response.text)
            
        except httpx.HTTPError as e:
            raise Exception(f"HTTP error fetching {url}: {str(e)}")
        except Exception as e:
            raise Exception(f"Error processing {url}: {str(e)}")
    
    def generate_summary(self, title, content, max_length=200):
        """Generate AI summary of the content."""
        if not self.client:
            raise Exception("OpenAI client not initialized. Please provide API key.")
        
        try:
            # Truncate content if too long (GPT token limits)
            max_content_length = 8000
            if len(content) > max_content_length:
                content = content[:max_content_length] + "..."
            
            prompt = f"""Summarize the following article in {max_length} words or less. Focus on key points and main arguments.

Title: {title}

Content: {content}

Summary:"""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a skilled editor who creates concise, informative summaries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise Exception(f"Summary generation failed: {str(e)}")
    
    def summarize_url(self, url, max_length=200):
        """Complete pipeline: fetch URL, extract text, generate summary."""
        try:
            print(f"Fetching content from: {url}")
            extracted = self.fetch_url_content(url)
            
            print(f"Extracted {len(extracted['content'])} characters")
            print(f"Title: {extracted['title']}")
            
            if len(extracted['content']) < 100:
                raise Exception("Insufficient content extracted for summarization")
            
            print("Generating summary...")
            summary = self.generate_summary(extracted['title'], extracted['content'], max_length)
            
            return {
                "url": url,
                "title": extracted['title'],
                "summary": summary,
                "content_length": len(extracted['content'])
            }
            
        except Exception as e:
            raise Exception(f"Summarization pipeline failed: {str(e)}")
    
    def close(self):
        """Close HTTP session."""
        self.session.close()


def main():
    """Main execution function."""
    # Configuration
    test_urls = [
        "https://www.bbc.com/news",
        "https://techcrunch.com/2024/01/01/example-article/",
        "https://www.reuters.com/technology/"
    ]
    
    # Initialize (you would set your OpenAI API key here)
    api_key = None  # Replace with: os.getenv("OPENAI_API_KEY") or your key
    summarizer = ArticleSummarizer(api_key=api_key)
    
    print("Article Summarization Tool")
    print("=" * 50)
    
    # Interactive mode
    while True:
        try:
            url = input("\nEnter article URL (or 'quit' to exit): ").strip()
            
            if url.lower() in ['quit', 'exit', 'q']:
                break
            
            if not url:
                print("Please enter a valid URL.")
                continue
            
            # Basic URL validation
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                print("Invalid URL format. Please include http:// or https://")
                continue
            
            # Process URL
            result = summarizer.summarize_url(url, max_length=200)
            
            print("\n" + "="*60)
            print(f"SUMMARY RESULTS")
            print("="*60)
            print(f"URL: {result['url']}")
            print(f"Title: {result['title']}")
            print(f"Content Length: {result['content_length']} characters")
            print(f"\nSummary:\n{result['summary']}")
            print("="*60)
            
        except Key