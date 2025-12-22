import google.generativeai as genai
from typing import List, Dict, Any
from backend.src.core.config import settings

class LLMService:
    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.llm_model)
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_DANGEROUS",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE",
            },
        ]

    def generate_response(self, query: str, context_chunks: List[Dict[str, Any]]) -> str:
        """
        Generate a response based on the query and provided context
        
        Args:
            query: The user's question/query
            context_chunks: List of context chunks to use for response generation
            
        Returns:
            Generated response string
        """
        # Combine context chunks into a single context string
        context_parts = []
        for chunk in context_chunks:
            content = chunk.get('content', '')
            if content:
                context_parts.append(f"Context: {content}")
        
        combined_context = "\n\n".join(context_parts)
        
        # Create a prompt that includes the context and query
        prompt = f"""
        Based on the following context, please answer the user's question. 
        If the context does not contain relevant information to answer the question, 
        please respond with "Information not found in the book".
        
        Context:
        {combined_context}
        
        Question: {query}
        
        Answer:
        """
        
        try:
            response = self.model.generate_content(
                prompt,
                safety_settings=self.safety_settings
            )
            return response.text if response.text else "Information not found in the book"
        except Exception as e:
            print(f"Error generating response with Gemini: {e}")
            return "Information not found in the book"

    def validate_response(self, response: str, context_chunks: List[Dict[str, Any]]) -> bool:
        """
        Validate that the response is based on the provided context
        This is a simple validation that checks if response contains information from context
        """
        if "Information not found in the book" in response:
            return True  # This is a valid response when no context is found
        
        # Simple check: see if the response contains key phrases from the context
        response_lower = response.lower()
        for chunk in context_chunks:
            content = chunk.get('content', '').lower()
            # Check if any significant word from context appears in response
            if len(content) > 10:  # Only check if context chunk is substantial
                context_words = content.split()
                for word in context_words[:10]:  # Check first 10 words as sample
                    if len(word) > 5 and word in response_lower:
                        return True
        
        # If no strong connection found, it may not be properly grounded in context
        print("Warning: Response may not be properly based on context")
        return False