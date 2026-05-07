```python
#!/usr/bin/env python3
"""
Web Health & SEO Monitoring Script

This script performs comprehensive website health checks and basic SEO analysis by:
- Pinging a list of URLs and measuring response times
- Checking HTTP status codes and response headers
- Extracting SEO metrics (title tags, meta descriptions)
- Compiling results into structured JSON output

Dependencies: httpx, json (standard library)
Usage: python script.py
"""

import json
import time
import re
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Optional

try:
    import httpx
except ImportError:
    print("Error: httpx library required. Install with: pip install httpx")
    exit(1)


class WebHealthChecker:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout, follow_redirects=True)
        
    def extract_seo_metrics(self, html_content: str) -> Dict[str, Optional[str]]:
        """Extract basic SEO metrics from HTML content."""
        metrics = {
            'title': None,
            'meta_description': None,
            'h1_tags': [],
            'meta_keywords': None
        }
        
        try:
            # Extract title tag
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', html_content, re.IGNORECASE)
            if title_match:
                metrics['title'] = title_match.group(1).strip()
            
            # Extract meta description
            meta_desc_match = re.search(
                r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']', 
                html_content, 
                re.IGNORECASE
            )
            if meta_desc_match:
                metrics['meta_description'] = meta_desc_match.group(1).strip()
            
            # Extract meta keywords
            meta_keywords_match = re.search(
                r'<meta[^>]+name=["\']keywords["\'][^>]+content=["\']([^"\']+)["\']', 
                html_content, 
                re.IGNORECASE
            )
            if meta_keywords_match:
                metrics['meta_keywords'] = meta_keywords_match.group(1).strip()
            
            # Extract H1 tags
            h1_matches = re.findall(r'<h1[^>]*>([^<]+)</h1>', html_content, re.IGNORECASE)
            metrics['h1_tags'] = [h1.strip() for h1 in h1_matches]
            
        except Exception as e:
            print(f"Warning: Error extracting SEO metrics: {e}")
            
        return metrics
    
    def check_url(self, url: str) -> Dict:
        """Check a single URL and return comprehensive metrics."""
        result = {
            'url': url,
            'timestamp': time.time(),
            'status_code': None,
            'response_time_ms': None,
            'success': False,
            'error': None,
            'headers': {},
            'seo_metrics': {},
            'content_length': None,
            'final_url': None
        }
        
        try:
            start_time = time.time()
            response = self.client.get(url)
            end_time = time.time()
            
            result.update({
                'status_code': response.status_code,
                'response_time_ms': round((end_time - start_time) * 1000, 2),
                'success': response.status_code < 400,
                'headers': dict(response.headers),
                'content_length': len(response.content),
                'final_url': str(response.url)
            })
            
            # Extract SEO metrics if successful and content is HTML
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '').lower()
                if 'text/html' in content_type:
                    result['seo_metrics'] = self.extract_seo_metrics(response.text)
                    
        except httpx.TimeoutException:
            result['error'] = 'Request timeout'
        except httpx.ConnectError:
            result['error'] = 'Connection failed'
        except Exception as e:
            result['error'] = str(e)
            
        return result
    
    def check_multiple_urls(self, urls: List[str]) -> List[Dict]:
        """Check multiple URLs and return results."""
        results = []
        
        for i, url in enumerate(urls, 1):
            print(f"Checking {i}/{len(urls)}: {url}")
            result = self.check_url(url)
            results.append(result)
            
            # Brief pause between requests to be respectful
            time.sleep(0.1)
            
        return results
    
    def __del__(self):
        """Cleanup client connection."""
        if hasattr(self, 'client'):
            self.client.close()


def main():
    # Default URLs to check
    urls_to_check = [
        'https://www.google.com',
        'https://www.github.com',
        'https://www.stackoverflow.com',
        'https://httpbin.org/delay/2',
        'https://httpstat.us/404',
        'https://www.python.org',
        'https://docs.python.org',
        'https://nonexistent-domain-12345.com'
    ]
    
    print("Web Health & SEO Monitor")
    print("=" * 40)
    print(f"Checking {len(urls_to_check)} URLs...")
    print()
    
    try:
        checker = WebHealthChecker(timeout=15)
        results = checker.check_multiple_urls(urls_to_check)
        
        # Summary statistics
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful
        avg_response_time = sum(r['response_time_ms'] or 0 for r in results if r['response_time_ms']) / len(results)
        
        print("\n" + "=" * 40)
        print("SUMMARY")
        print("=" * 40)
        print(f"Total URLs checked: {len(results)}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Average response time: {avg_response_time:.2f}ms")
        print()
        
        # Detailed results
        print("DETAILED RESULTS")
        print("=" * 40)
        
        for result in results:
            status = "✓" if result['success'] else "✗"
            url = result['url']
            status_code = result['status_code'] or 'N/A'
            response_time = f"{result['response_time_ms']}ms" if result['response_time_ms'] else 'N/A'
            error = result['error'] or ''
            
            print(f"{status} {url}")
            print(f"   Status: {status_code} | Time: {response_time}")
            
            if result['seo_metrics']:
                seo = result['seo_metrics']
                if seo.get('title'):
                    print(f"   Title: {seo['title'][:60]}{'...' if len(seo['title']) > 60 else ''}")
                if seo.get('meta_description'):
                    print(f"   Description: {seo['meta_description'][:60]}{'...' if len(seo['meta_description']) > 60 else ''}")
            
            if error:
                print(f"   Error: {error}")
            print()
        
        # JSON output for programmatic use
        print("=" * 40)
        print("JSON OUTPUT")
        print("=" * 40)
        print(json.dumps(results, indent=2))
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"Fatal error: {e}")


if __name__ == "__