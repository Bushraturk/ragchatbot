"""
Web Scraper Module

This module provides functionality to scrape content from web pages.
"""
import requests
from bs4 import BeautifulSoup
from typing import Dict, List
import logging
import time
from urllib.parse import urljoin, urlparse

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def scrape_page_content(url: str, timeout: int = 10) -> Dict[str, str]:
    """
    Scrape content from a single web page.
    
    Args:
        url (str): URL of the page to scrape
        timeout (int): Request timeout in seconds
        
    Returns:
        Dict[str, str]: Dictionary containing title, content, and metadata
    """
    try:
        logger.info(f"Scraping content from {url}")
        
        # Set headers to mimic a real browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title_tag = soup.find('title')
        title = title_tag.get_text().strip() if title_tag else "No Title"
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extract main content - try different selectors for main content
        main_content = soup.find('main') or \
                      soup.find('article') or \
                      soup.find('div', {'class': 'content'}) or \
                      soup.find('div', {'id': 'content'}) or \
                      soup.find('div', class_='post') or \
                      soup.find('div', class_='page-content') or \
                      soup.find('div', class_='entry-content') or \
                      soup.find('div', attrs={'role': 'main'}) or \
                      soup.body
        
        if main_content:
            # Get text content, removing extra whitespace
            content = ' '.join(main_content.get_text().split())
        else:
            # If no main content found, use the body or full text
            content = ' '.join(soup.get_text().split())
        
        # Limit content length if too long
        if len(content) > 10000:  # 10k characters max
            logger.info(f"Truncating content from {url} from {len(content)} to 10000 characters")
            content = content[:10000]
        
        # Extract other metadata if needed
        description_tag = soup.find('meta', attrs={'name': 'description'})
        description = description_tag.get('content', '') if description_tag else ''
        
        result = {
            'url': url,
            'title': title,
            'content': content,
            'description': description,
            'scraped_at': str(time.time())
        }
        
        logger.info(f"Successfully scraped content from {url} - Title: {title[:50]}...")
        return result
        
    except requests.RequestException as e:
        logger.error(f"Error requesting {url}: {e}")
        return {'url': url, 'error': str(e)}
    except Exception as e:
        logger.error(f"Error scraping {url}: {e}")
        return {'url': url, 'error': str(e)}


def scrape_multiple_pages(urls: List[str], delay: float = 1.0) -> List[Dict[str, str]]:
    """
    Scrape content from multiple web pages.
    
    Args:
        urls (List[str]): List of URLs to scrape
        delay (float): Delay between requests in seconds to be respectful to the server
        
    Returns:
        List[Dict[str, str]]: List of scraped content
    """
    results = []
    
    for i, url in enumerate(urls):
        logger.info(f"Scraping {i+1}/{len(urls)}: {url}")
        content = scrape_page_content(url)
        results.append(content)
        
        # Add delay between requests to be respectful to the server
        if delay > 0 and i < len(urls) - 1:
            time.sleep(delay)
    
    return results


def clean_content(text: str) -> str:
    """
    Clean and normalize scraped content.
    
    Args:
        text (str): Raw scraped text
        
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    cleaned = ' '.join(text.split())
    
    # Remove common website elements that might be scraped but aren't content
    # This is a simple approach - in practice, you might need more sophisticated cleaning
    lines = cleaned.split('. ')
    filtered_lines = [line for line in lines if len(line.strip()) > 10]  # Filter out very short lines
    cleaned = '. '.join(filtered_lines)
    
    return cleaned


if __name__ == "__main__":
    # Example usage
    test_urls = [
        "https://bushraturk.github.io/my-website/"
        # Add more URLs as needed for testing
    ]
    
    print("Scraping test URLs...")
    results = scrape_multiple_pages(test_urls, delay=0.5)
    
    for result in results:
        if 'error' not in result:
            print(f"Title: {result['title']}")
            print(f"Content length: {len(result['content'])} characters")
            print(f"URL: {result['url']}")
            print("---")
        else:
            print(f"Error scraping {result['url']}: {result['error']}")