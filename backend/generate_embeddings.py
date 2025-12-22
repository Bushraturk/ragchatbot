#!/usr/bin/env python3
"""
Script to generate embeddings from the sitemap data and save them to Qdrant.
"""

import os
import sys
import json
import uuid
import asyncio
from typing import List, Dict, Any

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.embedding_service import EmbeddingService
from src.core.vector_store import VectorStore


def load_sitemap_data():
    """Load the sitemap data that was previously scraped."""
    sitemap_file = os.path.join(os.path.dirname(__file__), 'scraped_sitemap_data.json')
    if os.path.exists(sitemap_file):
        with open(sitemap_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        print(f"Sitemap data file not found: {sitemap_file}")
        return []


async def process_sitemap_data_for_qdrant():
    """Process the sitemap data to generate embeddings and store in Qdrant."""
    print("Loading sitemap data...")
    sitemap_data = load_sitemap_data()
    
    if not sitemap_data:
        print("No sitemap data available to process")
        return False
    
    print(f"Loaded {len(sitemap_data)} items from sitemap data")
    
    # Initialize services
    print("Initializing embedding service...")
    embedding_service = EmbeddingService()
    
    print("Initializing vector store...")
    vector_store = VectorStore()
    
    # Process each item from the sitemap
    successful_count = 0
    failed_count = 0
    
    for i, item in enumerate(sitemap_data):
        print(f"Processing item {i+1}/{len(sitemap_data)}: {item.get('title', 'No Title')[:50]}...")
        
        try:
            # Combine title and content for better embedding
            text_to_embed = f"{item.get('title', '')}\n\n{item.get('content', '')}"
            
            # Generate embedding
            embedding = embedding_service.embed_text(text_to_embed, input_type="search_document")
            
            # Create a unique document ID
            doc_id = f"web_content_{uuid.uuid4().hex[:12]}"
            
            # Add to vector store
            vector_store.add_web_content(
                doc_id=doc_id,
                title=item.get('title', ''),
                content=item.get('content', ''),
                embedding=embedding,
                url=item.get('url', ''),
                scraped_at=item.get('scraped_at', ''),
                metadata={
                    'source_type': 'web_content',
                    'original_url': item.get('url', ''),
                    'title': item.get('title', '')
                }
            )
            
            successful_count += 1
            print(f"  ✓ Successfully processed: {item.get('title', '')[:50]}...")
            
        except Exception as e:
            failed_count += 1
            print(f"  ✗ Failed to process {item.get('url', '')}: {str(e)}")
    
    print(f"\nEmbedding process completed!")
    print(f"Successful: {successful_count}")
    print(f"Failed: {failed_count}")
    print(f"Total processed: {len(sitemap_data)}")
    
    return True


def main():
    print("Starting embedding process for sitemap data...")
    print("This will generate embeddings and save them to Qdrant.")
    
    # Run the async function
    success = asyncio.run(process_sitemap_data_for_qdrant())
    
    if success:
        print("\n✅ Embeddings generated and saved to Qdrant successfully!")
        print("You can now use the RAG system with the embedded sitemap data.")
    else:
        print("\n❌ Embedding process failed!")
    
    return success


if __name__ == "__main__":
    main()