"""
Tool definitions and execution for the AI agent.
"""

from typing import Dict, Any, List, Callable, Optional
import logging

from app.rag.retriever import retriever

logger = logging.getLogger(__name__)


class Tool:
    """Tool definition."""
    
    def __init__(
        self,
        name: str,
        description: str,
        function: Callable,
        parameters: Dict[str, Any]
    ):
        """Initialize tool."""
        self.name = name
        self.description = description
        self.function = function
        self.parameters = parameters
    
    async def execute(self, **kwargs) -> Any:
        """Execute the tool."""
        try:
            return await self.function(**kwargs)
        except Exception as e:
            logger.error(f"Error executing tool {self.name}: {e}")
            raise


# Tool implementations
async def search_documents(query: str, top_k: int = 3) -> Dict[str, Any]:
    """
    Search company policy documents.
    
    Args:
        query: Search query
        top_k: Number of documents to retrieve
        
    Returns:
        Retrieved documents
    """
    logger.info(f"Tool 'search_documents' called with query: {query}")
    
    documents = await retriever.retrieve(query=query, top_k=top_k)
    sources = retriever.format_sources(documents)
    
    return {
        "documents": documents,
        "sources": sources,
        "count": len(documents)
    }


async def calculate(expression: str) -> Dict[str, Any]:
    """
    Perform simple calculations.
    
    Args:
        expression: Mathematical expression
        
    Returns:
        Calculation result
    """
    logger.info(f"Tool 'calculate' called with expression: {expression}")
    
    try:
        # Safe evaluation (only allow basic math)
        allowed_chars = set("0123456789+-*/(). ")
        if not all(c in allowed_chars for c in expression):
            return {
                "error": "Invalid expression. Only basic math operations allowed."
            }
        
        result = eval(expression)
        return {
            "result": result,
            "expression": expression
        }
    except Exception as e:
        return {
            "error": f"Calculation error: {str(e)}"
        }


# Tool registry
TOOLS: Dict[str, Tool] = {
    "search_documents": Tool(
        name="search_documents",
        description="Search company policy documents for relevant information",
        function=search_documents,
        parameters={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                },
                "top_k": {
                    "type": "integer",
                    "description": "Number of documents to retrieve (default: 3)"
                }
            },
            "required": ["query"]
        }
    ),
    "calculate": Tool(
        name="calculate",
        description="Perform simple mathematical calculations",
        function=calculate,
        parameters={
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Mathematical expression to evaluate"
                }
            },
            "required": ["expression"]
        }
    )
}


class ToolExecutor:
    """Execute tools based on agent decisions."""
    
    def __init__(self):
        """Initialize tool executor."""
        self.tools = TOOLS
    
    async def execute_tool(
        self,
        tool_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute a tool by name.
        
        Args:
            tool_name: Name of the tool
            **kwargs: Tool parameters
            
        Returns:
            Tool execution result
        """
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        tool = self.tools[tool_name]
        logger.info(f"Executing tool: {tool_name}")
        
        result = await tool.execute(**kwargs)
        return result
    
    def get_tool_descriptions(self) -> List[Dict[str, Any]]:
        """Get descriptions of all available tools."""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters
            }
            for tool in self.tools.values()
        ]
    
    def get_tool_names(self) -> List[str]:
        """Get names of all available tools."""
        return list(self.tools.keys())


# Global tool executor
tool_executor = ToolExecutor()
