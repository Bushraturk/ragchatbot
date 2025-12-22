"""
Sitemap Embedding Pipeline

This script orchestrates the process of:
1. Parsing a sitemap.xml file
2. Scraping content from each URL
3. Generating embeddings using Cohere
4. Storing embeddings in Qdrant vector database
"""
import os
import sys
from typing import List, Dict, Any
import logging
import time
from tqdm import tqdm  # For progress tracking

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.sitemap_parser import parse_sitemap, filter_urls_by_domain
from utils.web_scraper import scrape_multiple_pages, clean_content
from services.document_service import DocumentService

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main(sitemap_url: str, delay: float = 1.0) -> bool:
    """
    Main function to run the sitemap embedding pipeline

    Args:
        sitemap_url: URL of the sitemap.xml file
        delay: Delay between scraping requests in seconds

    Returns:
        True if successful, False otherwise
    """
    start_time = time.time()
    logger.info(f"Starting sitemap embedding pipeline for: {sitemap_url}")

    try:
        # Step 1: Parse sitemap to extract URLs
        logger.info("Step 1: Parsing sitemap...")
        urls = parse_sitemap(sitemap_url)

        if not urls:
            logger.error("No URLs found in sitemap")
            return False

        logger.info(f"Found {len(urls)} URLs in sitemap")

        # Step 2: Scrape content from URLs with progress tracking
        logger.info("Step 2: Scraping content from URLs...")
        scraped_data = []
        failed_count = 0

        # Use tqdm for progress tracking during scraping
        for i, url in enumerate(tqdm(urls, desc="Scraping URLs", unit="url")):
            try:
                # Scrape single page with a shorter timeout
                from utils.web_scraper import scrape_page_content
                content = scrape_page_content(url)

                if 'error' not in content:
                    scraped_data.append(content)
                else:
                    failed_count += 1
                    logger.warning(f"Failed to scrape {url}: {content.get('error')}")

                # Add delay between requests to be respectful to the server
                if delay > 0 and i < len(urls) - 1:
                    time.sleep(delay)
            except Exception as e:
                failed_count += 1
                logger.error(f"Error scraping {url}: {e}")

        logger.info(f"Successfully scraped content from {len(scraped_data)} pages, {failed_count} failed")

        if not scraped_data:
            logger.error("No valid content scraped from any URLs")
            return False

        # Step 3: Clean the content
        logger.info("Step 3: Cleaning scraped content...")
        for item in scraped_data:
            item['content'] = clean_content(item['content'])

        # Step 4: Initialize document service and add content to vector store with progress tracking
        logger.info("Step 4: Adding content to vector store...")
        doc_service = DocumentService()

        success = doc_service.process_sitemap_content(scraped_data)

        elapsed_time = time.time() - start_time
        if success:
            logger.info(f"Sitemap embedding pipeline completed successfully in {elapsed_time:.2f}s!")
        else:
            logger.error(f"Sitemap embedding pipeline failed after {elapsed_time:.2f}s!")

        return success

    except Exception as e:
        elapsed_time = time.time() - start_time
        logger.error(f"Error in sitemap embedding pipeline after {elapsed_time:.2f}s: {e}")
        return False


def process_sitemap_with_filtering(sitemap_url: str, domain_filter: str = None, delay: float = 1.0) -> bool:
    """
    Process sitemap with optional domain filtering

    Args:
        sitemap_url: URL of the sitemap.xml file
        domain_filter: Optional domain to filter URLs by
        delay: Delay between scraping requests in seconds

    Returns:
        True if successful, False otherwise
    """
    start_time = time.time()
    logger.info(f"Starting sitemap embedding pipeline with domain filter: {domain_filter}")

    try:
        # Step 1: Parse sitemap to extract URLs
        logger.info("Step 1: Parsing sitemap...")
        urls = parse_sitemap(sitemap_url)

        # Step 2: Filter URLs by domain if specified
        if domain_filter:
            logger.info(f"Step 2: Filtering URLs by domain: {domain_filter}...")
            urls = filter_urls_by_domain(urls, domain_filter)

        if not urls:
            logger.error("No URLs found in sitemap after filtering")
            return False

        logger.info(f"Found {len(urls)} URLs after filtering")

        # Step 3: Scrape content from filtered URLs with progress tracking
        logger.info("Step 3: Scraping content from URLs...")
        scraped_data = []
        failed_count = 0

        # Use tqdm for progress tracking during scraping
        for i, url in enumerate(tqdm(urls, desc="Scraping URLs", unit="url")):
            try:
                # Scrape single page with a shorter timeout
                from utils.web_scraper import scrape_page_content
                content = scrape_page_content(url)

                if 'error' not in content:
                    scraped_data.append(content)
                else:
                    failed_count += 1
                    logger.warning(f"Failed to scrape {url}: {content.get('error')}")

                # Add delay between requests to be respectful to the server
                if delay > 0 and i < len(urls) - 1:
                    time.sleep(delay)
            except Exception as e:
                failed_count += 1
                logger.error(f"Error scraping {url}: {e}")

        logger.info(f"Successfully scraped content from {len(scraped_data)} pages, {failed_count} failed")

        if not scraped_data:
            logger.error("No valid content scraped from any URLs")
            return False

        # Step 4: Clean the content
        logger.info("Step 4: Cleaning scraped content...")
        for item in scraped_data:
            item['content'] = clean_content(item['content'])

        # Step 5: Initialize document service and add content to vector store with progress tracking
        logger.info("Step 5: Adding content to vector store...")
        doc_service = DocumentService()

        success = doc_service.process_sitemap_content(scraped_data)

        elapsed_time = time.time() - start_time
        if success:
            logger.info(f"Sitemap embedding pipeline with domain filtering completed successfully in {elapsed_time:.2f}s!")
        else:
            logger.error(f"Sitemap embedding pipeline with domain filtering failed after {elapsed_time:.2f}s!")

        return success

    except Exception as e:
        elapsed_time = time.time() - start_time
        logger.error(f"Error in sitemap embedding pipeline with domain filtering after {elapsed_time:.2f}s: {e}")
        return False


if __name__ == "__main__":
    # Example usage
    sitemap_url = "https://bushraturk.github.io/my-website/sitemap.xml"

    # Add domain filter if needed (optional)
    domain_filter = "bushraturk.github.io"  # Set to None to skip filtering

    # Run the pipeline
    if domain_filter:
        success = process_sitemap_with_filtering(sitemap_url, domain_filter)
    else:
        success = main(sitemap_url)

    if success:
        logger.info("Pipeline completed successfully!")
        sys.exit(0)
    else:
        logger.error("Pipeline failed!")
        sys.exit(1)