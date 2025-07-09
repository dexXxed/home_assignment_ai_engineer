"""
Tests for diagram_generator.core.constants module
"""
import pytest

from diagram_generator.core.constants import (
    RESPONSE_TYPE_DIAGRAM,
    RESPONSE_TYPE_CODE,
    RESPONSE_TYPE_EXPLANATION,
    RESPONSE_TYPE_QUESTION,
    NODE_TYPES,
    MICROSERVICES_PATTERNS
)


class TestResponseTypes:
    """Test response type constants"""
    
    def test_response_type_values(self):
        """Test that response type constants have correct values"""
        assert RESPONSE_TYPE_DIAGRAM == "diagram"
        assert RESPONSE_TYPE_CODE == "code"
        assert RESPONSE_TYPE_EXPLANATION == "explanation"
        assert RESPONSE_TYPE_QUESTION == "question"
    
    def test_response_types_are_strings(self):
        """Test that all response types are strings"""
        response_types = [
            RESPONSE_TYPE_DIAGRAM,
            RESPONSE_TYPE_CODE,
            RESPONSE_TYPE_EXPLANATION,
            RESPONSE_TYPE_QUESTION
        ]
        
        for response_type in response_types:
            assert isinstance(response_type, str)
            assert len(response_type) > 0
    
    def test_response_types_are_unique(self):
        """Test that all response types are unique"""
        response_types = [
            RESPONSE_TYPE_DIAGRAM,
            RESPONSE_TYPE_CODE,
            RESPONSE_TYPE_EXPLANATION,
            RESPONSE_TYPE_QUESTION
        ]
        
        assert len(response_types) == len(set(response_types))


class TestNodeTypes:
    """Test node type constants"""
    
    def test_node_types_is_dict(self):
        """Test that NODE_TYPES is a dictionary"""
        assert isinstance(NODE_TYPES, dict)
        assert len(NODE_TYPES) > 0
    
    def test_expected_node_types_exist(self):
        """Test that expected node types exist"""
        expected_types = [
            "api_gateway",
            "load_balancer",
            "service",
            "database",
            "queue",
            "monitoring"
        ]
        
        for node_type in expected_types:
            assert node_type in NODE_TYPES
    
    def test_node_types_have_descriptions(self):
        """Test that all node types have descriptions"""
        for node_type, description in NODE_TYPES.items():
            assert isinstance(node_type, str)
            assert isinstance(description, str)
            assert len(node_type) > 0
            assert len(description) > 0
    
    def test_node_types_count(self):
        """Test that we have exactly 6 node types"""
        assert len(NODE_TYPES) == 6
    
    def test_api_gateway_description(self):
        """Test api_gateway description"""
        assert NODE_TYPES["api_gateway"] == "API Gateway service for routing requests"
    
    def test_load_balancer_description(self):
        """Test load_balancer description"""
        assert NODE_TYPES["load_balancer"] == "Load balancer (ALB/NLB) for distributing traffic"
    
    def test_service_description(self):
        """Test service description"""
        assert NODE_TYPES["service"] == "Application service or microservice"
    
    def test_database_description(self):
        """Test database description"""
        assert NODE_TYPES["database"] == "Database service (RDS, DynamoDB, etc.)"
    
    def test_queue_description(self):
        """Test queue description"""
        assert NODE_TYPES["queue"] == "Message queue service (SQS, SNS, etc.)"
    
    def test_monitoring_description(self):
        """Test monitoring description"""
        assert NODE_TYPES["monitoring"] == "Monitoring service (CloudWatch, X-Ray, etc.)"


class TestMicroservicesPatterns:
    """Test microservices pattern constants"""
    
    def test_microservices_patterns_is_dict(self):
        """Test that MICROSERVICES_PATTERNS is a dictionary"""
        assert isinstance(MICROSERVICES_PATTERNS, dict)
        assert len(MICROSERVICES_PATTERNS) > 0
    
    def test_expected_patterns_exist(self):
        """Test that expected patterns exist"""
        expected_patterns = [
            "api_gateway_pattern",
            "service_mesh_pattern",
            "event_driven_pattern",
            "cqrs_pattern",
            "saga_pattern",
            "circuit_breaker_pattern"
        ]
        
        for pattern in expected_patterns:
            assert pattern in MICROSERVICES_PATTERNS
    
    def test_patterns_have_descriptions(self):
        """Test that all patterns have descriptions"""
        for pattern, description in MICROSERVICES_PATTERNS.items():
            assert isinstance(pattern, str)
            assert isinstance(description, str)
            assert len(pattern) > 0
            assert len(description) > 0
    
    def test_patterns_count(self):
        """Test that we have exactly 6 patterns"""
        assert len(MICROSERVICES_PATTERNS) == 6
    
    def test_api_gateway_pattern_description(self):
        """Test api_gateway_pattern description"""
        expected = "API Gateway routing to multiple microservices"
        assert MICROSERVICES_PATTERNS["api_gateway_pattern"] == expected
    
    def test_service_mesh_pattern_description(self):
        """Test service_mesh_pattern description"""
        expected = "Service-to-service communication with load balancing"
        assert MICROSERVICES_PATTERNS["service_mesh_pattern"] == expected
    
    def test_event_driven_pattern_description(self):
        """Test event_driven_pattern description"""
        expected = "Event-driven architecture with message queues"
        assert MICROSERVICES_PATTERNS["event_driven_pattern"] == expected
    
    def test_cqrs_pattern_description(self):
        """Test cqrs_pattern description"""
        expected = "Command Query Responsibility Segregation pattern"
        assert MICROSERVICES_PATTERNS["cqrs_pattern"] == expected
    
    def test_saga_pattern_description(self):
        """Test saga_pattern description"""
        expected = "Distributed transaction management pattern"
        assert MICROSERVICES_PATTERNS["saga_pattern"] == expected
    
    def test_circuit_breaker_pattern_description(self):
        """Test circuit_breaker_pattern description"""
        expected = "Fault tolerance and resilience pattern"
        assert MICROSERVICES_PATTERNS["circuit_breaker_pattern"] == expected


class TestConstantsIntegration:
    """Test integration between constants"""
    
    def test_all_constants_are_defined(self):
        """Test that all expected constants are defined"""
        # This test ensures we haven't missed any constants
        assert RESPONSE_TYPE_DIAGRAM is not None
        assert RESPONSE_TYPE_CODE is not None
        assert RESPONSE_TYPE_EXPLANATION is not None
        assert RESPONSE_TYPE_QUESTION is not None
        assert NODE_TYPES is not None
        assert MICROSERVICES_PATTERNS is not None
    
    def test_constants_are_immutable_types(self):
        """Test that constants use immutable types"""
        # Strings are immutable
        assert isinstance(RESPONSE_TYPE_DIAGRAM, str)
        assert isinstance(RESPONSE_TYPE_CODE, str)
        assert isinstance(RESPONSE_TYPE_EXPLANATION, str)
        assert isinstance(RESPONSE_TYPE_QUESTION, str)
        
        # Dictionaries are mutable but we can test their structure
        assert isinstance(NODE_TYPES, dict)
        assert isinstance(MICROSERVICES_PATTERNS, dict) 