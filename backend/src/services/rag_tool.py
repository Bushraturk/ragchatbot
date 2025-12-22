"""
RAG Tool for Agents

This module provides a custom tool that agents can use to retrieve information
from the vector store containing sitemap data.
"""

import os
import sys
from typing import Dict, List, Any, Optional
import logging

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pydantic import BaseModel, Field
from src.core.vector_store import vector_store
from src.core.config import settings
from src.services.embedding_service import EmbeddingService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGQueryToolInput(BaseModel):
    """Input for the RAG Query Tool."""
    query: str = Field(..., description="The query to search for in the knowledge base")
    limit: int = Field(default=5, description="Maximum number of results to return")


class RAGQueryTool:
    """Tool for querying the RAG system to retrieve relevant information from the vector store."""
    
    def __init__(self):
        self.name = "rag_query"
        self.description = "Retrieve relevant information from the knowledge base based on a query. The knowledge base contains information from the Physical AI & Robotics course website."
        self.vector_store = vector_store
        self.embedding_service = EmbeddingService()
    
    def _get_vector_store_results(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get results from the vector store based on the query.
        
        Args:
            query: The query string to search for
            limit: Maximum number of results to return
            
        Returns:
            List of dictionaries containing search results
        """
        try:
            # Initialize vector store if needed
            self.vector_store._ensure_initialized()
            
            # Generate embedding for the query
            query_embedding = self.embedding_service.embed_text(query, input_type="search_query")
            
            # Search the vector store
            results = self.vector_store.search(query_embedding=query_embedding, limit=limit)
            
            return results
            
        except Exception as e:
            logger.error(f"Error querying vector store: {e}")
            return []
    
    def run(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """
        Execute the RAG query tool.
        
        Args:
            query: The query string to search for
            limit: Maximum number of results to return (default: 5)
            
        Returns:
            Dictionary containing the search results
        """
        logger.info(f"Running RAG query: {query}")
        
        # Get results from vector store
        results = self._get_vector_store_results(query, limit)
        
        if not results:
            logger.info("No results found in vector store")
            return {
                "query": query,
                "results_found": False,
                "message": "No relevant information found in the knowledge base.",
                "results": []
            }
        
        logger.info(f"Found {len(results)} results for query: {query}")
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "content": result.get('content', ''),
                "similarity_score": result.get('similarity_score', 0.0),
                "metadata": result.get('metadata', {}),
                "id": result.get('id', '')
            })
        
        return {
            "query": query,
            "results_found": True,
            "message": f"Found {len(formatted_results)} relevant results.",
            "results": formatted_results
        }
    
    def __call__(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Callable interface for the tool.
        
        Args:
            input_data: Dictionary containing 'query' and optional 'limit'
            
        Returns:
            Dictionary containing the search results
        """
        query = input_data.get('query', '')
        limit = input_data.get('limit', 5)
        
        if not query:
            return {
                "query": query,
                "results_found": False,
                "message": "No query provided.",
                "results": []
            }
        
        return self.run(query, limit)


def create_rag_tool():
    """Factory function to create an instance of the RAG query tool."""
    return RAGQueryTool()


# Example usage
if __name__ == "__main__":
    # Create the RAG tool
    rag_tool = create_rag_tool()
    
    # Example query
    query_input = {
        "query": "What is the Physical AI & Robotics course about?",
        "limit": 3
    }
    
    # Run the tool
    result = rag_tool(query_input)
    
    print("RAG Tool Result:")
    print(f"Query: {result['query']}")
    print(f"Results found: {result['results_found']}")
    print(f"Message: {result['message']}")
    
    if result['results_found']:
        for i, res in enumerate(result['results']):
            print(f"\nResult {i+1}:")
            print(f"  Content: {res['content'][:200]}...")
            print(f"  Similarity: {res['similarity_score']}")
            print(f"  Metadata: {res['metadata']}")