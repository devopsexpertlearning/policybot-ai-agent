"""
Unit tests for agent tools.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.agents.tools import Tool, ToolExecutor, calculate, search_documents, TOOLS


@pytest.mark.unit
class TestTools:
    """Test individual tools and executor."""
    
    @pytest.mark.asyncio
    async def test_calculate_valid(self):
        """Test valid calculation."""
        result = await calculate("2 + 2")
        assert result["result"] == 4
        assert "error" not in result
        
    @pytest.mark.asyncio
    async def test_calculate_invalid(self):
        """Test invalid calculation."""
        result = await calculate("2 + invalid")
        assert "error" in result
        
    @pytest.mark.asyncio
    async def test_calculate_security(self):
        """Test calculation security check."""
        result = await calculate("import os")
        assert "error" in result
        
    @pytest.mark.asyncio
    async def test_search_documents(self):
        """Test document search tool."""
        with patch('app.agents.tools.retriever') as mock_retriever:
            mock_retriever.retrieve = AsyncMock(return_value=[{"content": "test"}])
            mock_retriever.format_sources = Mock(return_value=["test.txt"])
            
            result = await search_documents(query="test", top_k=2)
            
            assert "documents" in result
            assert "sources" in result
            assert result["count"] == 1
            mock_retriever.retrieve.assert_called_once_with(query="test", top_k=2)

    @pytest.mark.asyncio
    async def test_tool_execution(self):
        """Test tool executor runs tools correctly."""
        executor = ToolExecutor()
        
        # Test calculate execution
        result = await executor.execute_tool("calculate", expression="5 * 5")
        assert result["result"] == 25
        
    def test_tool_registry(self):
        """Test tool registry structure."""
        assert "search_documents" in TOOLS
        assert "calculate" in TOOLS
        assert isinstance(TOOLS["calculate"], Tool)
        
    def test_get_tool_descriptions(self):
        """Test tool descriptions generation."""
        executor = ToolExecutor()
        descriptions = executor.get_tool_descriptions()
        
        assert len(descriptions) == len(TOOLS)
        assert all("name" in d for d in descriptions)
        assert all("description" in d for d in descriptions)
        assert all("parameters" in d for d in descriptions)

    @pytest.mark.asyncio
    async def test_execute_unknown_tool(self):
        """Test executing non-existent tool."""
        executor = ToolExecutor()
        with pytest.raises(ValueError, match="Unknown tool"):
            await executor.execute_tool("unknown_tool")
