# Agent System Implementation

## Overview

The RAG ChatKit Gemini system implements a custom agent-based architecture that follows the Agent SDK pattern. The agent system is responsible for processing user messages, retrieving relevant context, and generating appropriate responses using RAG methodology.

## Core Components

### Agent Base Classes (`src/core/agent_base.py`)

#### AgentEventType
Enum defining the types of events an agent can emit:
- `MESSAGE`: Regular message events
- `STATUS_UPDATE`: Status updates during processing
- `TOOL_CALL`: Tool execution events
- `ERROR`: Error events

#### AgentEvent
Data class representing an event emitted by an agent during processing:
```python
@dataclass
class AgentEvent:
    type: AgentEventType
    data: Dict[str, Any]
    timestamp: datetime = None
```

#### Message
Data class representing a message in the conversation:
```python
@dataclass
class Message:
    id: str
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: datetime = None
```

#### AgentContext
Container for agent operation context:
```python
@dataclass
class AgentContext:
    thread_id: str
    session_metadata: Dict[str, Any]
    agent_config: Dict[str, Any]
    tools: List['Tool']
```

#### Tool (Abstract Base Class)
Interface for tools that can be used by agents:
```python
class Tool(ABC):
    @abstractmethod
    async def execute(self, parameters: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        pass
```

#### Agent (Abstract Base Class)
Base class for agents that can process conversations:
```python
class Agent(ABC):
    def __init__(self, name: str, system_prompt: str = ""):
        self.name = name
        self.system_prompt = system_prompt
        self.tools: List[Tool] = []

    def add_tool(self, tool: Tool): ...

    @abstractmethod
    async def process(self, messages: List[Message], context: AgentContext) -> AsyncIterator[AgentEvent]:
        pass
```

### RAG Tool Implementation (`src/services/rag_tool.py`)

The `RAGTool` extends the `Tool` base class and provides RAG capabilities to agents:

```python
class RAGTool(Tool):
    def __init__(self):
        self.rag_service = RAGService()

    async def execute(self, parameters: Dict[str, Any], context: AgentContext) -> Dict[str, Any]:
        # Execute RAG operations based on parameters:
        # - query: The user's query
        # - mode: Either 'full_book' or 'selected_text'
        # - selected_text: Text to use in selected_text mode (optional)
        # - thread_id: The conversation thread ID
```

### RAG Agent Implementation (`src/agents/rag_agent.py`)

The `RAGAgent` specializes in RAG operations and uses the `RAGTool`:

```python
class RAGAgent(Agent):
    def __init__(self, name: str = "RAG-Agent", system_prompt: str = None):
        # Specialized agent with RAG capabilities
        super().__init__(
            name=name,
            system_prompt=system_prompt or (
                "You are a helpful assistant that answers questions based on provided context. "
                "Answer the user's question based ONLY on the information provided in the context. "
                "If the context does not contain relevant information to answer the question, "
                "please respond with 'Information not found in the provided documents'."
            )
        )
        self.add_tool(RAGTool())  # Add RAG tool to agent's toolkit

    async def process(self, messages: List[Message], context: AgentContext) -> AsyncIterator[AgentEvent]:
        # Process messages using RAG capabilities
        # Extract latest user message and run it through RAG pipeline
        # Yield streaming events during processing
```

## Agent Flow in the System

### Thread Creation and Management
1. When a request comes to `/chatkit`, the `AgentChatKitServer` creates an `AgentContext`
2. The context includes thread information, configuration (mode, selected_text), and tools

### Message Processing
1. The `RAGAgent.process()` method receives the conversation history
2. It identifies the latest user message to respond to
3. The agent configures the RAG tool with the appropriate mode and selected text
4. The RAG tool retrieves relevant context from the vector store or uses selected text
5. The Gemini model generates a response based on the context
6. The response is streamed back to the client via SSE

### Context Management
- The agent processes the entire thread history to maintain conversation context
- Mode can be set to 'full_book' (searches vector store) or 'selected_text' (uses provided text)
- Selected text is passed through the agent context when in selected_text mode

## Integration with Backend API

The `AgentChatKitServer` in `main.py` acts as the integration layer between the FastAPI endpoints and the agent system:

```python
class AgentChatKitServer:
    def __init__(self, data_store: Store):
        self.store = data_store
        self.rag_agent = RAGAgent(name="RAG-Agent")

    async def respond(self, thread: ThreadMetadata, input_item: ThreadItem, request_context: Dict) -> AsyncIterator:
        # Convert ThreadItems to Messages for the agent
        # Create agent context with proper configuration
        # Process conversation with agent
        # Stream response back to client
```

## Configuration Options

The agent behavior can be customized through the `AgentContext`:

- `mode`: Either 'full_book' or 'selected_text'
- `selected_text`: Text to use as context in selected_text mode
- `thread_id`: Thread identifier for conversation history
- `session_metadata`: Additional metadata about the session

## Error Handling

The agent system includes comprehensive error handling:
- Network errors during tool execution
- Invalid query parameters
- Vector store connectivity issues
- LLM service errors
- Database operation failures

Error events are properly formatted and streamed back to clients in the SSE format.

## Extensibility

The agent system is designed for extensibility:
- Additional tools can be added to agents using `add_tool()`
- New agent types can be created by extending the `Agent` base class
- Tool implementations can be modified to support different retrieval strategies
- Context information can be extended for additional functionality