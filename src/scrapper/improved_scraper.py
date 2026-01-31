from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
import pandas as pd
import time
import sys
import os
from urllib.parse import quote
from tqdm import tqdm
import logging

# For cloud deployment
try:
    from webdriver_manager.chrome import ChromeDriverManager
    CLOUD_MODE = True
except ImportError:
    CLOUD_MODE = False

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImprovedScraper:
    def __init__(self, product_name: str, no_of_products: int, headless: bool = False):
        """
        Initialize the scraper with improved settings
        
        Args:
            product_name: Product to search for
            no_of_products: Number of products to scrape
            headless: Run browser in headless mode (no GUI)
        """
        options = Options()
        
        # Performance optimizations
        if headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        
        # Add user agent to avoid detection
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
        
        try:
            # Initialize Chrome driver
            if CLOUD_MODE:
                # For cloud deployment (Streamlit Cloud, Heroku, etc.)
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
            else:
                # For local development
                self.driver = webdriver.Chrome(options=options)
            
            self.driver.set_page_load_timeout(30)
            logger.info("Browser initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            raise
        
        self.product_name = product_name
        self.no_of_products = no_of_products
        self.wait = WebDriverWait(self.driver, 10)

    def scrape_product_urls(self):
        """Scrape product URLs from search results"""
        try:
            search_string = self.product_name.replace(" ", "-")
            encoded_query = quote(search_string)
            url = f"https://www.myntra.com/{search_string}?rawQuery={encoded_query}"
            
            logger.info(f"Searching for: {self.product_name}")
            self.driver.get(url)
            time.sleep(3)  # Wait for page to load
            
            myntra_html = bs(self.driver.page_source, "html.parser")
            pclass = myntra_html.findAll("ul", {"class": "results-base"})
            
            product_urls = []
            for i in pclass:
                href = i.find_all("a", href=True)
                for product_no in range(len(href)):
                    t = href[product_no]["href"]
                    product_urls.append(t)
            
            logger.info(f"Found {len(product_urls)} products")
            return product_urls
            
        except Exception as e:
            logger.error(f"Error scraping product URLs: {e}")
            return []

    def extract_reviews(self, product_link):
        """Extract reviews from a product page"""
        try:
            productLink = "https://www.myntra.com/" + product_link
            self.driver.get(productLink)
            time.sleep(2)
            
            prodRes_html = bs(self.driver.page_source, "html.parser")
            
            # Extract product details
            title_h = prodRes_html.findAll("title")
            self.product_title = title_h[0].text if title_h else "Unknown Product"
            
            overallRating = prodRes_html.findAll("div", {"class": "index-overallRating"})
            self.product_rating_value = "N/A"
            for i in overallRating:
                rating_div = i.find("div")
                if rating_div:
                    self.product_rating_value = rating_div.text
            
            price = prodRes_html.findAll("span", {"class": "pdp-price"})
            self.product_price = "N/A"
            for i in price:
                self.product_price = i.text
            
            product_reviews = prodRes_html.find("a", {"class": "detailed-reviews-allReviews"})
            
            if not product_reviews:
                logger.warning(f"No reviews found for: {self.product_title}")
                return None
                
            return product_reviews
            
        except Exception as e:
            logger.error(f"Error extracting reviews: {e}")
            return None

    def scroll_to_load_reviews(self):
        """Scroll page to load all reviews with progress indication"""
        try:
            self.driver.set_window_size(1920, 1080)
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            scroll_count = 0
            max_scrolls = 20  # Prevent infinite scrolling
            
            while scroll_count < max_scrolls:
                self.driver.execute_script("window.scrollBy(0, 1000);")
                time.sleep(2)
                
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                
                if new_height == last_height:
                    break
                
                last_height = new_height
                scroll_count += 1
                
            logger.info(f"Scrolled {scroll_count} times to load reviews")
            
        except Exception as e:
            logger.error(f"Error during scrolling: {e}")

    def extract_review_data(self, product_reviews):
        """Extract individual review data"""
        try:
            review_link = "https://www.myntra.com" + product_reviews["href"]
            self.driver.get(review_link)
            
            self.scroll_to_load_reviews()
            
            review_html = bs(self.driver.page_source, "html.parser")
            review_container = review_html.findAll("div", {"class": "detailed-reviews-userReviewsContainer"})
            
            reviews = []
            
            for container in review_container:
                user_rating = container.findAll("div", {"class": "user-review-main user-review-showRating"})
                user_comment = container.findAll("div", {"class": "user-review-reviewTextWrapper"})
                user_name = container.findAll("div", {"class": "user-review-left"})
                
                for i in range(len(user_rating)):
                    try:
                        rating = user_rating[i].find("span", class_="user-review-starRating").get_text().strip()
                    except:
                        rating = "No rating"
                    
                    try:
                        comment = user_comment[i].text.strip()
                    except:
                        comment = "No comment"
                    
                    try:
                        name = user_name[i].find("span").text.strip()
                    except:
                        name = "Anonymous"
                    
                    try:
                        date = user_name[i].find_all("span")[1].text.strip()
                    except:
                        date = "Unknown date"
                    
                    review_dict = {
                        "Product Name": self.product_title,
                        "Overall Rating": self.product_rating_value,
                        "Price": self.product_price,
                        "Date": date,
                        "Rating": rating,
                        "Reviewer": name,
                        "Comment": comment,
                    }
                    reviews.append(review_dict)
            
            if reviews:
                logger.info(f"Extracted {len(reviews)} reviews for {self.product_title}")
                return pd.DataFrame(reviews)
            else:
                logger.warning("No reviews extracted")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting review data: {e}")
            return None

    def scrape_all_reviews(self):
        """Main method to scrape all reviews with progress bar"""
        try:
            product_urls = self.scrape_product_urls()
            
            if not product_urls:
                logger.error("No products found!")
                return None
            
            all_reviews = []
            products_scraped = 0
            products_checked = 0
            max_products_to_check = min(len(product_urls), self.no_of_products * 3)  # Check up to 3x requested
            
            # Progress bar
            pbar = tqdm(total=self.no_of_products, desc="Scraping Products")
            
            for idx, url in enumerate(product_urls):
                if products_scraped >= self.no_of_products:
                    break
                
                if products_checked >= max_products_to_check:
                    logger.warning(f"Checked {products_checked} products, found only {products_scraped} with reviews")
                    break
                
                products_checked += 1
                pbar.set_description(f"Product {products_scraped + 1}/{self.no_of_products} (Checked: {products_checked})")
                
                reviews_link = self.extract_reviews(url)
                
                if reviews_link:
                    review_data = self.extract_review_data(reviews_link)
                    
                    if review_data is not None and not review_data.empty:
                        all_reviews.append(review_data)
                        products_scraped += 1
                        pbar.update(1)
                        logger.info(f"✓ Found {len(review_data)} reviews from product {products_scraped}")
                else:
                    # Show user that this product has no reviews
                    if products_checked % 5 == 0:  # Update every 5 products
                        logger.info(f"Still searching... Checked {products_checked} products, found {products_scraped} with reviews")
                
                # Add delay to avoid being blocked
                time.sleep(2)
            
            pbar.close()
            
            if all_reviews:
                final_data = pd.concat(all_reviews, ignore_index=True)
                logger.info(f"✓ SUCCESS: Total {len(final_data)} reviews scraped from {products_scraped} products!")
                return final_data
            else:
                logger.error(f"✗ NO REVIEWS FOUND: Checked {products_checked} products but none had reviews")
                logger.error("Try searching for a different product or popular brands")
                return None
                
        except Exception as e:
            logger.error(f"Error in main scraping process: {e}")
            return None
        finally:
            self.close()

    def close(self):
        """Close the browser"""
        try:
            self.driver.quit()
            logger.info("Browser closed successfully")
        except:
            pass


# Retry mechanism wrapper
def scrape_with_retry(product_name, no_of_products, max_retries=3, headless=False):
    """Scrape with retry mechanism"""
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempt {attempt + 1}/{max_retries}")
            scraper = ImprovedScraper(product_name, no_of_products, headless=headless)
            data = scraper.scrape_all_reviews()
            
            if data is not None:
                return data
            else:
                logger.warning(f"Attempt {attempt + 1} returned no data")
                
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                logger.info("Retrying...")
                time.sleep(5)
            else:
                logger.error("All retry attempts failed")
                return None
    
    return None
