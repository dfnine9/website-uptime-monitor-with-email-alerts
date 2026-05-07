"""
RSS Feed Parser and JSON Converter

This module fetches RSS feeds from a predefined list of URLs and parses them into
a structured JSON format. It extracts article titles, links, descriptions, and
publication dates from each feed.

Dependencies: httpx (for HTTP requests)
Usage: python script.py

The script will fetch feeds, parse them, and output results as JSON to stdout.
"""

import json
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict, Any
import httpx


def parse_rss_feed(feed_content: str, feed_url: str) -> List[Dict[str, Any]]:
    """
    Parse RSS feed content and extract article information.
    
    Args:
        feed_content: Raw XML content of the RSS feed
        feed_url: URL of the feed for reference
    
    Returns:
        List of dictionaries containing article data
    """
    articles = []
    
    try:
        root = ET.fromstring(feed_content)
        
        # Handle RSS 2.0 format
        items = root.findall('.//item')
        if not items:
            # Handle Atom format
            items = root.findall('.//{http://www.w3.org/2005/Atom}entry')
        
        for item in items:
            article = {}
            
            # Extract title
            title_elem = item.find('title') or item.find('.//{http://www.w3.org/2005/Atom}title')
            article['title'] = title_elem.text.strip() if title_elem is not None else "No title"
            
            # Extract link
            link_elem = item.find('link') or item.find('.//{http://www.w3.org/2005/Atom}link')
            if link_elem is not None:
                # Handle Atom format where link is an attribute
                if link_elem.get('href'):
                    article['link'] = link_elem.get('href')
                else:
                    article['link'] = link_elem.text.strip() if link_elem.text else ""
            else:
                article['link'] = ""
            
            # Extract description
            desc_elem = (item.find('description') or 
                        item.find('summary') or 
                        item.find('.//{http://www.w3.org/2005/Atom}summary') or
                        item.find('.//{http://www.w3.org/2005/Atom}content'))
            article['description'] = desc_elem.text.strip() if desc_elem is not None else "No description"
            
            # Extract publication date
            date_elem = (item.find('pubDate') or 
                        item.find('published') or 
                        item.find('.//{http://www.w3.org/2005/Atom}published') or
                        item.find('.//{http://www.w3.org/2005/Atom}updated'))
            
            if date_elem is not None:
                article['publication_date'] = date_elem.text.strip()
            else:
                article['publication_date'] = datetime.now().isoformat()
            
            article['source_feed'] = feed_url
            articles.append(article)
            
    except ET.ParseError as e:
        print(f"XML parsing error for {feed_url}: {e}")
    except Exception as e:
        print(f"Unexpected error parsing {feed_url}: {e}")
    
    return articles


def fetch_rss_feeds(feed_urls: List[str]) -> Dict[str, Any]:
    """
    Fetch RSS feeds from multiple URLs and parse them.
    
    Args:
        feed_urls: List of RSS feed URLs to fetch
    
    Returns:
        Dictionary containing all parsed articles and metadata
    """
    all_articles = []
    failed_feeds = []
    successful_feeds = []
    
    with httpx.Client(timeout=30.0) as client:
        for url in feed_urls:
            try:
                response = client.get(url, follow_redirects=True)
                response.raise_for_status()
                
                articles = parse_rss_feed(response.text, url)
                all_articles.extend(articles)
                successful_feeds.append(url)
                
                print(f"Successfully fetched {len(articles)} articles from {url}")
                
            except httpx.RequestError as e:
                error_msg = f"Request error for {url}: {e}"
                print(error_msg)
                failed_feeds.append({"url": url, "error": str(e)})
                
            except httpx.HTTPStatusError as e:
                error_msg = f"HTTP error {e.response.status_code} for {url}"
                print(error_msg)
                failed_feeds.append({"url": url, "error": error_msg})
                
            except Exception as e:
                error_msg = f"Unexpected error for {url}: {e}"
                print(error_msg)
                failed_feeds.append({"url": url, "error": str(e)})
    
    return {
        "articles": all_articles,
        "metadata": {
            "total_articles": len(all_articles),
            "successful_feeds": len(successful_feeds),
            "failed_feeds": len(failed_feeds),
            "fetch_timestamp": datetime.now().isoformat(),
            "failed_feed_details": failed_feeds
        }
    }


def main():
    """Main function to execute the RSS feed parsing."""
    
    # Predefined list of RSS feed URLs
    rss_feeds = [
        "https://rss.cnn.com/rss/edition.rss",
        "https://feeds.bbci.co.uk/news/rss.xml",
        "https://www.reddit.com/r/technology/.rss",
        "https://techcrunch.com/feed/",
        "https://feeds.reuters.com/reuters/topNews",
        "https://www.wired.com/feed/rss",
        "https://feeds.arstechnica.com/arstechnica/index",
        "https://www.theguardian.com/international/rss"
    ]
    
    print("Starting RSS feed parsing...")
    print(f"Fetching from {len(rss_feeds)} feeds...")
    
    try:
        result = fetch_rss_feeds(rss_feeds)
        
        # Output results as JSON
        print("\n" + "="*50)
        print("RESULTS:")
        print("="*50)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    except Exception as e:
        error_result = {
            "error": f"Fatal error during execution: {e}",
            "articles": [],
            "metadata": {
                "total_articles": 0,
                "successful_feeds": 0,
                "failed_feeds": len(rss_feeds),
                "fetch_timestamp": datetime.now().isoformat()
            }
        }
        print(json.dumps(error_result, indent=2))


if __name__ == "__main__":
    main()