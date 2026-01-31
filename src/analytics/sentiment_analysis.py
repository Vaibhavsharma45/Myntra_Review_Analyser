import pandas as pd
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import logging

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Analyze sentiment of reviews using multiple methods"""
    
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()
    
    def analyze_textblob(self, text):
        """
        Analyze sentiment using TextBlob
        Returns: polarity (-1 to 1), subjectivity (0 to 1)
        """
        try:
            blob = TextBlob(str(text))
            return blob.sentiment.polarity, blob.sentiment.subjectivity
        except:
            return 0, 0
    
    def analyze_vader(self, text):
        """
        Analyze sentiment using VADER
        Returns: compound score (-1 to 1)
        """
        try:
            scores = self.vader.polarity_scores(str(text))
            return scores['compound']
        except:
            return 0
    
    def get_sentiment_label(self, score):
        """
        Convert numerical score to label
        """
        if score >= 0.05:
            return "Positive"
        elif score <= -0.05:
            return "Negative"
        else:
            return "Neutral"
    
    def analyze_dataframe(self, df, text_column='Comment'):
        """
        Add sentiment analysis to entire dataframe
        """
        logger.info("Starting sentiment analysis...")
        
        # TextBlob analysis
        df['TB_Polarity'], df['TB_Subjectivity'] = zip(*df[text_column].apply(self.analyze_textblob))
        df['TB_Sentiment'] = df['TB_Polarity'].apply(self.get_sentiment_label)
        
        # VADER analysis
        df['VADER_Score'] = df[text_column].apply(self.analyze_vader)
        df['VADER_Sentiment'] = df['VADER_Score'].apply(self.get_sentiment_label)
        
        logger.info("Sentiment analysis completed!")
        return df
    
    def get_sentiment_stats(self, df):
        """
        Get sentiment statistics
        """
        stats = {
            'TextBlob': df['TB_Sentiment'].value_counts().to_dict(),
            'VADER': df['VADER_Sentiment'].value_counts().to_dict(),
            'Average_Polarity': df['TB_Polarity'].mean(),
            'Average_VADER': df['VADER_Score'].mean()
        }
        return stats


def extract_keywords(df, text_column='Comment', sentiment_column='VADER_Sentiment', top_n=20):
    """
    Extract most common keywords from reviews by sentiment
    """
    from collections import Counter
    import re
    
    # Stop words to ignore
    stop_words = set(['the', 'is', 'in', 'and', 'to', 'a', 'of', 'for', 'it', 'this', 
                      'that', 'on', 'with', 'as', 'are', 'was', 'be', 'but', 'not',
                      'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
                      'can', 'could', 'should', 'i', 'you', 'my', 'me', 'your'])
    
    results = {}
    
    for sentiment in df[sentiment_column].unique():
        sentiment_reviews = df[df[sentiment_column] == sentiment][text_column]
        
        # Extract words
        words = []
        for review in sentiment_reviews:
            # Convert to lowercase and extract words
            text = str(review).lower()
            text_words = re.findall(r'\b[a-z]{3,}\b', text)
            words.extend([w for w in text_words if w not in stop_words])
        
        # Count frequency
        word_counts = Counter(words)
        results[sentiment] = word_counts.most_common(top_n)
    
    return results
