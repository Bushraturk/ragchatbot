"""
RAG Agent implementation
An agent that specializes in RAG (Retrieval Augmented Generation) operations
"""
from typing import List, Dict, Any, AsyncIterator
import asyncio
import uuid
from datetime import datetime

from src.core.agent_base import (
    Agent, Message, AgentEvent, AgentEventType, AgentContext
)
from src.services.rag_tool import RAGTool


class RAGAgent(Agent):
    """
    Agent specialized for RAG operations
    """
    
    def __init__(self, name: str = "RAG-Agent", system_prompt: str = None):
        super().__init__(
            name=name,
            system_prompt=system_prompt or (
                "You are a helpful assistant that answers questions based on provided context. "
                "Answer the user's question based ONLY on the information provided in the context. "
                "If the context does not contain relevant information to answer the question, "
                "please respond with 'Information not found in the provided documents'."
            )
        )
        
        # Add the RAG tool to the agent's toolkit
        self.add_tool(RAGTool())
    
    async def process(self, messages: List[Message], context: AgentContext) -> AsyncIterator[AgentEvent]:
        """
        Process messages using RAG capabilities
        """
        # Extract the latest user message (the one we need to respond to)
        if not messages:
            yield AgentEvent(
                type=AgentEventType.ERROR,
                data={"error": "No messages provided to process"}
            )
            return
        
        # Get the last user message
        last_user_message = None
        for msg in reversed(messages):
            if msg.role == "user":
                last_user_message = msg
                break
        
        if not last_user_message:
            yield AgentEvent(
                type=AgentEventType.ERROR,
                data={"error": "No user message to respond to"}
            )
            return
        
        # Determine mode based on context
        mode = context.agent_config.get("mode", "full_book")
        selected_text = context.agent_config.get("selected_text", None)
        
        # Find the RAG tool in our tools
        rag_tool = None
        for tool in self.tools:
            if isinstance(tool, RAGTool):
                rag_tool = tool
                break
                
        if not rag_tool:
            yield AgentEvent(
                type=AgentEventType.ERROR,
                data={"error": "RAG tool not found"}
            )
            return
        
        # Execute the RAG tool
        try:
            tool_params = {
                "query": last_user_message.content,
                "mode": mode,
                "selected_text": selected_text,
                "thread_id": context.thread_id
            }
            
            result = await rag_tool.execute(tool_params, context)
            
            if result.get("success"):
                # Yield the response
                yield AgentEvent(
                    type=AgentEventType.MESSAGE,
                    data={
                        "content": result["result"],
                        "references": result.get("references", []),
                        "tool_result": result
                    }
                )
            else:
                # Handle error case
                yield AgentEvent(
                    type=AgentEventType.ERROR,
                    data={"error": result.get("error", "Unknown error")}
                )
                
        except Exception as e:
            yield AgentEvent(
                type=AgentEventType.ERROR,
                data={"error": f"Error executing RAG tool: {str(e)}"}
            )