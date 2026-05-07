# Automated Sentiment Analysis Report Generator

## Project Overview

I'll synthesize all the completed subtasks into a comprehensive automated report generator that combines sentiment analysis with market mood insights and generates professional HTML/PDF reports.

## Complete System Architecture

[ACTION:BUILD]

### 1. Project Structure
```
sentiment-report-generator/
├── src/
│   ├── sentiment/
│   │   ├── __init__.py
│   │   ├── models.py           # Multi-model sentiment analysis
│   │   ├── processors.py       # Text preprocessing
│   │   └── analyzers.py        # Ensemble sentiment scoring
│   ├── mood/
│   │   ├── __init__.py
│   │   ├── engine.py          # Market mood aggregation
│   │   ├── indicators.py       # Technical indicators
│   │   └── synthesizer.py      # Mood synthesis
│   ├── reports/
│   │   ├── __init__.py
│   │   ├── generator.py        # HTML/PDF generation
│   │   ├── visualizer.py       # Charts and graphs
│   │   └── templates/          # Report templates
│   ├── data/
│   │   ├── __init__.py
│   │   ├── collectors.py       # Data ingestion
│   │   └── storage.py          # Data persistence
│   └── utils/
│       ├── __init__.py
│       ├── config.py
│       └── logger.py
├── tests/                      # Comprehensive test suite
├── automation/
│   ├── airflow_dags/          # Airflow orchestration
│   ├── docker/                # Containerization
│   └── scripts/               # Deployment scripts
├── requirements.txt
├── docker-compose.yml
└── README.md
```

### 2. Core Sentiment Analysis Engine

```python
# src/sentiment/models.py
from dataclasses import dataclass
from datetime import datetime
import numpy as np
from typing import Dict, List, Optional, Tuple
import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from textblob import TextBlob
import yfinance as yf

@dataclass
class SentimentScore:
    score: float
    confidence: float
    label: str
    timestamp: datetime
    source: str

class FinancialSentimentAnalyzer:
    """Multi-model ensemble sentiment analyzer for financial texts"""
    
    def __init__(self):
        self.models = self._initialize_models()
        self.weights = {
            'finbert': 0.4,
            'textblob': 0.2,
            'vader': 0.2,
            'custom_financial': 0.2
        }
    
    def _initialize_models(self):
        """Initialize pre-trained models"""
        return {
            'finbert': {
                'tokenizer': AutoTokenizer.from_pretrained('ProsusAI/finbert'),
                'model': AutoModelForSequenceClassification.from_pretrained('ProsusAI/finbert')
            }
        }
    
    def analyze_text(self, text: str) -> SentimentScore:
        """Perform ensemble sentiment analysis"""
        scores = {}
        
        # FinBERT analysis
        scores['finbert'] = self._finbert_analysis(text)
        
        # TextBlob analysis
        blob = TextBlob(text)
        scores['textblob'] = blob.sentiment.polarity
        
        # Weighted ensemble
        weighted_score = sum(scores[model] * self.weights[model] 
                           for model in scores.keys() if model in self.weights)
        
        confidence = self._calculate_confidence(scores)
        label = self._score_to_label(weighted_score)
        
        return SentimentScore(
            score=weighted_score,
            confidence=confidence,
            label=label,
            timestamp=datetime.now(),
            source='ensemble'
        )
    
    def _finbert_analysis(self, text: str) -> float:
        """FinBERT-specific analysis"""
        tokenizer = self.models['finbert']['tokenizer']
        model = self.models['finbert']['model']
        
        inputs = tokenizer(text, return_tensors="pt", truncation=True, 
                          padding=True, max_length=512)
        
        with torch.no_grad():
            outputs = model(**inputs)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
        # Convert to sentiment score (-1 to 1)
        negative, neutral, positive = predictions[0].tolist()
        return positive - negative
    
    def _calculate_confidence(self, scores: Dict[str, float]) -> float:
        """Calculate ensemble confidence"""
        return 1.0 - np.std(list(scores.values()))
    
    def _score_to_label(self, score: float) -> str:
        """Convert numerical score to label"""
        if score > 0.1:
            return 'positive'
        elif score < -0.1:
            return 'negative'
        else:
            return 'neutral'
```

### 3. Market Mood Aggregation Engine

```python
# src/mood/engine.py
from typing import Dict, List, Tuple, Optional
import pandas as pd
import numpy as np
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class MarketMoodIndex:
    overall_mood: float
    sentiment_component: float
    technical_component: float
    volume_component: float
    volatility_component: float
    confidence: float
    timestamp: datetime
    
class MarketMoodAggregator:
    """Aggregates multiple data sources into comprehensive market mood"""
    
    def __init__(self):
        self.weights = {
            'sentiment': 0.35,
            'technical': 0.25,
            'volume': 0.20,
            'volatility': 0.20
        }
    
    def calculate_mood_index(self, 
                           sentiment_data: List[SentimentScore],
                           price_data: pd.DataFrame,
                           volume_data: pd.DataFrame) -> MarketMoodIndex:
        """Calculate comprehensive market mood index"""
        
        # Sentiment component
        sentiment_component = self._aggregate_sentiment(sentiment_data)
        
        # Technical indicators component
        technical_component = self._calculate_technical_mood(price_data)
        
        # Volume analysis component
        volume_component = self._analyze_volume_patterns(volume_data)
        
        # Volatility component
        volatility_component = self._calculate_volatility_mood(price_data)
        
        # Weighted overall mood
        overall_mood = (
            sentiment_component * self.weights['sentiment'] +
            technical_component * self.weights['technical'] +
            volume_component * self.weights['volume'] +
            volatility_component * self.weights['volatility']
        )
        
        confidence = self._calculate_mood_confidence(
            sentiment_component, technical_component, 
            volume_component, volatility_component
        )
        
        return MarketMoodIndex(
            overall_mood=overall_mood,
            sentiment_component=sentiment_component,
            technical_component=technical_component,
            volume_component=volume_component,
            volatility_component=volatility_component,
            confidence=confidence,
            timestamp=datetime.now()
        )
    
    def _aggregate_sentiment(self, sentiment_data: List[SentimentScore]) -> float:
        """Aggregate sentiment scores with recency weighting"""
        if not sentiment_data:
            return 0.0
            
        total_weight = 0
        weighted_sum = 0
        
        for sentiment in sentiment_data:
            # Exponential decay for recency
            hours_old = (datetime.now() - sentiment.timestamp).total_seconds() / 3600
            weight = sentiment.confidence * np.exp(-hours_old / 12)  # 12-hour half-life
            
            weighted_sum += sentiment.score * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    