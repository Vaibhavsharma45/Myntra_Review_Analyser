import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime
import time

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from scrapper.improved_scraper import scrape_with_retry
from analytics.sentiment_analysis import SentimentAnalyzer, extract_keywords
from analytics.visualizations import AdvancedVisualizer
from utils.export_utils import ExportManager

# Page config
st.set_page_config(
    page_title="Myntra Review Scraper Pro",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        border: none;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #764ba2 0%, #667eea 100%);
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'scraped_data' not in st.session_state:
    st.session_state.scraped_data = None
if 'analyzed_data' not in st.session_state:
    st.session_state.analyzed_data = None

# Header
st.markdown('<h1 class="main-header">🛍️ Myntra Review Scraper Pro</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Advanced Review Analysis with AI-Powered Sentiment Detection</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/shopping-bag.png", width=80)
    st.title("⚙️ Settings")
    
    product_name = st.text_input(
        "🔍 Product Name",
        placeholder="e.g., Nike shoes, Levis jeans",
        help="Enter the product you want to search for"
    )
    
    num_products = st.slider(
        "📊 Number of Products",
        min_value=1,
        max_value=10,
        value=3,
        help="How many products to scrape reviews from"
    )
    
    headless_mode = st.checkbox(
        "🚀 Headless Mode",
        value=True,
        help="Run browser in background (faster)"
    )
    
    st.divider()
    
    st.subheader("📥 Export Options")
    export_format = st.multiselect(
        "Choose formats",
        ["Excel", "CSV", "Summary Report"],
        default=["Excel"]
    )

# Main content
tab1, tab2, tab3, tab4 = st.tabs(["🏠 Scraper", "📊 Analytics", "💬 Reviews", "📈 Advanced"])

with tab1:
    st.header("Start Scraping")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info("👆 Configure your search in the sidebar and click 'Start Scraping'")
        
        if st.button("🚀 Start Scraping", type="primary", use_container_width=True):
            if not product_name:
                st.error("⚠️ Please enter a product name!")
            else:
                with st.spinner("🔄 Scraping reviews... This may take a few minutes..."):
                    # Progress tracking
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    info_box = st.empty()
                    
                    status_text.text("🌐 Initializing browser...")
                    progress_bar.progress(10)
                    time.sleep(0.5)
                    
                    status_text.text("🔍 Searching for products...")
                    progress_bar.progress(30)
                    
                    # Info message
                    info_box.info("💡 **Tip:** If products don't have reviews, the scraper will automatically skip them and search for more products.")
                    
                    # Scrape data
                    data = scrape_with_retry(
                        product_name=product_name,
                        no_of_products=num_products,
                        headless=headless_mode
                    )
                    
                    progress_bar.progress(70)
                    
                    if data is not None and not data.empty:
                        status_text.text("🤖 Analyzing sentiment...")
                        
                        # Sentiment analysis
                        analyzer = SentimentAnalyzer()
                        data = analyzer.analyze_dataframe(data)
                        
                        st.session_state.scraped_data = data
                        st.session_state.analyzed_data = data
                        
                        progress_bar.progress(100)
                        status_text.text("✅ Scraping completed!")
                        info_box.empty()  # Clear info message
                        
                        st.success(f"🎉 Successfully scraped {len(data)} reviews from {data['Product Name'].nunique()} products!")
                        
                        # Quick stats
                        col_a, col_b, col_c, col_d = st.columns(4)
                        with col_a:
                            st.metric("Total Reviews", len(data))
                        with col_b:
                            positive = len(data[data['VADER_Sentiment'] == 'Positive'])
                            st.metric("Positive", f"{positive} ({positive/len(data)*100:.0f}%)")
                        with col_c:
                            negative = len(data[data['VADER_Sentiment'] == 'Negative'])
                            st.metric("Negative", f"{negative} ({negative/len(data)*100:.0f}%)")
                        with col_d:
                            try:
                                rating_numeric = pd.to_numeric(
                                    data['Rating'].astype(str).str.extract(r'(\d+\.?\d*)')[0], 
                                    errors='coerce'
                                )
                                avg_rating = rating_numeric.mean()
                            except:
                                avg_rating = 0.0
                            st.metric("Avg Rating", f"{avg_rating:.2f} ⭐")
                    else:
                        progress_bar.progress(100)
                        status_text.text("❌ No reviews found")
                        info_box.empty()  # Clear info message
                        
                        st.error("😞 **No reviews found!**")
                        st.warning("""
                        **Possible reasons:**
                        - Products don't have customer reviews yet
                        - Product name might be too specific or misspelled
                        - Try searching for popular products or brand names
                        
                        **Suggestions:**
                        - Try: "Nike shoes", "Levis jeans", "Puma t-shirt"
                        - Increase number of products to search
                        - Use generic product names
                        """)
                        
                        # Show search suggestion
                        with st.expander("🔍 Search Tips"):
                            st.markdown("""
                            **Good searches:**
                            - ✅ Brand names: "Nike", "Adidas", "Puma"
                            - ✅ Generic products: "running shoes", "jeans", "t-shirt"
                            - ✅ Popular categories: "sneakers", "formal shirt"
                            
                            **Avoid:**
                            - ❌ Very specific: "Nike Air Max 270 React White"
                            - ❌ Model numbers: "SKU-12345"
                            - ❌ Rare products: "vintage cricket bat 1980"
                            """)
    
    with col2:
        st.subheader("📋 Features")
        st.markdown("""
        ✅ **Real-time scraping**  
        ✅ **AI Sentiment Analysis**  
        ✅ **Word Cloud Generation**  
        ✅ **Multiple Export Formats**  
        ✅ **Interactive Visualizations**  
        ✅ **Product Comparison**  
        """)

with tab2:
    st.header("📊 Analytics Dashboard")
    
    if st.session_state.analyzed_data is not None:
        df = st.session_state.analyzed_data
        viz = AdvancedVisualizer(df)
        
        # Key metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        total = len(df)
        pos = len(df[df['VADER_Sentiment'] == 'Positive'])
        neg = len(df[df['VADER_Sentiment'] == 'Negative'])
        neu = len(df[df['VADER_Sentiment'] == 'Neutral'])
        avg_sent = df['VADER_Score'].mean()
        
        with col1:
            st.metric("📝 Total Reviews", total)
        with col2:
            st.metric("😊 Positive", pos, f"{pos/total*100:.1f}%")
        with col3:
            st.metric("😐 Neutral", neu, f"{neu/total*100:.1f}%")
        with col4:
            st.metric("😞 Negative", neg, f"{neg/total*100:.1f}%")
        with col5:
            sentiment_emoji = "😊" if avg_sent > 0.05 else ("😞" if avg_sent < -0.05 else "😐")
            st.metric(f"{sentiment_emoji} Avg Sentiment", f"{avg_sent:.3f}")
        
        st.divider()
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(viz.create_sentiment_distribution(), use_container_width=True)
        
        with col2:
            st.plotly_chart(viz.create_rating_distribution(), use_container_width=True)
        
        st.plotly_chart(viz.create_sentiment_vs_rating(), use_container_width=True)
        
        st.plotly_chart(viz.create_product_comparison(), use_container_width=True)
        
        # Timeline chart
        timeline = viz.create_timeline_chart()
        if timeline:
            st.plotly_chart(timeline, use_container_width=True)
        
    else:
        st.info("👆 Please scrape some data first from the 'Scraper' tab!")

with tab3:
    st.header("💬 Review Explorer")
    
    if st.session_state.analyzed_data is not None:
        df = st.session_state.analyzed_data
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            sentiment_filter = st.multiselect(
                "Filter by Sentiment",
                options=df['VADER_Sentiment'].unique(),
                default=df['VADER_Sentiment'].unique()
            )
        
        with col2:
            product_filter = st.multiselect(
                "Filter by Product",
                options=df['Product Name'].unique(),
                default=df['Product Name'].unique()
            )
        
        with col3:
            rating_filter = st.multiselect(
                "Filter by Rating",
                options=sorted(df['Rating'].unique()),
                default=df['Rating'].unique()
            )
        
        # Apply filters
        filtered_df = df[
            (df['VADER_Sentiment'].isin(sentiment_filter)) &
            (df['Product Name'].isin(product_filter)) &
            (df['Rating'].isin(rating_filter))
        ]
        
        st.write(f"Showing {len(filtered_df)} reviews")
        
        # Display reviews
        for idx, row in filtered_df.iterrows():
            sentiment_color = {
                'Positive': '🟢',
                'Neutral': '🟡',
                'Negative': '🔴'
            }
            
            with st.expander(f"{sentiment_color.get(row['VADER_Sentiment'], '⚪')} {row['Product Name'][:50]}... - ⭐ {row['Rating']}"):
                st.write(f"**Reviewer:** {row['Reviewer']}")
                st.write(f"**Date:** {row['Date']}")
                st.write(f"**Sentiment:** {row['VADER_Sentiment']} (Score: {row['VADER_Score']:.3f})")
                st.write(f"**Review:** {row['Comment']}")
        
        # Export options
        st.divider()
        st.subheader("📥 Export Data")
        
        export_col1, export_col2, export_col3 = st.columns(3)
        
        with export_col1:
            if st.button("📊 Download Excel", use_container_width=True):
                filename = ExportManager.export_to_excel(filtered_df)
                if filename:
                    with open(filename, 'rb') as f:
                        st.download_button(
                            "⬇️ Download Excel File",
                            f,
                            file_name=filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
        
        with export_col2:
            if st.button("📄 Download CSV", use_container_width=True):
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    "⬇️ Download CSV File",
                    csv,
                    file_name=f"reviews_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        with export_col3:
            if st.button("📋 Generate Summary", use_container_width=True):
                summary = ExportManager.create_summary_report(filtered_df)
                st.download_button(
                    "⬇️ Download Summary",
                    summary,
                    file_name=f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
    else:
        st.info("👆 Please scrape some data first from the 'Scraper' tab!")

with tab4:
    st.header("📈 Advanced Analysis")
    
    if st.session_state.analyzed_data is not None:
        df = st.session_state.analyzed_data
        
        # Word clouds
        st.subheader("☁️ Word Clouds")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Positive Reviews**")
            viz = AdvancedVisualizer(df)
            wc_pos = viz.create_wordcloud('Positive')
            if wc_pos:
                st.image(wc_pos)
        
        with col2:
            st.write("**Negative Reviews**")
            wc_neg = viz.create_wordcloud('Negative')
            if wc_neg:
                st.image(wc_neg)
        
        st.divider()
        
        # Keyword extraction
        st.subheader("🔑 Top Keywords by Sentiment")
        
        keywords = extract_keywords(df)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if 'Positive' in keywords:
                st.write("**😊 Positive Reviews**")
                for word, count in keywords['Positive'][:10]:
                    st.write(f"• {word}: {count}")
        
        with col2:
            if 'Neutral' in keywords:
                st.write("**😐 Neutral Reviews**")
                for word, count in keywords['Neutral'][:10]:
                    st.write(f"• {word}: {count}")
        
        with col3:
            if 'Negative' in keywords:
                st.write("**😞 Negative Reviews**")
                for word, count in keywords['Negative'][:10]:
                    st.write(f"• {word}: {count}")
        
        st.divider()
        
        # Detailed stats table
        st.subheader("📊 Detailed Statistics")
        stats_df = viz.create_detailed_stats_table()
        st.dataframe(stats_df, use_container_width=True, hide_index=True)
        
    else:
        st.info("👆 Please scrape some data first from the 'Scraper' tab!")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>Made with ❤️ using Streamlit | Myntra Review Scraper Pro v2.0</p>
    <p>⚡ Powered by AI Sentiment Analysis</p>
</div>
""", unsafe_allow_html=True)
