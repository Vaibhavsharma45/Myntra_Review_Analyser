import pandas as pd
from datetime import datetime
import io
from fpdf import FPDF
import logging

logger = logging.getLogger(__name__)


class ExportManager:
    """Handle data export to various formats"""
    
    @staticmethod
    def export_to_excel(df, filename=None):
        """
        Export dataframe to Excel with formatting
        """
        if filename is None:
            filename = f"myntra_reviews_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        try:
            with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
                # Write main data
                df.to_excel(writer, sheet_name='Reviews', index=False)
                
                # Get workbook and worksheet
                workbook = writer.book
                worksheet = writer.sheets['Reviews']
                
                # Add formats
                header_format = workbook.add_format({
                    'bold': True,
                    'bg_color': '#4361EE',
                    'font_color': 'white',
                    'border': 1
                })
                
                # Format header
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                
                # Auto-adjust column widths
                for i, col in enumerate(df.columns):
                    max_length = max(
                        df[col].astype(str).apply(len).max(),
                        len(str(col))
                    )
                    worksheet.set_column(i, i, min(max_length + 2, 50))
                
                # Add statistics sheet
                try:
                    rating_numeric = pd.to_numeric(
                        df['Rating'].astype(str).str.extract(r'(\d+\.?\d*)')[0], 
                        errors='coerce'
                    )
                    avg_rating = f"{rating_numeric.mean():.2f}"
                except:
                    avg_rating = "N/A"
                
                stats_df = pd.DataFrame({
                    'Metric': [
                        'Total Reviews',
                        'Unique Products',
                        'Average Rating',
                        'Positive Reviews',
                        'Negative Reviews',
                        'Neutral Reviews'
                    ],
                    'Value': [
                        len(df),
                        df['Product Name'].nunique(),
                        avg_rating,
                        len(df[df['VADER_Sentiment'] == 'Positive']),
                        len(df[df['VADER_Sentiment'] == 'Negative']),
                        len(df[df['VADER_Sentiment'] == 'Neutral'])
                    ]
                })
                
                stats_df.to_excel(writer, sheet_name='Statistics', index=False)
                
            logger.info(f"Excel file exported: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error exporting to Excel: {e}")
            return None
    
    @staticmethod
    def export_to_csv(df, filename=None):
        """Export dataframe to CSV"""
        if filename is None:
            filename = f"myntra_reviews_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        try:
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            logger.info(f"CSV file exported: {filename}")
            return filename
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return None
    
    @staticmethod
    def create_summary_report(df):
        """Create a text summary report"""
        report = []
        report.append("=" * 60)
        report.append("MYNTRA REVIEW SCRAPER - SUMMARY REPORT")
        report.append("=" * 60)
        report.append(f"\nGenerated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"\n{'─' * 60}\n")
        
        # Basic stats
        report.append("OVERVIEW:")
        report.append(f"  Total Reviews Scraped: {len(df)}")
        report.append(f"  Unique Products: {df['Product Name'].nunique()}")
        report.append(f"  Date Range: {df['Date'].min()} to {df['Date'].max()}")
        
        # Rating stats
        report.append(f"\n{'─' * 60}\n")
        report.append("RATING ANALYSIS:")
        try:
            rating_numeric = pd.to_numeric(
                df['Rating'].astype(str).str.extract(r'(\d+\.?\d*)')[0], 
                errors='coerce'
            )
            avg_rating = rating_numeric.mean()
        except:
            avg_rating = 0.0
        report.append(f"  Average Rating: {avg_rating:.2f} stars")
        rating_dist = df['Rating'].value_counts().sort_index()
        for rating, count in rating_dist.items():
            report.append(f"  {rating} stars: {count} reviews ({count/len(df)*100:.1f}%)")
        
        # Sentiment stats
        report.append(f"\n{'─' * 60}\n")
        report.append("SENTIMENT ANALYSIS:")
        sentiment_dist = df['VADER_Sentiment'].value_counts()
        for sentiment, count in sentiment_dist.items():
            report.append(f"  {sentiment}: {count} reviews ({count/len(df)*100:.1f}%)")
        
        avg_sentiment = df['VADER_Score'].mean()
        report.append(f"  Average Sentiment Score: {avg_sentiment:.3f}")
        
        # Top products
        report.append(f"\n{'─' * 60}\n")
        report.append("TOP PRODUCTS BY REVIEW COUNT:")
        top_products = df['Product Name'].value_counts().head(5)
        for idx, (product, count) in enumerate(top_products.items(), 1):
            report.append(f"  {idx}. {product[:50]}... ({count} reviews)")
        
        # Most positive/negative
        report.append(f"\n{'─' * 60}\n")
        report.append("SENTIMENT HIGHLIGHTS:")
        
        most_positive = df.nlargest(3, 'VADER_Score')
        report.append("\n  Most Positive Reviews:")
        for idx, row in most_positive.iterrows():
            comment = row['Comment'][:80] + "..." if len(str(row['Comment'])) > 80 else row['Comment']
            report.append(f"    • {comment}")
            report.append(f"      Rating: {row['Rating']} | Sentiment: {row['VADER_Score']:.2f}")
        
        most_negative = df.nsmallest(3, 'VADER_Score')
        report.append("\n  Most Negative Reviews:")
        for idx, row in most_negative.iterrows():
            comment = row['Comment'][:80] + "..." if len(str(row['Comment'])) > 80 else row['Comment']
            report.append(f"    • {comment}")
            report.append(f"      Rating: {row['Rating']} | Sentiment: {row['VADER_Score']:.2f}")
        
        report.append(f"\n{'═' * 60}\n")
        
        return '\n'.join(report)
    
    @staticmethod
    def export_summary_to_txt(df, filename=None):
        """Export summary report to text file"""
        if filename is None:
            filename = f"summary_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        try:
            report = ExportManager.create_summary_report(df)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"Summary report exported: {filename}")
            return filename
        except Exception as e:
            logger.error(f"Error exporting summary: {e}")
            return None
