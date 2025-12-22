# Sitemap Embedding Pipeline

This package provides functionality to extract content from a sitemap.xml file, scrape web pages, generate embeddings using Cohere, and store them in Qdrant vector database for use in your RAG system.

## Overview

This pipeline allows you to:
- Parse sitemap.xml files to extract URLs
- Scrape content from the extracted URLs
- Generate embeddings using Cohere
- Store embeddings in Qdrant vector database
- Integrate with your existing RAG system

## Prerequisites

Before using this pipeline, ensure you have:

1. **Cohere API Key** - Get one from [Cohere](https://cohere.com/)
2. **Qdrant Cloud Instance** - Set up at [Qdrant Cloud](https://cloud.qdrant.io/)
3. **Git** - For cloning the repository
4. **Python 3.11** or higher

## Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ragchatboot/backend
```

### 2. Install Dependencies

```bash
pip install -r requirements_sitemap.txt
```

### 3. Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your actual API keys:
   ```bash
   # Qdrant Vector Database
   QDRANT_URL=your_actual_qdrant_cloud_url
   QDRANT_API_KEY=your_actual_qdrant_api_key

   # Cohere API
   COHERE_API_KEY=your_actual_cohere_api_key
   ```

### 4. Verify Setup

Run the following command to test your setup:

```bash
python -c "import cohere; import qdrant_client; print('Dependencies installed successfully')"
```

## Quick Start

### 1. Run the Sitemap Embedding Pipeline

```bash
cd src/utils
python sitemap_embedder.py
```

This will:
1. Parse the sitemap at `https://bushraturk.github.io/my-website/sitemap.xml` (configured in the script)
2. Scrape content from each URL
3. Generate embeddings using Cohere
4. Store embeddings in Qdrant vector database

### 2. Customize for Your Sitemap

To use with your own sitemap, edit the `sitemap_embedder.py` file:

```python
# Change this line to your sitemap URL
sitemap_url = "https://your-website.com/sitemap.xml"
```

## Detailed Usage

### Running the Pipeline with Options

The pipeline includes filtering by domain and customizable delay between requests:

```python
from sitemap_embedder import process_sitemap_with_filtering

# Run with domain filtering and custom delay
success = process_sitemap_with_filtering(
    sitemap_url="https://bushraturk.github.io/my-website/sitemap.xml",
    domain_filter="bushraturk.github.io",  # Only process URLs from this domain
    delay=1.5  # Wait 1.5 seconds between requests
)
```

### Using Individual Components

#### 1. Parse Sitemap Only

```python
from utils.sitemap_parser import parse_sitemap

urls = parse_sitemap("https://bushraturk.github.io/my-website/sitemap.xml")
print(f"Found {len(urls)} URLs")
```

#### 2. Scrape Content from URLs

```python
from utils.web_scraper import scrape_multiple_pages

urls = ["https://example.com/page1", "https://example.com/page2"]
scraped_data = scrape_multiple_pages(urls, delay=1.0)
```

#### 3. Add Content Directly to Vector Store

```python
from services.document_service import DocumentService

doc_service = DocumentService()
success = doc_service.add_web_content(
    title="Page Title",
    content="Page content here...",
    url="https://example.com/page",
    scraped_at="timestamp"
)
```

## Configuration

### Environment Variables

- `QDRANT_URL`: Your Qdrant Cloud instance URL
- `QDRANT_API_KEY`: Your Qdrant API key
- `COHERE_API_KEY`: Your Cohere API key

### Pipeline Settings

- **Scraping delay**: Default is 1 second between requests to be respectful to the server
- **Content chunk size**: Default is 1000 characters per chunk
- **Embedding model**: Using Cohere's embed-english-v3.0 model

## Integration with RAG System

Once content is embedded into Qdrant, it can be used in your RAG system through the same retrieval mechanisms that handle documents. The embedded web content will be stored in the `web_content` collection in Qdrant with metadata that includes the source URL and title.

## Troubleshooting

### Common Issues

1. **API Key Issues**
   - Verify your API keys are correctly set in the `.env` file
   - Check that the API keys have the necessary permissions

2. **Sitemap Parsing Issues**
   - Ensure the sitemap URL is accessible
   - Check that the sitemap is in valid XML format

3. **Rate Limiting**
   - If you encounter rate limiting, increase the delay between requests
   - Some websites have stricter rate limits than others

4. **Memory Issues**
   - For very large sitemaps, consider processing in smaller batches
   - Monitor memory usage during the embedding process

### Error Logs

The pipeline logs all activities to help with debugging. Check the logs if you encounter issues:

```
[timestamp] - sitemap_embedder - INFO - Starting sitemap embedding pipeline for: [URL]
[timestamp] - sitemap_embedder - INFO - Found [N] URLs in sitemap
[timestamp] - sitemap_embedder - INFO - Successfully scraped content from [N] pages
[timestamp] - sitemap_embedder - INFO - Sitemap embedding pipeline completed successfully!
```

## Security Notes

- Keep your API keys secure and never commit them to version control
- The pipeline includes appropriate delays to be respectful to web servers
- Be mindful of robots.txt files and website terms of service when scraping

## Additional Resources

- [Cohere Embeddings Documentation](https://docs.cohere.com/docs/embeddings)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Beautiful Soup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

## Support

If you encounter issues or have questions about the sitemap embedding pipeline, please open an issue in the repository.