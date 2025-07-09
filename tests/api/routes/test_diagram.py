"""
Tests for diagram_generator.api.routes.diagram module
"""
import tempfile
from unittest.mock import Mock, patch, AsyncMock

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from diagram_generator.api.routes.diagram import router, get_agent
from diagram_generator.agents.diagram_agent import DiagramAgent
from diagram_generator.api.models import DiagramRequest, DiagramResponse


@pytest.fixture(autouse=True)
def clear_agent_cache():
    """Clear the cached agent instance before each test"""
    import diagram_generator.api.routes.diagram as diagram_module
    diagram_module._agent_instance = None
    yield
    diagram_module._agent_instance = None


@pytest.fixture
def test_client():
    """Create a test client for the diagram router"""
    from fastapi import FastAPI
    
    app = FastAPI()
    app.include_router(router)
    
    return TestClient(app)


@pytest.fixture
def mock_agent():
    """Create a mock diagram agent"""
    agent = Mock(spec=DiagramAgent)
    agent.generate_diagram = AsyncMock()
    return agent


@pytest.fixture
def mock_successful_response():
    """Create a mock successful diagram response"""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp.write(b"fake image data")
        tmp_path = tmp.name
    
    return DiagramResponse(
        success=True,
        canvas_id="test_canvas_123",
        image_path=tmp_path,
        reasoning="Generated test diagram successfully"
    )


@pytest.fixture
def mock_failed_response():
    """Create a mock failed diagram response"""
    return DiagramResponse(
        success=False,
        error="Failed to generate diagram",
        reasoning="Error occurred during generation"
    )


class TestGetAgent:
    """Test get_agent function"""
    
    @patch('diagram_generator.api.routes.diagram.create_diagram_agent')
    @patch('diagram_generator.api.routes.diagram.settings')
    @pytest.mark.asyncio
    async def test_get_agent_success(self, mock_settings, mock_create_agent):
        """Test successful agent creation"""
        mock_settings.GEMINI_API_KEY = "test_key"
        mock_agent = Mock(spec=DiagramAgent)
        mock_create_agent.return_value = mock_agent
        
        agent = await get_agent()
        
        assert agent == mock_agent
        mock_create_agent.assert_called_once()
    
    @patch('diagram_generator.api.routes.diagram.create_diagram_agent')
    @patch('diagram_generator.api.routes.diagram.settings')
    @pytest.mark.asyncio
    async def test_get_agent_failure(self, mock_settings, mock_create_agent):
        """Test agent creation failure"""
        mock_settings.GEMINI_API_KEY = "test_key"
        mock_create_agent.return_value = None
        
        with pytest.raises(HTTPException):  # Should raise HTTPException
            await get_agent()
    
    @patch('diagram_generator.api.routes.diagram.create_diagram_agent')
    @patch('diagram_generator.api.routes.diagram.settings')
    @pytest.mark.asyncio
    async def test_get_agent_exception(self, mock_settings, mock_create_agent):
        """Test agent creation with exception"""
        mock_settings.GEMINI_API_KEY = "test_key"
        mock_create_agent.side_effect = Exception("Agent creation failed")
        
        with pytest.raises(Exception):  # Should raise the original exception
            await get_agent()
    
    @patch('diagram_generator.api.routes.diagram.create_diagram_agent')
    @patch('diagram_generator.api.routes.diagram.settings')
    @pytest.mark.asyncio
    async def test_get_agent_caching(self, mock_settings, mock_create_agent):
        """Test agent instance caching"""
        mock_settings.GEMINI_API_KEY = "test_key"
        mock_agent = Mock(spec=DiagramAgent)
        mock_create_agent.return_value = mock_agent
        
        # First call should create agent
        agent1 = await get_agent()
        
        # Second call should return cached agent
        agent2 = await get_agent()
        
        assert agent1 == agent2
        mock_create_agent.assert_called_once()  # Should only be called once


class TestGenerateDiagramRoute:
    """Test /generate-diagram route"""
    
    @patch('diagram_generator.api.routes.diagram.get_agent')
    def test_generate_diagram_success(self, mock_get_agent, test_client, mock_agent, mock_successful_response):
        """Test successful diagram generation"""
        mock_get_agent.return_value = mock_agent
        mock_agent.generate_diagram.return_value = mock_successful_response
        
        response = test_client.post(
            "/generate-diagram",
            data={"description": "Generate a microservices architecture"}
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"
        assert len(response.content) > 0
    
    @patch('diagram_generator.api.routes.diagram.get_agent')
    def test_generate_diagram_agent_failure(self, mock_get_agent, test_client, mock_agent, mock_failed_response):
        """Test diagram generation with agent failure"""
        mock_get_agent.return_value = mock_agent
        mock_agent.generate_diagram.return_value = mock_failed_response
        
        response = test_client.post(
            "/generate-diagram",
            data={"description": "Generate a microservices architecture"}
        )
        
        assert response.status_code == 500
        assert "Failed to generate diagram" in response.json()["detail"]
    
    @patch('diagram_generator.api.routes.diagram.get_agent')
    def test_generate_diagram_short_description(self, mock_get_agent, test_client):
        """Test diagram generation with short description"""
        response = test_client.post(
            "/generate-diagram",
            data={"description": "short"}
        )
        
        assert response.status_code == 400
        assert "at least 10 characters" in response.json()["detail"]
    
    @patch('diagram_generator.api.routes.diagram.get_agent')
    def test_generate_diagram_missing_description(self, mock_get_agent, test_client):
        """Test diagram generation with missing description"""
        response = test_client.post("/generate-diagram")
        
        assert response.status_code == 422  # Validation error
    
    @patch('diagram_generator.api.routes.diagram.get_agent')
    def test_generate_diagram_empty_description(self, mock_get_agent, test_client):
        """Test diagram generation with empty description"""
        response = test_client.post(
            "/generate-diagram",
            data={"description": ""}
        )
        
        assert response.status_code == 400
        assert "at least 10 characters" in response.json()["detail"]
    
    @patch('diagram_generator.api.routes.diagram.get_agent')
    def test_generate_diagram_whitespace_description(self, mock_get_agent, test_client):
        """Test diagram generation with whitespace description"""
        response = test_client.post(
            "/generate-diagram",
            data={"description": "   "}
        )
        
        assert response.status_code == 400
        assert "at least 10 characters" in response.json()["detail"]
    
    @patch('diagram_generator.api.routes.diagram.get_agent')
    def test_generate_diagram_get_agent_error(self, mock_get_agent, test_client):
        """Test diagram generation when get_agent fails"""
        mock_get_agent.side_effect = Exception("Agent error")
        
        response = test_client.post(
            "/generate-diagram",
            data={"description": "Generate a microservices architecture"}
        )
        
        assert response.status_code == 500
        assert "Agent error" in response.json()["detail"]
    
    @patch('diagram_generator.api.routes.diagram.get_agent')
    def test_generate_diagram_agent_generate_error(self, mock_get_agent, test_client, mock_agent):
        """Test diagram generation when agent.generate_diagram fails"""
        mock_get_agent.return_value = mock_agent
        mock_agent.generate_diagram.side_effect = Exception("Generation error")
        
        response = test_client.post(
            "/generate-diagram",
            data={"description": "Generate a microservices architecture"}
        )
        
        assert response.status_code == 500
        assert "Generation error" in response.json()["detail"]
    
    @patch('diagram_generator.api.routes.diagram.get_agent')
    @patch('diagram_generator.api.routes.diagram.file_exists')
    def test_generate_diagram_missing_image_file(self, mock_file_exists, mock_get_agent, test_client, mock_agent):
        """Test diagram generation when image file is missing"""
        mock_get_agent.return_value = mock_agent
        mock_file_exists.return_value = False
        
        response_data = DiagramResponse(
            success=True,
            canvas_id="test_canvas",
            image_path="/nonexistent/path.png",
            reasoning="Generated successfully"
        )
        mock_agent.generate_diagram.return_value = response_data
        
        response = test_client.post(
            "/generate-diagram",
            data={"description": "Generate a microservices architecture"}
        )
        
        assert response.status_code == 500
        assert "image file was not found" in response.json()["detail"]
    
    @patch('diagram_generator.api.routes.diagram.get_agent')
    def test_generate_diagram_success_no_image_path(self, mock_get_agent, test_client, mock_agent):
        """Test diagram generation when success but no image path"""
        mock_get_agent.return_value = mock_agent
        
        response_data = DiagramResponse(
            success=True,
            canvas_id="test_canvas",
            image_path=None,
            reasoning="Generated but no image"
        )
        mock_agent.generate_diagram.return_value = response_data
        
        response = test_client.post(
            "/generate-diagram",
            data={"description": "Generate a microservices architecture"}
        )
        
        assert response.status_code == 500
        assert "image file was not found" in response.json()["detail"]
    
    @patch('diagram_generator.api.routes.diagram.get_agent')
    def test_generate_diagram_long_description(self, mock_get_agent, test_client, mock_agent, mock_successful_response):
        """Test diagram generation with long description"""
        mock_get_agent.return_value = mock_agent
        mock_agent.generate_diagram.return_value = mock_successful_response
        
        long_description = "Generate a complex microservices architecture with authentication, authorization, payment processing, order management, inventory tracking, notification services, and monitoring capabilities" * 10
        
        response = test_client.post(
            "/generate-diagram",
            data={"description": long_description}
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"
    
    @patch('diagram_generator.api.routes.diagram.get_agent')
    def test_generate_diagram_special_characters(self, mock_get_agent, test_client, mock_agent, mock_successful_response):
        """Test diagram generation with special characters in description"""
        mock_get_agent.return_value = mock_agent
        mock_agent.generate_diagram.return_value = mock_successful_response
        
        special_description = "Generate a microservices architecture with @#$%^&*() special characters and emojis"
        
        response = test_client.post(
            "/generate-diagram",
            data={"description": special_description}
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"


class TestIntegration:
    """Integration tests for diagram routes"""
    
    @patch('diagram_generator.api.routes.diagram.get_agent')
    def test_end_to_end_diagram_generation(self, mock_get_agent, test_client, mock_agent, mock_successful_response):
        """Test complete end-to-end diagram generation flow"""
        mock_get_agent.return_value = mock_agent
        mock_agent.generate_diagram.return_value = mock_successful_response
        
        # Test the complete flow
        response = test_client.post(
            "/generate-diagram",
            data={"description": "Generate a microservices architecture with API gateway, services, and database"}
        )
        
        # Verify response
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"
        assert len(response.content) > 0
        
        # Verify agent was called correctly
        mock_agent.generate_diagram.assert_called_once()
        call_args = mock_agent.generate_diagram.call_args[0][0]
        assert isinstance(call_args, DiagramRequest)
        assert "microservices architecture" in call_args.description
    
    @patch('diagram_generator.api.routes.diagram.get_agent')
    def test_multiple_requests_same_agent(self, mock_get_agent, test_client, mock_agent, mock_successful_response):
        """Test multiple requests use the same agent instance"""
        mock_get_agent.return_value = mock_agent
        mock_agent.generate_diagram.return_value = mock_successful_response
        
        # Make multiple requests
        for i in range(3):
            response = test_client.post(
                "/generate-diagram",
                data={"description": f"Generate architecture {i}"}
            )
            assert response.status_code == 200
        
        # Verify agent was called multiple times but created only once
        assert mock_agent.generate_diagram.call_count == 3
        assert mock_get_agent.call_count == 3  # get_agent called for each request
        # The same agent instance is returned each time (verified by mock setup)
    
    @patch('diagram_generator.api.routes.diagram.get_agent')
    def test_error_handling_preserves_agent(self, mock_get_agent, test_client, mock_agent, mock_failed_response):
        """Test that errors don't break agent caching"""
        mock_get_agent.return_value = mock_agent
        
        # First request fails
        mock_agent.generate_diagram.return_value = mock_failed_response
        response1 = test_client.post(
            "/generate-diagram",
            data={"description": "Generate architecture 1"}
        )
        assert response1.status_code == 500
        
        # Second request succeeds
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp.write(b"fake image data")
            tmp_path = tmp.name
        
        success_response = DiagramResponse(
            success=True,
            canvas_id="test_canvas",
            image_path=tmp_path,
            reasoning="Generated successfully"
        )
        mock_agent.generate_diagram.return_value = success_response
        
        response2 = test_client.post(
            "/generate-diagram",
            data={"description": "Generate architecture 2"}
        )
        assert response2.status_code == 200
        
        # Verify agent was called for each request
        assert mock_get_agent.call_count == 2  # get_agent called twice
        assert mock_agent.generate_diagram.call_count == 2 