"""
Website Performance Monitor

This script measures website response times and collects detailed performance metrics
including DNS lookup time, connection time, and time to first byte. Results are
stored in CSV format with timestamps for analysis and monitoring purposes.

Usage: python script.py

The script will test a predefined list of websites and save results to 'performance_metrics.csv'
"""

import requests
import time
import csv
import socket
from datetime import datetime
from urllib.parse import urlparse


def measure_dns_lookup(hostname):
    """Measure DNS lookup time for a given hostname."""
    try:
        start_time = time.time()
        socket.gethostbyname(hostname)
        return (time.time() - start_time) * 1000  # Convert to milliseconds
    except socket.gaierror:
        return None


def measure_website_performance(url, timeout=10):
    """
    Measure various performance metrics for a website.
    
    Args:
        url (str): The URL to test
        timeout (int): Request timeout in seconds
        
    Returns:
        dict: Performance metrics or None if request failed
    """
    try:
        # Parse URL to get hostname for DNS lookup
        parsed_url = urlparse(url)
        hostname = parsed_url.netloc
        
        # Measure DNS lookup time
        dns_time = measure_dns_lookup(hostname)
        
        # Measure HTTP request performance
        start_time = time.time()
        
        # Use Session for connection reuse measurement
        session = requests.Session()
        response = session.get(url, timeout=timeout, stream=True)
        
        # Calculate times
        total_time = (time.time() - start_time) * 1000  # ms
        
        # Get first byte by reading minimal content
        first_byte_start = time.time()
        next(response.iter_content(chunk_size=1))
        first_byte_time = (time.time() - first_byte_start) * 1000  # ms
        
        # Connection time estimation (total - first_byte for simplification)
        connection_time = total_time - first_byte_time if total_time > first_byte_time else 0
        
        return {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'status_code': response.status_code,
            'dns_lookup_ms': round(dns_time, 2) if dns_time else None,
            'connection_time_ms': round(connection_time, 2),
            'first_byte_ms': round(first_byte_time, 2),
            'total_time_ms': round(total_time, 2),
            'response_size_bytes': len(response.content) if response.status_code == 200 else 0,
            'success': response.status_code == 200
        }
        
    except requests.exceptions.RequestException as e:
        print(f"Request failed for {url}: {e}")
        return {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'status_code': None,
            'dns_lookup_ms': None,
            'connection_time_ms': None,
            'first_byte_ms': None,
            'total_time_ms': None,
            'response_size_bytes': 0,
            'success': False,
            'error': str(e)
        }
    except Exception as e:
        print(f"Unexpected error for {url}: {e}")
        return None


def save_to_csv(results, filename='performance_metrics.csv'):
    """Save performance results to CSV file."""
    if not results:
        print("No results to save.")
        return
    
    try:
        fieldnames = ['timestamp', 'url', 'status_code', 'dns_lookup_ms', 
                     'connection_time_ms', 'first_byte_ms', 'total_time_ms', 
                     'response_size_bytes', 'success', 'error']
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in results:
                if result:  # Skip None results
                    # Ensure all fields exist
                    row = {field: result.get(field, '') for field in fieldnames}
                    writer.writerow(row)
        
        print(f"\nResults saved to {filename}")
        
    except Exception as e:
        print(f"Error saving to CSV: {e}")


def main():
    """Main function to test website performance."""
    # List of websites to test
    test_urls = [
        'https://www.google.com',
        'https://www.github.com',
        'https://www.stackoverflow.com',
        'https://www.python.org',
        'https://httpbin.org/delay/1'  # Intentional delay for testing
    ]
    
    print("Website Performance Monitor")
    print("=" * 40)
    print(f"Testing {len(test_urls)} websites...")
    print()
    
    results = []
    
    for i, url in enumerate(test_urls, 1):
        print(f"[{i}/{len(test_urls)}] Testing: {url}")
        
        result = measure_website_performance(url)
        
        if result:
            results.append(result)
            
            # Print results to stdout
            if result['success']:
                print(f"  ✓ Status: {result['status_code']}")
                print(f"  ✓ DNS Lookup: {result['dns_lookup_ms']}ms")
                print(f"  ✓ Connection: {result['connection_time_ms']}ms")
                print(f"  ✓ First Byte: {result['first_byte_ms']}ms")
                print(f"  ✓ Total Time: {result['total_time_ms']}ms")
                print(f"  ✓ Response Size: {result['response_size_bytes']} bytes")
            else:
                print(f"  ✗ Failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"  ✗ Could not measure performance")
        
        print()
        
        # Small delay between requests to be respectful
        time.sleep(1)
    
    # Save results to CSV
    save_to_csv(results)
    
    # Print summary
    successful_tests = sum(1 for r in results if r and r.get('success', False))
    print(f"\nSummary:")
    print(f"Total tests: {len(test_urls)}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {len(test_urls) - successful_tests}")
    
    if successful_tests > 0:
        avg_total_time = sum(r['total_time_ms'] for r in results if r and r.get('success')) / successful_tests
        print(f"Average response time: {avg_total_time:.2f}ms")


if __name__ == "__main__":
    main()