# electrek_scraper/utils/scraper_service.py
from bs4 import BeautifulSoup
from datetime import datetime
import re
import os
import time
import random
from .proxy_manager import ProxyManager

class ElectrekScraper:
    def __init__(self, use_proxy=None):
        self.base_url = "https://electrek.co"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Store original proxy setting if we need to override it
        if use_proxy is not None:
            original_value = os.environ.get('USE_PROXY')
            os.environ['USE_PROXY'] = 'true' if use_proxy else 'false'
            self.proxy_manager = ProxyManager()
            if original_value is not None:
                os.environ['USE_PROXY'] = original_value
            else:
                os.environ.pop('USE_PROXY', None)
        else:
            self.proxy_manager = ProxyManager()
    
    def get_article_urls(self, limit=25, pages=1, page_delay=2.0):
        """
        Get article URLs from multiple pages
        
        Parameters:
        - limit: Maximum number of articles to collect (up to 2000)
        - pages: Maximum number of pages to visit (up to 80)
        - page_delay: Base delay between page requests in seconds
        """
        all_article_urls = []
        
        print(f"Starting article collection: targeting {limit} articles across up to {pages} pages")
        start_time = time.time()
        
        # Scrape multiple pages if needed
        for page_num in range(1, pages + 1):
            if page_num == 1:
                page_url = self.base_url
            else:
                page_url = f"{self.base_url}/page/{page_num}/"
                
            print(f"Fetching page {page_num}/{pages}: {page_url}")
            
            # Add progressive delay for higher page numbers to avoid rate limiting
            if page_num > 1:
                # Scale delay slightly with page number for very large scrapes
                actual_delay = page_delay * (1 + (page_num / 100))
                # Add randomness to appear more human-like
                delay = random.uniform(actual_delay, actual_delay * 1.5)
                print(f"Waiting {delay:.2f} seconds before fetching page {page_num}...")
                time.sleep(delay)
                
            response = self.proxy_manager.make_request(
                page_url,
                headers=self.headers
            )
            
            if not response:
                print(f"Failed to retrieve page {page_num}")
                # Add longer delay after failure to reduce pressure
                time.sleep(page_delay * 2)
                continue
                    
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find article links
            article_links = soup.select("article h2 a")
            
            # Track progress
            previous_count = len(all_article_urls)
            
            # Process links
            for link in article_links:
                if 'href' in link.attrs:
                    url = link['href']
                    # Make sure we have absolute URLs
                    if not url.startswith('http'):
                        url = f"{self.base_url.rstrip('/')}/{url.lstrip('/')}"
                    all_article_urls.append(url)
                    
            # Report progress
            new_count = len(all_article_urls) - previous_count
            total_count = len(all_article_urls)
            print(f"Found {new_count} new article links on page {page_num} (Total: {total_count}/{limit})")
            
            # Stop if we've reached our limit
            if len(all_article_urls) >= limit:
                print(f"Reached article limit ({limit}). Stopping page fetching.")
                break
        
        # Calculate and report stats
        elapsed_time = time.time() - start_time
        collected_count = min(len(all_article_urls), limit)
        pages_visited = page_num
        
        print(f"Article collection complete:")
        print(f"- Collected {collected_count} article URLs")
        print(f"- Visited {pages_visited} pages")
        print(f"- Time elapsed: {elapsed_time:.2f} seconds")
        
        # Return only up to the requested limit
        return all_article_urls[:limit]
    
    def parse_article(self, url):
        """Parse an article page - simplified to only get metadata with better error handling"""
        print(f"Parsing article metadata: {url}")
        
        # Add a short random delay
        time.sleep(random.uniform(0.5, 1.5))
        
        try:
            response = self.proxy_manager.make_request(
                url, 
                headers=self.headers
            )
            
            if not response:
                print(f"Failed to retrieve article at {url}")
                raise Exception(f"Could not retrieve article at {url}")
                    
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract just the metadata fields
            title_element = soup.select_one("h1.h1") or soup.select_one("h1")
            title = title_element.text.strip() if title_element else "No title found"
            
            author_element = soup.select_one("span.author-name") or soup.select_one(".author-name")
            author = author_element.text.strip() if author_element else "Unknown author"
            
            # Extract date - simplified approach
            date_text = None
            date_pattern = r'\w+\s+\d+\s+\d{4}\s+-\s+\d+:\d+\s+[ap]m'
            date_element = soup.find(string=re.compile(date_pattern))
            
            published_at = None
            if date_element:
                try:
                    date_text = date_element.strip()
                    date_text = re.sub(r'[^\w\s:-]', '', date_text).strip()
                    date_text = date_text.replace("PT", "").strip()
                    published_at = datetime.strptime(date_text, '%b %d %Y - %I:%M %p')
                except ValueError as e:
                    print(f"Error parsing date: {e}")
                    published_at = datetime.now()  # Fallback to current time
            
            # Extract comment count - simplified
            comment_count = 0
            comment_element = soup.select_one("a#single-comments-link")
            if comment_element:
                comment_text = comment_element.text.strip()
                count_match = re.search(r'(\d+)', comment_text)
                if count_match:
                    comment_count = int(count_match.group(1))
            
            # Return simplified result
            result = {
                'title': title,
                'url': url,
                'author': author,
                'published_at': published_at,
                'comment_count': comment_count
            }
            
            print(f"Extracted metadata: {result}")
            return result
            
        except Exception as e:
            print(f"Error parsing article: {e}")
            # Return basic data even on error
            return {
                'title': f"Error: {str(e)[:30]}...",
                'url': url,
                'author': "Unknown",
                'published_at': datetime.now(),
                'comment_count': 0
            }