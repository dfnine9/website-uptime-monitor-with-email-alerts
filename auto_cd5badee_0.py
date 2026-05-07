```python
"""
RSS Feed Parser and News Aggregator

This module fetches articles from multiple RSS news sources and extracts
structured data including titles, content, and timestamps. The parsed
data is output as JSON to stdout for easy consumption by other tools.

Features:
- Fetches from 8 major news sources
- Extracts title, description/content, publication date, and source URL
- Handles RSS feed parsing with built-in XML libraries
- Robust error handling for network and parsing failures
- Self-contained with minimal dependencies

Usage:
    python script.py

Output:
    JSON array of article objects with fields: title, content, timestamp, source, url
"""

import json
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime
from urllib.parse import urljoin
import httpx


class RSSParser:
    """RSS feed parser with error handling and data extraction."""
    
    def __init__(self):
        self.feeds = [
            {"name": "Reuters", "url": "http://feeds.reuters.com/reuters/topNews"},
            {"name": "BBC", "url": "http://feeds.bbci.co.uk/news/rss.xml"},
            {"name": "CNN", "url": "http://rss.cnn.com/rss/edition.rss"},
            {"name": "NPR", "url": "https://feeds.npr.org/1001/rss.xml"},
            {"name": "Associated Press", "url": "https://feeds.apnews.com/ApNews/apf-usnews"},
            {"name": "The Guardian", "url": "https://www.theguardian.com/world/rss"},
            {"name": "Washington Post", "url": "http://feeds.washingtonpost.com/rss/national"},
            {"name": "ABC News", "url": "https://abcnews.go.com/abcnews/topstories"}
        ]
        self.timeout = 10
        
    def fetch_feed(self, feed_url, source_name):
        """Fetch and parse a single RSS feed."""
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(feed_url)
                response.raise_for_status()
                
            # Parse XML
            root = ET.fromstring(response.text)
            articles = []
            
            # Handle different RSS formats
            items = root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry')
            
            for item in items:
                try:
                    article = self.parse_item(item, source_name)
                    if article:
                        articles.append(article)
                except Exception as e:
                    print(f"Error parsing item from {source_name}: {e}", file=sys.stderr)
                    continue
                    
            return articles
            
        except httpx.TimeoutException:
            print(f"Timeout fetching {source_name}: {feed_url}", file=sys.stderr)
        except httpx.HTTPStatusError as e:
            print(f"HTTP error {e.response.status_code} for {source_name}: {feed_url}", file=sys.stderr)
        except ET.ParseError as e:
            print(f"XML parse error for {source_name}: {e}", file=sys.stderr)
        except Exception as e:
            print(f"Unexpected error fetching {source_name}: {e}", file=sys.stderr)
            
        return []
    
    def parse_item(self, item, source_name):
        """Parse a single RSS item into structured data."""
        # Extract title
        title_elem = item.find('title') or item.find('.//{http://www.w3.org/2005/Atom}title')
        title = title_elem.text.strip() if title_elem is not None and title_elem.text else "No Title"
        
        # Extract content/description
        content_elem = (item.find('description') or 
                       item.find('content') or 
                       item.find('.//{http://www.w3.org/2005/Atom}summary') or
                       item.find('.//{http://www.w3.org/2005/Atom}content'))
        content = content_elem.text.strip() if content_elem is not None and content_elem.text else "No Content"
        
        # Clean HTML tags from content
        content = self.clean_html(content)
        
        # Extract link
        link_elem = item.find('link') or item.find('.//{http://www.w3.org/2005/Atom}link')
        if link_elem is not None:
            # Handle Atom format links
            if link_elem.get('href'):
                url = link_elem.get('href')
            else:
                url = link_elem.text.strip() if link_elem.text else ""
        else:
            url = ""
            
        # Extract publication date
        pubdate_elem = (item.find('pubDate') or 
                       item.find('.//{http://purl.org/dc/elements/1.1/}date') or
                       item.find('.//{http://www.w3.org/2005/Atom}published') or
                       item.find('.//{http://www.w3.org/2005/Atom}updated'))
        
        timestamp = self.parse_date(pubdate_elem.text if pubdate_elem is not None and pubdate_elem.text else "")
        
        return {
            "title": title,
            "content": content[:500] + "..." if len(content) > 500 else content,  # Truncate long content
            "timestamp": timestamp,
            "source": source_name,
            "url": url
        }
    
    def clean_html(self, text):
        """Remove basic HTML tags from text."""
        if not text:
            return ""
        # Simple HTML tag removal
        import re
        clean = re.sub(r'<[^>]+>', '', text)
        clean = clean.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
        return clean.strip()
    
    def parse_date(self, date_str):
        """Parse various date formats into ISO format."""
        if not date_str:
            return datetime.now().isoformat()
            
        try:
            # Try parsing RFC 2822 format (common in RSS)
            dt = parsedate_to_datetime(date_str.strip())
            return dt.isoformat()
        except (ValueError, TypeError):
            pass
            
        # Try ISO format
        for fmt in ['%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S']:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                return dt.isoformat()
            except ValueError:
                continue
                
        # Fallback to current time
        return datetime.now().isoformat()
    
    def fetch_all_feeds(self):
        """Fetch articles from all configured RSS feeds."""
        all_articles = []
        
        for feed in self.feeds:
            print(f"Fetching {feed['name']}...", file=sys.stderr)
            articles = self.fetch_feed(feed['url'], feed['name'])
            all_articles.extend(articles)
            print(f"Retrieved {len(articles)} articles from {feed['name']}", file=sys.stderr)
        
        return all_articles


def main():
    """Main execution function."""
    parser = RSSParser()
    
    try:
        articles = parser.fetch_all_feeds()
        
        # Sort by timestamp (newest first)
        articles.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Output JSON to stdout
        print(json.dumps(articles, indent=2, ensure_ascii=False))
        
        print(f"\nTotal articles retrieved: {len(articles)}", file=sys.stderr)
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e: