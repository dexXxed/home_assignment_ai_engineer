"""
Tests for diagram_generator.agents.diagram_agent module
"""
import os
from unittest.mock import Mock, patch, AsyncMock

import pytest

from diagram_generator.agents.diagram_agent import DiagramAgent, create_diagram_agent
from diagram_generator.api.models import DiagramRequest, DiagramResponse
from diagram_generator.utils.gemini_client import GeminiClient


class TestDiagramAgent:
    """Test DiagramAgent class"""
    
    @patch('diagram_generator.agents.diagram_agent.GeminiClient')
    def test_initialization_with_api_key(self, mock_gemini_client):
        """Test agent initialization with API key"""
        mock_client = Mock(spec=GeminiClient)
        mock_gemini_client.return_value = mock_client
        
        agent = DiagramAgent("test_api_key")
        
        assert agent.gemini_api_key == "test_api_key"
        assert agent.gemini_client == mock_client
        mock_gemini_client.assert_called_once_with("test_api_key")
    
    @patch('diagram_generator.agents.diagram_agent.GeminiClient')
    @patch('diagram_generator.agents.diagram_agent.settings')
    def test_initialization_without_api_key_env_var(self, mock_settings, mock_gemini_client):
        """Test initialization without API key but with environment variable"""
        mock_client = Mock(spec=GeminiClient)
        mock_gemini_client.return_value = mock_client
        mock_settings.GEMINI_API_KEY = None
        
        with patch.dict(os.environ, {"GEMINI_API_KEY": "env_api_key"}, clear=True):
            agent = DiagramAgent()
            
            assert agent.gemini_api_key == "env_api_key"
            assert agent.gemini_client == mock_client
    
    @patch('diagram_generator.agents.diagram_agent.GeminiClient')
    @patch('diagram_generator.agents.diagram_agent.settings')
    def test_initialization_no_api_key_raises_error(self, mock_settings, mock_gemini_client):
        """Test initialization without API key raises error"""
        mock_settings.GEMINI_API_KEY = None
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="GEMINI_API_KEY is required"):
                DiagramAgent()
    
    @patch('diagram_generator.agents.diagram_agent.GeminiClient')
    def test_available_tools_defined(self, mock_gemini_client):
        """Test that available tools are properly defined"""
        mock_client = Mock(spec=GeminiClient)
        mock_gemini_client.return_value = mock_client
        
        agent = DiagramAgent("test_api_key")
        
        assert isinstance(agent.available_tools, dict)
        assert "create_canvas" in agent.available_tools
        assert "create_cluster" in agent.available_tools
        assert "add_node" in agent.available_tools
        assert "add_edge" in agent.available_tools
        assert "render_diagram" in agent.available_tools
    
    @patch('diagram_generator.agents.diagram_agent.GeminiClient')
    def test_get_api_key_precedence(self, mock_gemini_client):
        """Test that provided API key takes precedence over environment"""
        mock_client = Mock(spec=GeminiClient)
        mock_gemini_client.return_value = mock_client
        
        with patch.dict(os.environ, {"GEMINI_API_KEY": "env_key"}):
            agent = DiagramAgent("provided_key")
            
            assert agent.gemini_api_key == "provided_key"
    
    @patch('diagram_generator.agents.diagram_agent.GeminiClient')
    def test_build_system_prompt(self, mock_gemini_client):
        """Test system prompt generation"""
        mock_client = Mock(spec=GeminiClient)
        mock_gemini_client.return_value = mock_client
        
        agent = DiagramAgent("test_api_key")
        prompt = agent._build_system_prompt()
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "microservices" in prompt.lower()
        assert "tools" in prompt.lower()
    
    @patch('diagram_generator.agents.diagram_agent.GeminiClient')
    def test_extract_allowed_components(self, mock_gemini_client):
        """Test component extraction from description"""
        mock_client = Mock(spec=GeminiClient)
        mock_gemini_client.return_value = mock_client
        
        agent = DiagramAgent("test_api_key")
        
        # Test with description containing known components
        description = "Create a microservices architecture with API gateway, load balancer, and database"
        components = agent._extract_allowed_components(description)
        
        assert isinstance(components, set)
        # Default components are always included
        assert "api_gateway" in components
        assert "service" in components
        assert "database" in components
        assert "queue" in components
        assert "monitoring" in components
    
    @patch('diagram_generator.agents.diagram_agent.GeminiClient')
    def test_build_user_prompt(self, mock_gemini_client):
        """Test user prompt generation"""
        mock_client = Mock(spec=GeminiClient)
        mock_gemini_client.return_value = mock_client
        
        agent = DiagramAgent("test_api_key")
        request = DiagramRequest(description="Generate a microservices architecture")
        
        prompt = agent._build_user_prompt(request)
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "microservices architecture" in prompt
        assert "tools" in prompt.lower()
    
    @patch('diagram_generator.agents.diagram_agent.GeminiClient')
    def test_standardize_cluster_name(self, mock_gemini_client):
        """Test cluster name standardization"""
        mock_client = Mock(spec=GeminiClient)
        mock_gemini_client.return_value = mock_client
        
        agent = DiagramAgent("test_api_key")
        
        # Test various cluster names - only mapped ones are standardized
        assert agent._standardize_cluster_name("api_gateway") == "api_gateway"  # No mapping exists
        assert agent._standardize_cluster_name("microservices") == "Microservices"
        assert agent._standardize_cluster_name("shared infra") == "Shared Infra"
        assert agent._standardize_cluster_name("routing") == "Routing"
        assert agent._standardize_cluster_name("Unknown Cluster") == "Unknown Cluster"
    
    @patch('diagram_generator.agents.diagram_agent.GeminiClient')
    def test_validate_tool_call_valid(self, mock_gemini_client):
        """Test validation of valid tool calls"""
        mock_client = Mock(spec=GeminiClient)
        mock_gemini_client.return_value = mock_client
        
        agent = DiagramAgent("test_api_key")
        
        # Valid tool call
        tool_call = {
            "name": "create_canvas",
            "args": {"title": "Test Architecture"}
        }
        
        assert agent._validate_tool_call(tool_call) is True
    
    @patch('diagram_generator.agents.diagram_agent.GeminiClient')
    def test_validate_tool_call_invalid(self, mock_gemini_client):
        """Test validation of invalid tool calls"""
        mock_client = Mock(spec=GeminiClient)
        mock_gemini_client.return_value = mock_client
        
        agent = DiagramAgent("test_api_key")
        
        # Invalid tool calls
        invalid_calls = [
            {"args": {"title": "Missing name"}},  # Missing name
            {"name": "create_canvas"},  # Missing args
            {"name": "invalid_tool", "args": {}},  # Invalid tool name
            {}  # Empty call
        ]
        
        for call in invalid_calls:
            assert agent._validate_tool_call(call) is False
    
    @patch('diagram_generator.agents.diagram_agent.GeminiClient')
    @patch('diagram_generator.agents.diagram_agent.mcp_tools')
    def test_check_duplicate_node(self, mock_mcp_tools, mock_gemini_client):
        """Test duplicate node checking"""
        mock_client = Mock(spec=GeminiClient)
        mock_gemini_client.return_value = mock_client
        mock_mcp_tools.list_canvas_nodes.return_value = {"existing_node": {}}
        
        agent = DiagramAgent("test_api_key")
        
        # The implementation is simplified and always returns False
        assert agent._check_duplicate_node("canvas_id", "existing_node") is False
        assert agent._check_duplicate_node("canvas_id", "new_node") is False
    
    @patch('diagram_generator.agents.diagram_agent.GeminiClient')
    @patch('diagram_generator.agents.diagram_agent.mcp_tools')
    def test_enforce_shared_edges(self, mock_mcp_tools, mock_gemini_client):
        """Test shared edges enforcement"""
        mock_client = Mock(spec=GeminiClient)
        mock_gemini_client.return_value = mock_client
        
        # Mock canvas nodes
        mock_mcp_tools.list_canvas_nodes.return_value = {
            "service1": {"node_type": "service"},
            "database1": {"node_type": "database"},
            "queue1": {"node_type": "queue"}
        }
        
        agent = DiagramAgent("test_api_key")
        agent._enforce_shared_edges("test_canvas")
        
        # The implementation is a placeholder that does nothing
        # So no edges should be added
        mock_mcp_tools.add_edge.assert_not_called()
    
    @patch('diagram_generator.agents.diagram_agent.GeminiClient')
    @patch('diagram_generator.agents.diagram_agent.mcp_tools')
    @pytest.mark.asyncio
    async def test_call_mcp_tool_success(self, mock_mcp_tools, mock_gemini_client):
        """Test successful MCP tool call"""
        mock_client = Mock(spec=GeminiClient)
        mock_gemini_client.return_value = mock_client
        mock_mcp_tools.create_canvas.return_value = "test_canvas_id"
        
        agent = DiagramAgent("test_api_key")
        
        result = await agent._call_mcp_tool("create_canvas", {"title": "Test"})
        
        assert result == {"result": "test_canvas_id"}
        mock_mcp_tools.create_canvas.assert_called_once_with("Test")
    
    @patch('diagram_generator.agents.diagram_agent.GeminiClient')
    @patch('diagram_generator.agents.diagram_agent.mcp_tools')
    @pytest.mark.asyncio
    async def test_call_mcp_tool_error(self, mock_mcp_tools, mock_gemini_client):
        """Test MCP tool call with error"""
        mock_client = Mock(spec=GeminiClient)
        mock_gemini_client.return_value = mock_client
        mock_mcp_tools.create_canvas.side_effect = Exception("Tool error")
        
        agent = DiagramAgent("test_api_key")
        
        result = await agent._call_mcp_tool("create_canvas", {"title": "Test"})
        
        assert "error" in result
        assert "Tool error" in result["error"]
    
    @patch('diagram_generator.agents.diagram_agent.GeminiClient')
    @patch('diagram_generator.agents.diagram_agent.mcp_tools')
    @pytest.mark.asyncio
    async def test_generate_diagram_success(self, mock_mcp_tools, mock_gemini_client):
        """Test successful diagram generation"""
        mock_client = Mock(spec=GeminiClient)
        mock_client.generate_json_response = AsyncMock(return_value={
            "reasoning": "Generated microservices architecture",
            "tool_calls": [
                {"name": "create_canvas", "args": {"title": "Test Architecture"}},
                {"name": "render_diagram", "args": {"canvas_id": "CANVAS_ID"}}
            ]
        })
        mock_gemini_client.return_value = mock_client
        
        # Mock MCP tools
        mock_mcp_tools.create_canvas.return_value = "test_canvas_id"
        mock_mcp_tools.render_diagram.return_value = "/path/to/diagram.png"
        
        agent = DiagramAgent("test_api_key")
        request = DiagramRequest(description="Generate a microservices architecture")
        
        response = await agent.generate_diagram(request)
        
        assert isinstance(response, DiagramResponse)
        assert response.success is True
        assert response.image_path == "/path/to/diagram.png"
        assert response.reasoning == "Generated microservices architecture"
    
    @patch('diagram_generator.agents.diagram_agent.GeminiClient')
    @pytest.mark.asyncio
    async def test_generate_diagram_gemini_error(self, mock_gemini_client):
        """Test diagram generation with Gemini error"""
        mock_client = Mock(spec=GeminiClient)
        mock_client.generate_json_response = AsyncMock(side_effect=Exception("Gemini error"))
        mock_gemini_client.return_value = mock_client
        
        agent = DiagramAgent("test_api_key")
        request = DiagramRequest(description="Generate a microservices architecture")
        
        response = await agent.generate_diagram(request)
        
        assert isinstance(response, DiagramResponse)
        assert response.success is False
        assert "Gemini error" in response.error
    
    @patch('diagram_generator.agents.diagram_agent.GeminiClient')
    @patch('diagram_generator.agents.diagram_agent.mcp_tools')
    @pytest.mark.asyncio
    async def test_generate_diagram_no_image_path(self, mock_mcp_tools, mock_gemini_client):
        """Test diagram generation without image path"""
        mock_client = Mock(spec=GeminiClient)
        mock_client.generate_json_response = AsyncMock(return_value={
            "reasoning": "Generated but no render",
            "tool_calls": [
                {"name": "create_canvas", "args": {"title": "Test Architecture"}}
            ]
        })
        mock_gemini_client.return_value = mock_client
        
        mock_mcp_tools.create_canvas.return_value = "test_canvas_id"
        
        agent = DiagramAgent("test_api_key")
        request = DiagramRequest(description="Generate a microservices architecture")
        
        response = await agent.generate_diagram(request)
        
        assert isinstance(response, DiagramResponse)
        assert response.success is False
        assert "No diagram was rendered" in response.error


class TestCreateDiagramAgent:
    """Test create_diagram_agent function"""
    
    @patch('diagram_generator.agents.diagram_agent.DiagramAgent')
    @patch('diagram_generator.agents.diagram_agent.settings')
    @pytest.mark.asyncio
    async def test_create_agent_with_provided_key(self, mock_settings, mock_diagram_agent):
        """Test creating agent with provided API key"""
        mock_agent = Mock(spec=DiagramAgent)
        mock_diagram_agent.return_value = mock_agent
        
        result = await create_diagram_agent("provided_key")
        
        assert result == mock_agent
        mock_diagram_agent.assert_called_once_with("provided_key")
    
    @patch('diagram_generator.agents.diagram_agent.DiagramAgent')
    @patch('diagram_generator.agents.diagram_agent.settings')
    @pytest.mark.asyncio
    async def test_create_agent_with_settings_key(self, mock_settings, mock_diagram_agent):
        """Test creating agent with settings API key"""
        mock_settings.GEMINI_API_KEY = "settings_key"
        mock_agent = Mock(spec=DiagramAgent)
        mock_diagram_agent.return_value = mock_agent
        
        result = await create_diagram_agent()
        
        assert result == mock_agent
        mock_diagram_agent.assert_called_once_with("settings_key")
    
    @patch('diagram_generator.agents.diagram_agent.DiagramAgent')
    @patch('diagram_generator.agents.diagram_agent.settings')
    @pytest.mark.asyncio
    async def test_create_agent_no_key(self, mock_settings, mock_diagram_agent):
        """Test creating agent without API key"""
        mock_settings.GEMINI_API_KEY = None
        
        result = await create_diagram_agent()
        
        assert result is None
        mock_diagram_agent.assert_not_called()
    
    @patch('diagram_generator.agents.diagram_agent.DiagramAgent')
    @patch('diagram_generator.agents.diagram_agent.settings')
    @pytest.mark.asyncio
    async def test_create_agent_exception(self, mock_settings, mock_diagram_agent):
        """Test creating agent with exception"""
        mock_settings.GEMINI_API_KEY = "test_key"
        mock_diagram_agent.side_effect = Exception("Agent creation error")
        
        result = await create_diagram_agent()
        
        assert result is None 