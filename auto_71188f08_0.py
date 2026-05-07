"""
Tech News Aggregator

This script fetches technology news from HackerNews API and TechCrunch RSS feeds,
filters articles by predefined keywords (AI, blockchain, startups, etc.), and
extracts title, summary, and URL for the top 10 most relevant stories.

The script is self-contained and requires only httpx for HTTP requests.
Results are printed to stdout in a readable format.

Usage: python script.py
"""

import json
import re
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
from urllib.parse import urljoin
import httpx


class TechNewsAggregator:
    def __init__(self):
        self.keywords = [
            'ai', 'artificial intelligence', 'machine learning', 'blockchain', 
            'cryptocurrency', 'startups', 'venture capital', 'tech', 'software',
            'programming', 'development', 'cloud computing', 'cybersecurity',
            'data science', 'automation', 'robotics', 'fintech', 'saas'
        ]
        self.client = httpx.Client(timeout=30.0)
    
    def fetch_hackernews_stories(self) -> List[Dict]:
        """Fetch top stories from HackerNews API"""
        stories = []
        try:
            # Get top story IDs
            response = self.client.get('https://hacker-news.firebaseio.com/v0/topstories.json')
            response.raise_for_status()
            story_ids = response.json()[:30]  # Get top 30 to have enough after filtering
            
            for story_id in story_ids:
                try:
                    story_response = self.client.get(
                        f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json'
                    )
                    story_response.raise_for_status()
                    story_data = story_response.json()
                    
                    if story_data and story_data.get('type') == 'story':
                        stories.append({
                            'title': story_data.get('title', ''),
                            'url': story_data.get('url', f"https://news.ycombinator.com/item?id={story_id}"),
                            'summary': story_data.get('text', '')[:200] if story_data.get('text') else '',
                            'source': 'HackerNews',
                            'score': story_data.get('score', 0)
                        })
                except Exception as e:
                    print(f"Error fetching HN story {story_id}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error fetching HackerNews stories: {e}")
            
        return stories
    
    def fetch_techcrunch_stories(self) -> List[Dict]:
        """Fetch stories from TechCrunch RSS feed"""
        stories = []
        try:
            response = self.client.get('https://techcrunch.com/feed/')
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            
            for item in root.findall('.//item')[:20]:  # Get top 20 items
                try:
                    title_elem = item.find('title')
                    link_elem = item.find('link')
                    description_elem = item.find('description')
                    
                    title = title_elem.text if title_elem is not None else ''
                    url = link_elem.text if link_elem is not None else ''
                    description = description_elem.text if description_elem is not None else ''
                    
                    # Clean HTML from description
                    summary = re.sub(r'<[^>]+>', '', description)[:200] if description else ''
                    
                    stories.append({
                        'title': title,
                        'url': url,
                        'summary': summary,
                        'source': 'TechCrunch',
                        'score': 0  # RSS doesn't have scores
                    })
                except Exception as e:
                    print(f"Error parsing TechCrunch item: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error fetching TechCrunch stories: {e}")
            
        return stories
    
    def filter_by_keywords(self, stories: List[Dict]) -> List[Dict]:
        """Filter stories by predefined keywords"""
        filtered_stories = []
        
        for story in stories:
            text_to_check = (story['title'] + ' ' + story['summary']).lower()
            
            # Check if any keyword appears in title or summary
            for keyword in self.keywords:
                if keyword in text_to_check:
                    story['matched_keyword'] = keyword
                    filtered_stories.append(story)
                    break
                    
        return filtered_stories
    
    def rank_stories(self, stories: List[Dict]) -> List[Dict]:
        """Rank stories by relevance and score"""
        # Simple ranking: HN score + keyword match bonus
        for story in stories:
            base_score = story.get('score', 0)
            keyword_bonus = 10 if any(kw in story['title'].lower() for kw in self.keywords) else 0
            story['rank_score'] = base_score + keyword_bonus
            
        return sorted(stories, key=lambda x: x['rank_score'], reverse=True)
    
    def run(self):
        """Main execution function"""
        print("Fetching tech news...")
        print("=" * 60)
        
        all_stories = []
        
        # Fetch from both sources
        hn_stories = self.fetch_hackernews_stories()
        tc_stories = self.fetch_techcrunch_stories()
        
        all_stories.extend(hn_stories)
        all_stories.extend(tc_stories)
        
        print(f"Fetched {len(all_stories)} total stories")
        
        # Filter by keywords
        filtered_stories = self.filter_by_keywords(all_stories)
        print(f"Found {len(filtered_stories)} stories matching keywords")
        
        # Rank and get top 10
        ranked_stories = self.rank_stories(filtered_stories)
        top_stories = ranked_stories[:10]
        
        print(f"\nTop 10 Tech Stories:")
        print("=" * 60)
        
        for i, story in enumerate(top_stories, 1):
            print(f"\n{i}. {story['title']}")
            print(f"   Source: {story['source']}")
            print(f"   URL: {story['url']}")
            if story['summary']:
                print(f"   Summary: {story['summary'][:150]}...")
            if story.get('matched_keyword'):
                print(f"   Matched keyword: {story['matched_keyword']}")
            print("-" * 40)
    
    def __del__(self):
        """Clean up HTTP client"""
        try:
            self.client.close()
        except:
            pass


def main():
    """Main entry point"""
    try:
        aggregator = TechNewsAggregator()
        aggregator.run()
    except KeyboardInterrupt:
        print("\nScript interrupted by user")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()