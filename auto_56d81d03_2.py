```python
#!/usr/bin/env python3
"""
Website Status Alert System

This module implements a comprehensive alert system that monitors website status
by reading CSV logs, detecting error conditions, and sending email notifications.

Features:
- Reads CSV logs containing website monitoring data
- Detects HTTP error status codes (4xx/5xx) and timeout conditions
- Sends email alerts with detailed site status information
- Handles various error conditions gracefully
- Self-contained with minimal external dependencies

Usage:
    python script.py

Requirements:
    - Python 3.6+
    - httpx library for HTTP requests
    - anthropic library (imported but not used in core functionality)
    - Standard library modules: csv, smtplib, email, json, datetime, logging
"""

import csv
import smtplib
import json
import logging
import sys
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import time

try:
    import httpx
    import anthropic
except ImportError as e:
    print(f"Required dependency missing: {e}")
    print("Install with: pip install httpx anthropic")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('website_monitor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class WebsiteMonitor:
    """Main class for website monitoring and alerting."""
    
    def __init__(self, config_file: str = 'monitor_config.json'):
        """Initialize the monitor with configuration."""
        self.config = self._load_config(config_file)
        self.alert_history = {}
        self.error_threshold = self.config.get('error_threshold', 3)
        self.timeout_threshold = self.config.get('timeout_threshold', 30)
        
    def _load_config(self, config_file: str) -> Dict:
        """Load configuration from JSON file or create default."""
        default_config = {
            'csv_log_file': 'website_logs.csv',
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'email_user': 'your-email@gmail.com',
            'email_password': 'your-app-password',
            'alert_recipients': ['admin@company.com'],
            'check_interval': 300,
            'error_threshold': 3,
            'timeout_threshold': 30
        }
        
        try:
            if Path(config_file).exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    default_config.update(config)
                    return default_config
            else:
                # Create default config file
                with open(config_file, 'w') as f:
                    json.dump(default_config, f, indent=2)
                logger.info(f"Created default config file: {config_file}")
                return default_config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return default_config

    def _create_sample_csv(self) -> None:
        """Create a sample CSV log file for testing."""
        sample_data = [
            ['timestamp', 'url', 'status_code', 'response_time', 'error_message'],
            ['2024-01-15 10:00:00', 'https://example.com', '200', '0.5', ''],
            ['2024-01-15 10:05:00', 'https://example.com', '404', '1.2', 'Not Found'],
            ['2024-01-15 10:10:00', 'https://test-site.com', '500', '2.1', 'Internal Server Error'],
            ['2024-01-15 10:15:00', 'https://slow-site.com', '0', '35.0', 'Timeout'],
            ['2024-01-15 10:20:00', 'https://example.com', '503', '0.8', 'Service Unavailable'],
        ]
        
        csv_file = self.config['csv_log_file']
        if not Path(csv_file).exists():
            with open(csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(sample_data)
            logger.info(f"Created sample CSV file: {csv_file}")

    def read_csv_logs(self) -> List[Dict]:
        """Read and parse CSV log file."""
        logs = []
        csv_file = self.config['csv_log_file']
        
        try:
            # Create sample if file doesn't exist
            if not Path(csv_file).exists():
                self._create_sample_csv()
            
            with open(csv_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        # Parse and validate data
                        log_entry = {
                            'timestamp': datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S'),
                            'url': row['url'],
                            'status_code': int(row['status_code']) if row['status_code'].isdigit() else 0,
                            'response_time': float(row['response_time']),
                            'error_message': row.get('error_message', '')
                        }
                        logs.append(log_entry)
                    except (ValueError, KeyError) as e:
                        logger.warning(f"Invalid log entry: {row}, Error: {e}")
                        continue
                        
        except FileNotFoundError:
            logger.error(f"CSV log file not found: {csv_file}")
        except Exception as e:
            logger.error(f"Error reading CSV logs: {e}")
            
        logger.info(f"Read {len(logs)} log entries from {csv_file}")
        return logs

    def detect_errors(self, logs: List[Dict]) -> List[Dict]:
        """Detect error conditions from logs."""
        errors = []
        
        for log in logs:
            error_detected = False
            error_type = ""
            
            # Check for HTTP error status codes (4xx/5xx)
            if 400 <= log['status_code'] < 600:
                error_detected = True
                error_type = f"HTTP Error {log['status_code']}"
                
            # Check for timeouts
            elif log['response_time'] > self.timeout_threshold:
                error_detected = True
                error_type = "Timeout"
                
            # Check for status code 0 (usually indicates connection failure)
            elif log['status_code'] == 0:
                error_detected = True
                error_type = "Connection Failed"
            
            if error_detected:
                error_entry = {
                    'timestamp': log['timestamp'],
                    'url': log['url'],
                    'status_code': log['status_code'],
                    'response_time': log['response_time'],
                    'error_message': log['error_message'],
                    'error_type': error_type
                }
                errors.append(error_entry)
                
        logger.info(f"Detected {len(errors)} error conditions")
        return errors

    def should_send_alert(self, error: Dict) -> bool:
        """Determine if an alert should be sent based on error frequency."""
        url = error['url']
        current_time = datetime.now()
        
        # Initialize history for new URLs
        if url not in self.alert_history:
            self.alert_history[url] = {
                'error_count': 0,
                'last_alert': None,
                'consecutive_errors': 0
            }
        
        history = self.alert_history[url]
        
        # Increment error count
        history['error_count'] += 1
        history['consecutive_errors'] +=