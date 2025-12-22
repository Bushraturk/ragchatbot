"""
Sitemap Parser Module

This module provides functionality to parse XML sitemaps and extract URLs.
"""
import requests
from xml.etree import ElementTree as ET
from typing import List
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_sitemap(sitemap_url: str) -> List[str]:
    """
    Parse an XML sitemap and extract all URLs.
    
    Args:
        sitemap_url (str): URL of the sitemap.xml file
        
    Returns:
        List[str]: List of URLs extracted from the sitemap
    """
    try:
        logger.info(f"Fetching sitemap from {sitemap_url}")
        response = requests.get(sitemap_url)
        response.raise_for_status()
        
        # Parse the XML content
        root = ET.fromstring(response.content)
        
        # Handle both regular sitemaps and sitemap indexes
        urls = []
        
        # Define namespace map if exists
        namespaces = {}
        if root.tag.startswith('{'):
            # Extract namespace from root tag
            namespace = root.tag.split('}')[0][1:]
            namespaces['ns'] = namespace
        
        # Check if this is a sitemap index (contains sitemap entries) or a regular sitemap (contains URL entries)
        sitemap_tag = f"{{{namespace}}}" if namespace else ""
        
        # Try both formats
        url_entries = root.findall(f'.//{sitemap_tag}url/{sitemap_tag}loc')
        if not url_entries:
            # Try without namespace prefix
            url_entries = root.findall('.//url/loc')
        
        if url_entries:
            # This is a regular sitemap with URLs
            urls = [entry.text for entry in url_entries if entry.text]
        else:
            # Try to parse as sitemap index
            sitemap_entries = root.findall(f'.//{sitemap_tag}sitemap/{sitemap_tag}loc')
            if not sitemap_entries:
                sitemap_entries = root.findall('.//sitemap/loc')
            
            if sitemap_entries:
                # This is a sitemap index, need to fetch individual sitemaps
                for entry in sitemap_entries:
                    if entry.text:
                        logger.info(f"Found nested sitemap: {entry.text}")
                        urls.extend(parse_sitemap(entry.text))
        
        logger.info(f"Extracted {len(urls)} URLs from sitemap")
        return urls
        
    except requests.RequestException as e:
        logger.error(f"Error fetching sitemap: {e}")
        raise
    except ET.ParseError as e:
        logger.error(f"Error parsing sitemap XML: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error parsing sitemap: {e}")
        raise


def filter_urls_by_domain(urls: List[str], domain: str = None) -> List[str]:
    """
    Filter URLs to only include those from a specific domain (if provided).
    
    Args:
        urls (List[str]): List of URLs to filter
        domain (str): Domain to filter by (optional)
        
    Returns:
        List[str]: Filtered list of URLs
    """
    if not domain:
        return urls
    
    filtered_urls = []
    for url in urls:
        if domain in url:
            filtered_urls.append(url)
    
    logger.info(f"Filtered URLs: {len(filtered_urls)} from domain {domain}")
    return filtered_urls


if __name__ == "__main__":
    # Example usage
    sitemap_url = "https://bushraturk.github.io/my-website/sitemap.xml"
    urls = parse_sitemap(sitemap_url)
    
    print(f"Found {len(urls)} URLs in sitemap:")
    for i, url in enumerate(urls[:10]):  # Print first 10 URLs
        print(f"{i+1}. {url}")
    
    if len(urls) > 10:
        print(f"... and {len(urls) - 10} more URLs")