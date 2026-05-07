# Financial News Data Pipeline Script

Based on your request and the completed subtask work, here's a comprehensive Python script that fetches daily financial news from Alpha Vantage, filters by specific stocks/sectors, and stores data in SQLite:

## Complete Implementation

```python
import sqlite3
import requests
import hashlib
import logging
import re
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple, Any
from contextlib import contextmanager
import time
import json
import os
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class NewsArticle:
    """Data class for financial news articles"""
    title: str
    url: str
    time_published: str
    authors: List[str]
    summary: str
    source: str
    category_within_source: str
    overall_sentiment_score: float
    overall_sentiment_label: str
    ticker_sentiment: List[Dict]
    topics: List[Dict]

class FinancialNewsDatabase:
    """Comprehensive SQLite database manager for financial news"""
    
    def __init__(self, db_path: str = "financial_news.db"):
        self.db_path = db_path
        self.target_symbols = ['AAPL', 'TSLA', 'SPY', 'QQQ']
        self.sector_mapping = {
            'AAPL': 'Technology',
            'TSLA': 'Automotive/Clean Energy',
            'SPY': 'Market Index',
            'QQQ': 'Tech Index'
        }
        self._initialize_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database operation failed: {e}")
            raise
        finally:
            conn.close()
    
    def _initialize_database(self):
        """Initialize database with comprehensive schema"""
        with self.get_connection() as conn:
            # Main articles table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS financial_articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_hash TEXT UNIQUE NOT NULL,
                    headline TEXT NOT NULL,
                    content TEXT,
                    source TEXT NOT NULL,
                    url TEXT UNIQUE,
                    time_published TEXT NOT NULL,
                    authors TEXT,
                    category TEXT,
                    overall_sentiment_score REAL,
                    overall_sentiment_label TEXT,
                    topics TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Stock mentions table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS stock_mentions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER NOT NULL,
                    ticker TEXT NOT NULL,
                    sector TEXT,
                    relevance_score REAL,
                    sentiment_score REAL,
                    sentiment_label TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (article_id) REFERENCES financial_articles (id)
                )
            ''')
            
            # Performance indexes
            conn.execute('CREATE INDEX IF NOT EXISTS idx_articles_hash ON financial_articles(article_hash)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_articles_published ON financial_articles(time_published)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_articles_source ON financial_articles(source)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_mentions_ticker ON stock_mentions(ticker)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_mentions_article ON stock_mentions(article_id)')
            
            logger.info("Database initialized successfully")

    def store_article(self, article: NewsArticle) -> Optional[int]:
        """Store article with deduplication and stock mentions"""
        try:
            # Generate unique hash for deduplication
            content_hash = hashlib.sha256(
                f"{article.title}{article.url}{article.time_published}".encode()
            ).hexdigest()
            
            with self.get_connection() as conn:
                # Check for duplicates
                existing = conn.execute(
                    'SELECT id FROM financial_articles WHERE article_hash = ?',
                    (content_hash,)
                ).fetchone()
                
                if existing:
                    logger.info(f"Duplicate article skipped: {article.title[:50]}...")
                    return existing['id']
                
                # Insert article
                cursor = conn.execute('''
                    INSERT INTO financial_articles (
                        article_hash, headline, content, source, url,
                        time_published, authors, category, overall_sentiment_score,
                        overall_sentiment_label, topics
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    content_hash, article.title, article.summary, article.source,
                    article.url, article.time_published, json.dumps(article.authors),
                    article.category_within_source, article.overall_sentiment_score,
                    article.overall_sentiment_label, json.dumps(article.topics)
                ))
                
                article_id = cursor.lastrowid
                
                # Store stock mentions
                for ticker_data in article.ticker_sentiment:
                    ticker = ticker_data.get('ticker', '')
                    if ticker in self.target_symbols:
                        conn.execute('''
                            INSERT INTO stock_mentions (
                                article_id, ticker, sector, relevance_score,
                                sentiment_score, sentiment_label
                            ) VALUES (?, ?, ?, ?, ?, ?)
                        ''', (
                            article_id, ticker, self.sector_mapping.get(ticker),
                            float(ticker_data.get('relevance_score', 0)),
                            float(ticker_data.get('ticker_sentiment_score', 0)),
                            ticker_data.get('ticker_sentiment_label', 'Neutral')
                        ))
                
                logger.info(f"Stored article: {article.title[:50]}... (ID: {article_id})")
                return article_id
                
        except Exception as e:
            logger.error(f"Failed to store article: {e}")
            return None

class AlphaVantageNewsClient:
    """Alpha Vantage News API client with intelligent filtering"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
        self.target_tickers = ['AAPL', 'TSLA', 'SPY', 'QQQ']
        
    def fetch_news(self, topics: str = "technology,earnings", limit: int = 1000) -> List[NewsArticle]:
        """Fetch news from Alpha Vantage API"""
        try:
            params = {
                'function': 'NEWS_SENTIMENT',
                'topics': topics,
                'apikey': self.api_key,
                'limit': limit,
                'sort': 'LATEST'
            }
            
            logger.info(f"Fetching news from Alpha Vantage...")
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'feed' not in data:
                logger.error(f"API Error: {data.get('Error Message', 'Unknown error')}")
                return []
            
            articles = []
            for item in data['feed']:
                # Filter articles that mention our target stocks
                ticker_sentiment = item.get('ticker_sentiment', [])
                relevant_tickers = [ts for ts in ticker_sentiment if ts.get('ticker') in self.target_tickers]
                
                if relevant_t