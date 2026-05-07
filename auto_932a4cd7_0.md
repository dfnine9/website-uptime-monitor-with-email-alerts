# Alpha Vantage Stock Fundamentals Analysis System

## Overview
Complete implementation for connecting to Alpha Vantage API, fetching stock fundamentals, and creating intelligent filtering scripts for value investing analysis.

## 1. Environment Setup & API Configuration

### Installation Requirements
```bash
pip install alpha-vantage pandas python-dotenv requests numpy matplotlib seaborn
```

### Environment Configuration
```python
# .env file
ALPHA_VANTAGE_API_KEY=your_api_key_here
DATABASE_URL=sqlite:///stock_analysis.db
```

### Core API Connection Module
```python
# alpha_vantage_client.py
import os
import pandas as pd
import requests
from alpha_vantage.fundamentaldata import FundamentalData
from alpha_vantage.timeseries import TimeSeries
from dotenv import load_dotenv
import time
import sqlite3
from datetime import datetime, timedelta
import logging

load_dotenv()

class AlphaVantageClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('ALPHA_VANTAGE_API_KEY')
        self.fd = FundamentalData(key=self.api_key, output_format='pandas')
        self.ts = TimeSeries(key=self.api_key, output_format='pandas')
        self.base_url = "https://www.alphavantage.co/query"
        self.rate_limit_delay = 12  # seconds between calls
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def get_company_overview(self, symbol):
        """Fetch comprehensive company fundamentals"""
        try:
            params = {
                'function': 'OVERVIEW',
                'symbol': symbol,
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            if 'Error Message' in data or 'Note' in data:
                self.logger.warning(f"API limit or error for {symbol}: {data}")
                return None
                
            return data
            
        except Exception as e:
            self.logger.error(f"Error fetching overview for {symbol}: {e}")
            return None
    
    def get_income_statement(self, symbol):
        """Fetch annual income statement"""
        try:
            income_statement, _ = self.fd.get_income_statement_annual(symbol)
            time.sleep(self.rate_limit_delay)
            return income_statement
        except Exception as e:
            self.logger.error(f"Error fetching income statement for {symbol}: {e}")
            return None
    
    def get_balance_sheet(self, symbol):
        """Fetch annual balance sheet"""
        try:
            balance_sheet, _ = self.fd.get_balance_sheet_annual(symbol)
            time.sleep(self.rate_limit_delay)
            return balance_sheet
        except Exception as e:
            self.logger.error(f"Error fetching balance sheet for {symbol}: {e}")
            return None
    
    def get_cash_flow(self, symbol):
        """Fetch annual cash flow statement"""
        try:
            cash_flow, _ = self.fd.get_cash_flow_annual(symbol)
            time.sleep(self.rate_limit_delay)
            return cash_flow
        except Exception as e:
            self.logger.error(f"Error fetching cash flow for {symbol}: {e}")
            return None
```

## 2. Comprehensive Valuation Filtering System

```python
# valuation_filter.py
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import json
from dataclasses import dataclass
from datetime import datetime
import sqlite3

@dataclass
class ValuationCriteria:
    """Configurable valuation filter parameters"""
    # Value Metrics
    max_pe_ratio: float = 15.0
    max_pb_ratio: float = 3.0
    min_dividend_yield: float = 0.02  # 2%
    max_debt_to_equity: float = 0.5
    min_current_ratio: float = 1.5
    min_roe: float = 0.15  # 15%
    min_roa: float = 0.05  # 5%
    
    # Growth Metrics
    min_revenue_growth: float = 0.05  # 5%
    min_earnings_growth: float = 0.10  # 10%
    
    # Quality Metrics
    min_gross_margin: float = 0.30  # 30%
    min_operating_margin: float = 0.10  # 10%
    max_peg_ratio: float = 1.0
    
    # Market Cap filters
    min_market_cap: float = 1e9  # $1B minimum
    max_market_cap: float = 100e9  # $100B maximum

class StockValuationFilter:
    def __init__(self, av_client, db_path='stock_analysis.db'):
        self.av_client = av_client
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for storing analysis results"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS stock_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    pe_ratio REAL,
                    pb_ratio REAL,
                    dividend_yield REAL,
                    debt_to_equity REAL,
                    current_ratio REAL,
                    roe REAL,
                    roa REAL,
                    revenue_growth REAL,
                    earnings_growth REAL,
                    gross_margin REAL,
                    operating_margin REAL,
                    peg_ratio REAL,
                    market_cap REAL,
                    sector TEXT,
                    industry TEXT,
                    meets_criteria BOOLEAN,
                    valuation_score REAL,
                    raw_data TEXT
                )
            """)
    
    def calculate_valuation_metrics(self, symbol: str) -> Optional[Dict]:
        """Calculate comprehensive valuation metrics for a stock"""
        try:
            # Get company overview
            overview = self.av_client.get_company_overview(symbol)
            if not overview:
                return None
            
            # Extract key metrics with error handling
            def safe_float(value, default=0.0):
                try:
                    if value in ['None', 'N/A', '-', '']:
                        return default
                    return float(value)
                except (ValueError, TypeError):
                    return default
            
            metrics = {
                'symbol': symbol,
                'pe_ratio': safe_float(overview.get('PERatio')),
                'pb_ratio': safe_float(overview.get('PriceToBookRatio')),
                'dividend_yield': safe_float(overview.get('DividendYield')),
                'debt_to_equity': safe_float(overview.get('DebtToEquityRatio')),
                'current_ratio': safe_float(overview.get('CurrentRatio')),
                'roe': safe_float(overview.get('ReturnOnEquityTTM')),
                'roa': safe_float(overview.get('ReturnOnAssetsTTM')),
                'revenue_growth': safe_float(overview.get('QuarterlyRevenueGrowthYOY')),
                'earnings_growth': safe_float(overview.get('QuarterlyEarningsGrowthYOY')),
                'gross_margin': safe_float(overview.get('GrossProfitTTM')) / safe_float(overview.get('RevenueTTM'), 1),
                'operating_margin': safe_float(overview.get('OperatingMarginTTM')),
                'peg_ratio': safe_float(overview.get('PEGRatio')),
                'market_