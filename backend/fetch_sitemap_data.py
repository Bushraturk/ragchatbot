#!/usr/bin/env python3
"""
Script to fetch data from sitemap and save it for later use.
This script works independently of the Qdrant vector store.
"""

import os
import sys
import requests
from xml.etree import ElementTree as ET
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Any

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.sitemap_parser import parse_sitemap
from src.utils.web_scraper import scrape_multiple_pages, clean_content


def save_scraped_data_to_file(scraped_data: List[Dict[str, Any]], output_file: str):
    """Save scraped data to a JSON file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(scraped_data, f, ensure_ascii=False, indent=2)
    print(f"Scraped data saved to {output_file}")


def main():
    print("Starting sitemap data fetch process...")
    
    # The sitemap URL from the project
    sitemap_url = "https://bushraturk.github.io/my-website/sitemap.xml"
    
    print(f"Fetching sitemap from: {sitemap_url}")
    
    try:
        # Step 1: Parse sitemap to extract URLs
        urls = parse_sitemap(sitemap_url)
        print(f"Found {len(urls)} URLs in sitemap")
        
        if not urls:
            print("No URLs found in sitemap")
            return False
        
        # Step 2: Scrape content from URLs (with a delay to be respectful)
        print("Starting to scrape content from URLs...")
        scraped_data = scrape_multiple_pages(urls, delay=0.5)
        
        # Step 3: Filter out any failed scrapes
        successful_scrapes = [item for item in scraped_data if 'error' not in item]
        failed_scrapes = [item for item in scraped_data if 'error' in item]
        
        print(f"Successfully scraped {len(successful_scrapes)} pages")
        print(f"Failed to scrape {len(failed_scrapes)} pages")
        
        if failed_scrapes:
            print("Failed URLs:")
            for item in failed_scrapes[:5]:  # Show first 5 failures
                print(f"  - {item['url']}: {item.get('error', 'Unknown error')}")
        
        if successful_scrapes:
            # Step 4: Clean content
            for item in successful_scrapes:
                item['content'] = clean_content(item['content'])
            
            # Step 5: Save to file
            output_file = os.path.join(os.path.dirname(__file__), 'scraped_sitemap_data.json')
            save_scraped_data_to_file(successful_scrapes, output_file)
            
            # Also save a summary
            summary = {
                "sitemap_url": sitemap_url,
                "total_found_urls": len(urls),
                "successful_scrapes": len(successful_scrapes),
                "failed_scrapes": len(failed_scrapes),
                "scraped_at": time.time(),
                "data": successful_scrapes
            }
            
            summary_file = os.path.join(os.path.dirname(__file__), 'sitemap_summary.json')
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            
            print(f"Summary saved to {summary_file}")
            print("Sitemap data fetching completed successfully!")
            return True
        else:
            print("No successful scrapes to save")
            return False
            
    except Exception as e:
        print(f"Error during sitemap processing: {e}")
        return False


if __name__ == "__main__":
    success = main()
    if success:
        print("\nData has been fetched from the sitemap and saved to local files.")
        print("You can now use this data for your RAG system.")
    else:
        print("\nFailed to fetch data from sitemap.")