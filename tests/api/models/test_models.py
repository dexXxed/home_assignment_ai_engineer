"""
Tests for diagram_generator.api.models modules
"""
import pytest
from pydantic import ValidationError

from diagram_generator.api.models.requests import DiagramRequest
from diagram_generator.api.models.responses import DiagramResponse
from diagram_generator.api.models.schemas import ToolCall


class TestDiagramRequest:
    """Test DiagramRequest model"""
    
    def test_valid_diagram_request(self):
        """Test creating a valid diagram request"""
        request = DiagramRequest(
            description="Generate a microservices architecture",
            format="png"
        )
        
        assert request.description == "Generate a microservices architecture"
        assert request.format == "png"
    
    def test_diagram_request_without_format(self):
        """Test creating diagram request without format"""
        request = DiagramRequest(
            description="Generate a microservices architecture"
        )
        
        assert request.description == "Generate a microservices architecture"
        assert request.format is None
    
    def test_diagram_request_requires_description(self):
        """Test that description is required"""
        with pytest.raises(ValidationError):
            DiagramRequest()
    
    def test_diagram_request_empty_description(self):
        """Test that empty description is accepted by model (validation is done in route)"""
        request = DiagramRequest(description="")
        assert request.description == ""
    
    def test_diagram_request_description_validation(self):
        """Test description field validation"""
        # Valid description
        request = DiagramRequest(description="Valid description")
        assert request.description == "Valid description"
        
        # None description should raise error
        with pytest.raises(ValidationError):
            DiagramRequest(description=None)
    
    def test_diagram_request_format_is_optional(self):
        """Test that format field is optional"""
        request = DiagramRequest(description="Test description")
        assert request.format is None
        
        request = DiagramRequest(description="Test description", format="svg")
        assert request.format == "svg"
    
    def test_diagram_request_serialization(self):
        """Test request serialization"""
        request = DiagramRequest(
            description="Test description",
            format="png"
        )
        
        data = request.model_dump()
        assert data["description"] == "Test description"
        assert data["format"] == "png"
    
    def test_diagram_request_from_dict(self):
        """Test creating request from dictionary"""
        data = {
            "description": "Test description",
            "format": "svg"
        }
        
        request = DiagramRequest(**data)
        assert request.description == "Test description"
        assert request.format == "svg"


class TestDiagramResponse:
    """Test DiagramResponse model"""
    
    def test_successful_diagram_response(self):
        """Test creating a successful diagram response"""
        response = DiagramResponse(
            success=True,
            canvas_id="test_canvas_123",
            image_path="/path/to/image.png",
            reasoning="Generated architecture diagram with microservices"
        )
        
        assert response.success is True
        assert response.canvas_id == "test_canvas_123"
        assert response.image_path == "/path/to/image.png"
        assert response.error is None
        assert response.reasoning == "Generated architecture diagram with microservices"
    
    def test_failed_diagram_response(self):
        """Test creating a failed diagram response"""
        response = DiagramResponse(
            success=False,
            error="Failed to generate diagram",
            reasoning="Unable to process the request"
        )
        
        assert response.success is False
        assert response.canvas_id is None
        assert response.image_path is None
        assert response.error == "Failed to generate diagram"
        assert response.reasoning == "Unable to process the request"
    
    def test_diagram_response_requires_success(self):
        """Test that success field is required"""
        with pytest.raises(ValidationError):
            DiagramResponse(reasoning="Test reasoning")
    
    def test_diagram_response_requires_reasoning(self):
        """Test that reasoning field is required"""
        with pytest.raises(ValidationError):
            DiagramResponse(success=True)
    
    def test_diagram_response_optional_fields(self):
        """Test that optional fields default to None"""
        response = DiagramResponse(
            success=True,
            reasoning="Test reasoning"
        )
        
        assert response.canvas_id is None
        assert response.image_path is None
        assert response.error is None
    
    def test_diagram_response_serialization(self):
        """Test response serialization"""
        response = DiagramResponse(
            success=True,
            canvas_id="test_canvas",
            image_path="/path/to/image.png",
            reasoning="Test reasoning"
        )
        
        data = response.model_dump()
        assert data["success"] is True
        assert data["canvas_id"] == "test_canvas"
        assert data["image_path"] == "/path/to/image.png"
        assert data["error"] is None
        assert data["reasoning"] == "Test reasoning"
    
    def test_diagram_response_from_dict(self):
        """Test creating response from dictionary"""
        data = {
            "success": True,
            "canvas_id": "test_canvas",
            "image_path": "/path/to/image.png",
            "error": None,
            "reasoning": "Test reasoning"
        }
        
        response = DiagramResponse(**data)
        assert response.success is True
        assert response.canvas_id == "test_canvas"
        assert response.image_path == "/path/to/image.png"
        assert response.error is None
        assert response.reasoning == "Test reasoning"


class TestToolCall:
    """Test ToolCall model"""
    
    def test_valid_tool_call(self):
        """Test creating a valid tool call"""
        tool_call = ToolCall(
            name="create_canvas",
            args={"title": "Test Architecture"}
        )
        
        assert tool_call.name == "create_canvas"
        assert tool_call.args == {"title": "Test Architecture"}
    
    def test_tool_call_requires_name(self):
        """Test that name field is required"""
        with pytest.raises(ValidationError):
            ToolCall(args={"key": "value"})
    
    def test_tool_call_requires_args(self):
        """Test that args field is required"""
        with pytest.raises(ValidationError):
            ToolCall(name="test_tool")
    
    def test_tool_call_empty_args(self):
        """Test tool call with empty args"""
        tool_call = ToolCall(
            name="test_tool",
            args={}
        )
        
        assert tool_call.name == "test_tool"
        assert tool_call.args == {}
    
    def test_tool_call_complex_args(self):
        """Test tool call with complex args"""
        args = {
            "canvas_id": "test_canvas",
            "node_id": "api_gateway",
            "node_type": "api_gateway",
            "label": "API Gateway",
            "cluster_id": "routing"
        }
        
        tool_call = ToolCall(
            name="add_node",
            args=args
        )
        
        assert tool_call.name == "add_node"
        assert tool_call.args == args
    
    def test_tool_call_serialization(self):
        """Test tool call serialization"""
        tool_call = ToolCall(
            name="test_tool",
            args={"param1": "value1", "param2": 42}
        )
        
        data = tool_call.model_dump()
        assert data["name"] == "test_tool"
        assert data["args"] == {"param1": "value1", "param2": 42}
    
    def test_tool_call_from_dict(self):
        """Test creating tool call from dictionary"""
        data = {
            "name": "render_diagram",
            "args": {"canvas_id": "test_canvas"}
        }
        
        tool_call = ToolCall(**data)
        assert tool_call.name == "render_diagram"
        assert tool_call.args == {"canvas_id": "test_canvas"}
    
    def test_tool_call_args_validation(self):
        """Test that args must be a dictionary"""
        with pytest.raises(ValidationError):
            ToolCall(name="test_tool", args="not_a_dict")
        
        with pytest.raises(ValidationError):
            ToolCall(name="test_tool", args=123)
        
        with pytest.raises(ValidationError):
            ToolCall(name="test_tool", args=["list", "not", "dict"])


class TestModelsIntegration:
    """Test integration between models"""
    
    def test_models_work_together(self):
        """Test that models work together in a typical flow"""
        # Create a request
        request = DiagramRequest(
            description="Generate microservices architecture"
        )
        
        # Create tool calls that would be generated
        tool_calls = [
            ToolCall(
                name="create_canvas",
                args={"title": "Microservices Architecture"}
            ),
            ToolCall(
                name="add_node",
                args={
                    "canvas_id": "test_canvas",
                    "node_id": "api_gateway",
                    "node_type": "api_gateway",
                    "label": "API Gateway"
                }
            )
        ]
        
        # Create a successful response
        response = DiagramResponse(
            success=True,
            canvas_id="test_canvas",
            image_path="/path/to/diagram.png",
            reasoning="Generated microservices architecture with API Gateway"
        )
        
        # Verify all models are working correctly
        assert request.description == "Generate microservices architecture"
        assert len(tool_calls) == 2
        assert tool_calls[0].name == "create_canvas"
        assert tool_calls[1].name == "add_node"
        assert response.success is True
        assert response.canvas_id == "test_canvas"
    
    def test_json_serialization_roundtrip(self):
        """Test that models can be serialized and deserialized"""
        # Test DiagramRequest
        request = DiagramRequest(description="Test description")
        request_data = request.model_dump()
        request_restored = DiagramRequest(**request_data)
        assert request_restored.description == request.description
        
        # Test DiagramResponse
        response = DiagramResponse(success=True, reasoning="Test reasoning")
        response_data = response.model_dump()
        response_restored = DiagramResponse(**response_data)
        assert response_restored.success == response.success
        assert response_restored.reasoning == response.reasoning
        
        # Test ToolCall
        tool_call = ToolCall(name="test_tool", args={"key": "value"})
        tool_call_data = tool_call.model_dump()
        tool_call_restored = ToolCall(**tool_call_data)
        assert tool_call_restored.name == tool_call.name
        assert tool_call_restored.args == tool_call.args 