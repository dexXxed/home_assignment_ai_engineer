"""
Constants for the diagram generator service
"""

# Response Types
RESPONSE_TYPE_DIAGRAM = "diagram"
RESPONSE_TYPE_CODE = "code"
RESPONSE_TYPE_EXPLANATION = "explanation"
RESPONSE_TYPE_QUESTION = "question"

# Supported Node Types for Microservices Architecture
NODE_TYPES = {
    "api_gateway": "API Gateway service for routing requests",
    "load_balancer": "Load balancer (ALB/NLB) for distributing traffic",
    "service": "Application service or microservice",
    "database": "Database service (RDS, DynamoDB, etc.)",
    "queue": "Message queue service (SQS, SNS, etc.)",
    "monitoring": "Monitoring service (CloudWatch, X-Ray, etc.)"
}

# Microservices Architecture Patterns
MICROSERVICES_PATTERNS = {
    "api_gateway_pattern": "API Gateway routing to multiple microservices",
    "service_mesh_pattern": "Service-to-service communication with load balancing",
    "event_driven_pattern": "Event-driven architecture with message queues",
    "cqrs_pattern": "Command Query Responsibility Segregation pattern",
    "saga_pattern": "Distributed transaction management pattern",
    "circuit_breaker_pattern": "Fault tolerance and resilience pattern"
}
