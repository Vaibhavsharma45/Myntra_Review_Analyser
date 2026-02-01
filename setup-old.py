from setuptools import setup, find_packages

setup(
    name="myntra-scraper-improved",
    version="2.0.0",
    author="Your Name",
    description="Advanced Myntra Review Scraper with Sentiment Analysis",
    packages=find_packages(),
    install_requires=[
        "streamlit>=1.28.0",
        "selenium>=4.15.2",
        "beautifulsoup4>=4.12.2",
        "pandas>=2.1.3",
        "plotly>=5.18.0",
    ],
    python_requires=">=3.10",
)
