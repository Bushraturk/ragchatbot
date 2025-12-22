# Web Scraping & Sitemap Processing

## Overview
Is project mein website content ko scrape karke RAG system mein add kiya jata hai. Sitemap.xml se URLs extract hote hain, phir content scrape hota hai, aur finally embeddings generate hoke Qdrant mein store hoti hain.

## Pipeline Flow

```
Sitemap.xml
    |
    v
[1. Parse Sitemap] --> Extract URLs
    |
    v
[2. Scrape Pages] --> Extract Content
    |
    v
[3. Clean Content] --> Remove noise
    |
    v
[4. Generate Embeddings] --> Cohere
    |
    v
[5. Store in Qdrant] --> Vector DB
```

## Installation

```bash
pip install requests beautifulsoup4 lxml tqdm
```

## Implementation

### 1. Sitemap Parser
```python
# backend/src/utils/sitemap_parser.py

import requests
from xml.etree import ElementTree as ET
from typing import List

def parse_sitemap(sitemap_url: str) -> List[str]:
    """Parse sitemap.xml and extract all URLs"""
    response = requests.get(sitemap_url)
    root = ET.fromstring(response.content)

    # Handle namespace
    namespace = ""
    if root.tag.startswith('{'):
        namespace = root.tag.split('}')[0][1:]

    urls = []
    sitemap_tag = f"{{{namespace}}}" if namespace else ""

    # Find URL entries
    url_entries = root.findall(f'.//{sitemap_tag}url/{sitemap_tag}loc')
    if not url_entries:
        url_entries = root.findall('.//url/loc')

    urls = [entry.text for entry in url_entries if entry.text]

    return urls
```

### 2. Web Scraper
```python
# backend/src/utils/web_scraper.py

import requests
from bs4 import BeautifulSoup
from typing import Dict

def scrape_page_content(url: str, timeout: int = 10) -> Dict[str, str]:
    """Scrape content from a single web page"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    response = requests.get(url, headers=headers, timeout=timeout)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract title
    title_tag = soup.find('title')
    title = title_tag.get_text().strip() if title_tag else "No Title"

    # Remove scripts and styles
    for script in soup(["script", "style"]):
        script.decompose()

    # Extract main content
    main_content = (
        soup.find('main') or
        soup.find('article') or
        soup.find('div', {'class': 'content'}) or
        soup.body
    )

    content = ' '.join(main_content.get_text().split()) if main_content else ""

    # Limit content length
    if len(content) > 10000:
        content = content[:10000]

    return {
        'url': url,
        'title': title,
        'content': content
    }
```

### 3. Sitemap Embedder Pipeline
```python
# backend/src/utils/sitemap_embedder.py

from tqdm import tqdm
import time

def main(sitemap_url: str, delay: float = 1.0) -> bool:
    """Main sitemap embedding pipeline"""

    # Step 1: Parse sitemap
    urls = parse_sitemap(sitemap_url)
    print(f"Found {len(urls)} URLs")

    # Step 2: Scrape content with progress bar
    scraped_data = []
    for url in tqdm(urls, desc="Scraping"):
        content = scrape_page_content(url)
        if 'error' not in content:
            scraped_data.append(content)
        time.sleep(delay)  # Be respectful

    # Step 3: Clean content
    for item in scraped_data:
        item['content'] = clean_content(item['content'])

    # Step 4 & 5: Generate embeddings and store
    doc_service = DocumentService()
    doc_service.process_sitemap_content(scraped_data)

    return True
```

## Common Mistakes & Solutions

### Mistake 1: Blocked by Website
**Problem:** Website blocks scraper requests.

**Error:**
```
403 Forbidden
```

**Solution:** User-Agent header add karo:

```python
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

response = requests.get(url, headers=headers)
```

### Mistake 2: Rate Limiting / Too Fast
**Problem:** Server rate limit laga deta hai.

**Error:**
```
429 Too Many Requests
```

**Solution:** Delays add karo between requests:

```python
for i, url in enumerate(urls):
    content = scrape_page_content(url)
    scraped_data.append(content)

    # Wait between requests
    if i < len(urls) - 1:
        time.sleep(1.0)  # 1 second delay
```

### Mistake 3: Timeout Errors
**Problem:** Slow pages timeout ho jate hain.

**Solution:** Timeout handle karo:

```python
def scrape_page_content(url: str, timeout: int = 10) -> Dict:
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        # ... scrape logic
    except requests.Timeout:
        return {'url': url, 'error': 'Timeout'}
    except requests.RequestException as e:
        return {'url': url, 'error': str(e)}
```

### Mistake 4: Wrong Content Extracted
**Problem:** Navigation, footer, ads bhi scrape ho gaye.

**Solution:** Specific content selectors use karo:

```python
# Try multiple selectors for main content
main_content = (
    soup.find('main') or
    soup.find('article') or
    soup.find('div', class_='content') or
    soup.find('div', class_='post') or
    soup.find('div', class_='page-content') or
    soup.find('div', class_='entry-content') or
    soup.find('div', attrs={'role': 'main'}) or
    soup.body
)

# Remove unwanted elements
for element in soup(['nav', 'footer', 'aside', 'header', '.sidebar', '.ads']):
    element.decompose()
```

### Mistake 5: Encoding Issues
**Problem:** Non-ASCII characters cause errors.

**Error:**
```
UnicodeEncodeError: 'charmap' codec can't encode character
```

**Solution:** UTF-8 encoding use karo:

```python
# For Windows console
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# For file saving
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

### Mistake 6: Sitemap Namespace Issues
**Problem:** XML namespace se URLs nahi milte.

**Solution:** Namespace handle karo:

```python
root = ET.fromstring(response.content)

# Extract namespace from root tag
namespace = ""
if root.tag.startswith('{'):
    namespace = root.tag.split('}')[0][1:]

# Use namespace in search
sitemap_tag = f"{{{namespace}}}" if namespace else ""
url_entries = root.findall(f'.//{sitemap_tag}url/{sitemap_tag}loc')

# Fallback without namespace
if not url_entries:
    url_entries = root.findall('.//url/loc')
```

## Running the Pipeline

### Step 1: Fetch Sitemap Data
```bash
cd backend
python fetch_sitemap_data.py
```

### Step 2: Generate Embeddings
```bash
python generate_embeddings.py
```

### Or Combined Pipeline
```bash
python -m src.utils.sitemap_embedder
```

## Content Cleaning

```python
def clean_content(text: str) -> str:
    """Clean scraped content"""
    if not text:
        return ""

    # Remove extra whitespace
    cleaned = ' '.join(text.split())

    # Remove very short lines (navigation items)
    lines = cleaned.split('. ')
    filtered_lines = [line for line in lines if len(line.strip()) > 10]
    cleaned = '. '.join(filtered_lines)

    return cleaned
```

## Files in This Project

| File | Purpose |
|------|---------|
| `backend/src/utils/sitemap_parser.py` | Parse sitemap.xml |
| `backend/src/utils/web_scraper.py` | Scrape web pages |
| `backend/src/utils/sitemap_embedder.py` | Full pipeline |
| `backend/fetch_sitemap_data.py` | Fetch & save data |
| `backend/generate_embeddings.py` | Generate & store embeddings |
| `backend/scraped_sitemap_data.json` | Cached scraped data |

## Resources
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Requests Library](https://docs.python-requests.org/)
- [Sitemap Protocol](https://www.sitemaps.org/protocol.html)
