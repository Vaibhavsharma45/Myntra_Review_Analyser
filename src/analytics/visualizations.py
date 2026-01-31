import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import base64


class AdvancedVisualizer:
    """Create advanced visualizations for review data"""
    
    def __init__(self, df):
        self.df = df
    
    def create_sentiment_distribution(self):
        """Pie chart showing sentiment distribution"""
        sentiment_counts = self.df['VADER_Sentiment'].value_counts()
        
        colors = {
            'Positive': '#00D26A',
            'Neutral': '#FFB020',
            'Negative': '#FF4B4B'
        }
        
        fig = go.Figure(data=[go.Pie(
            labels=sentiment_counts.index,
            values=sentiment_counts.values,
            marker=dict(colors=[colors.get(s, '#888888') for s in sentiment_counts.index]),
            hole=0.4,
            textinfo='label+percent',
            textfont_size=14
        )])
        
        fig.update_layout(
            title="Sentiment Distribution",
            title_font_size=20,
            height=500
        )
        
        return fig
    
    def create_rating_distribution(self):
        """Bar chart showing rating distribution"""
        rating_counts = self.df['Rating'].value_counts().sort_index()
        
        fig = go.Figure(data=[go.Bar(
            x=rating_counts.index,
            y=rating_counts.values,
            marker_color='#4361EE',
            text=rating_counts.values,
            textposition='auto',
        )])
        
        fig.update_layout(
            title="Rating Distribution",
            xaxis_title="Rating (Stars)",
            yaxis_title="Number of Reviews",
            title_font_size=20,
            height=500,
            showlegend=False
        )
        
        return fig
    
    def create_sentiment_vs_rating(self):
        """Box plot comparing sentiment scores vs ratings"""
        fig = px.box(
            self.df,
            x='Rating',
            y='VADER_Score',
            color='VADER_Sentiment',
            title="Sentiment Score vs Star Rating",
            color_discrete_map={
                'Positive': '#00D26A',
                'Neutral': '#FFB020',
                'Negative': '#FF4B4B'
            }
        )
        
        fig.update_layout(
            xaxis_title="Star Rating",
            yaxis_title="VADER Sentiment Score",
            title_font_size=20,
            height=500
        )
        
        return fig
    
    def create_product_comparison(self):
        """Compare products by average rating and sentiment"""
        # Convert Rating to numeric first
        df_copy = self.df.copy()
        df_copy['Rating_Numeric'] = pd.to_numeric(
            df_copy['Rating'].astype(str).str.extract(r'(\d+\.?\d*)')[0], 
            errors='coerce'
        )
        
        product_stats = df_copy.groupby('Product Name').agg({
            'Rating_Numeric': 'mean',
            'VADER_Score': 'mean',
            'Comment': 'count'
        }).reset_index()
        
        product_stats.columns = ['Product', 'Avg Rating', 'Avg Sentiment', 'Review Count']
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=("Average Rating by Product", "Review Count by Product"),
            specs=[[{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Average Rating
        fig.add_trace(
            go.Bar(
                x=product_stats['Product'],
                y=product_stats['Avg Rating'],
                name='Avg Rating',
                marker_color='#7209B7',
                text=product_stats['Avg Rating'].round(2),
                textposition='auto'
            ),
            row=1, col=1
        )
        
        # Review Count
        fig.add_trace(
            go.Bar(
                x=product_stats['Product'],
                y=product_stats['Review Count'],
                name='Review Count',
                marker_color='#F72585',
                text=product_stats['Review Count'],
                textposition='auto'
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            title_text="Product Comparison",
            title_font_size=20,
            height=500,
            showlegend=False
        )
        
        return fig
    
    def create_wordcloud(self, sentiment_type='Positive'):
        """Generate word cloud for specific sentiment"""
        sentiment_reviews = self.df[self.df['VADER_Sentiment'] == sentiment_type]['Comment']
        text = ' '.join(sentiment_reviews.astype(str))
        
        if not text.strip():
            return None
        
        # Generate word cloud
        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color='white',
            colormap='viridis' if sentiment_type == 'Positive' else 'Reds',
            max_words=100
        ).generate(text)
        
        # Convert to image
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        ax.set_title(f'{sentiment_type} Reviews Word Cloud', fontsize=16, fontweight='bold')
        
        # Convert to base64 for Streamlit
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
        buf.seek(0)
        plt.close()
        
        return buf
    
    def create_timeline_chart(self):
        """Show sentiment trends over time"""
        # Try to parse dates
        try:
            self.df['Date_Parsed'] = pd.to_datetime(self.df['Date'], errors='coerce')
            df_with_dates = self.df.dropna(subset=['Date_Parsed'])
            
            if len(df_with_dates) == 0:
                return None
            
            # Group by date and sentiment
            timeline = df_with_dates.groupby([
                df_with_dates['Date_Parsed'].dt.to_period('M'),
                'VADER_Sentiment'
            ]).size().reset_index(name='Count')
            
            timeline['Date'] = timeline['Date_Parsed'].astype(str)
            
            fig = px.line(
                timeline,
                x='Date',
                y='Count',
                color='VADER_Sentiment',
                title="Review Sentiment Over Time",
                color_discrete_map={
                    'Positive': '#00D26A',
                    'Neutral': '#FFB020',
                    'Negative': '#FF4B4B'
                },
                markers=True
            )
            
            fig.update_layout(
                xaxis_title="Month",
                yaxis_title="Number of Reviews",
                title_font_size=20,
                height=500
            )
            
            return fig
        except:
            return None
    
    def create_detailed_stats_table(self):
        """Create detailed statistics table"""
        stats = {
            'Metric': [],
            'Value': []
        }
        
        stats['Metric'].extend([
            'Total Reviews',
            'Average Rating',
            'Positive Reviews %',
            'Negative Reviews %',
            'Neutral Reviews %',
            'Average Sentiment Score',
            'Unique Products'
        ])
        
        total = len(self.df)
        pos = len(self.df[self.df['VADER_Sentiment'] == 'Positive'])
        neg = len(self.df[self.df['VADER_Sentiment'] == 'Negative'])
        neu = len(self.df[self.df['VADER_Sentiment'] == 'Neutral'])
        
        # Convert Rating to numeric properly
        try:
            rating_numeric = pd.to_numeric(
                self.df['Rating'].astype(str).str.extract(r'(\d+\.?\d*)')[0], 
                errors='coerce'
            )
            avg_rating = rating_numeric.mean()
        except:
            avg_rating = 0.0
        
        stats['Value'].extend([
            str(total),
            f"{avg_rating:.2f}",
            f"{(pos/total*100):.1f}%",
            f"{(neg/total*100):.1f}%",
            f"{(neu/total*100):.1f}%",
            f"{self.df['VADER_Score'].mean():.3f}",
            str(self.df['Product Name'].nunique())
        ])
        
        return pd.DataFrame(stats)