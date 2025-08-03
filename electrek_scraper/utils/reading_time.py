"""
Reading time estimation service
"""
import re
from bs4 import BeautifulSoup

class ReadingTimeEstimator:
    """Calculate estimated reading time for articles"""
    
    def __init__(self, words_per_minute=250):
        self.words_per_minute = words_per_minute
    
    def strip_html(self, html_content):
        """Remove HTML tags and extract clean text"""
        if not html_content:
            return ""
        
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def count_words(self, text):
        """Count words in text"""
        if not text:
            return 0
        
        # Split on whitespace and filter out empty strings
        words = [word for word in re.split(r'\s+', text.strip()) if word]
        return len(words)
    
    def count_charts_and_images(self, html_content):
        """Count charts and images that add to reading time"""
        if not html_content:
            return 0
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Count charts (canvas elements, chart containers)
        charts = len(soup.find_all(['canvas'])) + len(soup.find_all(class_=['chart-container', 'chart']))
        
        # Count images
        images = len(soup.find_all('img'))
        
        return charts + images
    
    def calculate_reading_time(self, html_content):
        """Calculate estimated reading time in minutes"""
        if not html_content:
            return 1  # Minimum 1 minute
        
        # Extract text and count words
        text = self.strip_html(html_content)
        word_count = self.count_words(text)
        
        # Count visual elements that take time to process
        visual_elements = self.count_charts_and_images(html_content)
        
        # Calculate base reading time (words / WPM)
        base_time = word_count / self.words_per_minute
        
        # Add 0.5 minutes (30 seconds) per chart/image
        visual_time = visual_elements * 0.5
        
        # Total time in minutes
        total_time = base_time + visual_time
        
        # Round to nearest minute, minimum 1 minute
        reading_time = max(1, round(total_time))
        
        return reading_time
    
    def format_reading_time(self, html_content):
        """Get formatted reading time string"""
        minutes = self.calculate_reading_time(html_content)
        
        if minutes == 1:
            return "1 min read"
        else:
            return f"{minutes} min read"