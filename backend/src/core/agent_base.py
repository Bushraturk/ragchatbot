"""
Base classes for implementing agent-based systems
This serves as a foundation for the Agent SDK functionality
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, AsyncIterator
from dataclasses import dataclass
from enum import Enum
import asyncio
import uuid
from datetime import datetime


class AgentEventType(Enum):
    """Types of events an agent can emit"""
    MESSAGE = "message"
    STATUS_UPDATE = "status_update"
    TOOL_CALL = "tool_call"
    ERROR = "error"


@dataclass
class AgentEvent:
    """Event emitted by an agent during processing"""
    type: AgentEventType
    data: Dict[str, Any]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class Message:
    """Represents a message in the conversation"""
    id: str
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class AgentContext:
    """Context for agent operations"""
    thread_id: str
    session_metadata: Dict[str, Any]
    agent_config: Dict[str, Any]
    tools: List['Tool']
    

class Tool(ABC):
    """Abstract base class for tools that can be used by agents"""
    
    @abstractmethod
    async def execute(self, parameters: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        """Execute the tool with given parameters"""
        pass


class Agent(ABC):
    """Abstract base class for an agent that can process conversations"""
    
    def __init__(self, name: str, system_prompt: str = ""):
        self.name = name
        self.system_prompt = system_prompt
        self.tools: List[Tool] = []
        
    def add_tool(self, tool: Tool):
        """Add a tool to the agent's toolkit"""
        self.tools.append(tool)
        
    @abstractmethod
    async def process(self, messages: List[Message], context: AgentContext) -> AsyncIterator[AgentEvent]:
        """Process a list of messages and return streaming events"""
        pass