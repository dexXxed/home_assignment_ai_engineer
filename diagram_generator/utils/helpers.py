"""
Helper utilities for the diagram generator service
"""
import time
from datetime import datetime
from typing import Dict, List, Any

from ..core.constants import (
    RESPONSE_TYPE_DIAGRAM,
    RESPONSE_TYPE_CODE, 
    RESPONSE_TYPE_EXPLANATION,
    RESPONSE_TYPE_QUESTION
)


def measure_time(func):
    """
    Decorator to measure execution time of a function
    
    Args:
        func: Function to measure
        
    Returns:
        Wrapped function that includes timing
    """

    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000  # Convert to milliseconds

        # Add timing info to result if it's a dict
        if isinstance(result, dict):
            result['processing_time_ms'] = execution_time

        return result

    return wrapper


async def measure_time_async(func):
    """
    Decorator to measure execution time of an async function
    
    Args:
        func: Async function to measure
        
    Returns:
        Wrapped async function that includes timing
    """

    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000  # Convert to milliseconds

        # Add timing info to result if it's a dict
        if isinstance(result, dict):
            result['processing_time_ms'] = execution_time

        return result

    return wrapper


def get_current_timestamp() -> datetime:
    """
    Get current timestamp
    
    Returns:
        datetime: Current timestamp
    """
    return datetime.now()


def analyze_user_intent(message: str) -> Dict[str, Any]:
    """
    Analyze user intent from message
    
    Args:
        message: User message
        
    Returns:
        Dict[str, Any]: Intent analysis result
    """
    message_lower = message.lower()

    # Keywords that suggest diagram generation
    diagram_keywords = [
        "diagram", "architecture", "design", "draw", "create", "generate",
        "show", "visualize", "chart", "graph", "flowchart", "blueprint"
    ]

    # Keywords that suggest code request
    code_keywords = [
        "code", "function", "class", "method", "script", "program",
        "implementation", "example", "sample", "snippet"
    ]

    # Keywords that suggest explanation request
    explanation_keywords = [
        "explain", "what is", "how does", "why", "describe", "tell me about",
        "help me understand", "clarify", "definition"
    ]

    # Check for diagram intent
    if any(keyword in message_lower for keyword in diagram_keywords):
        return {
            "intent": RESPONSE_TYPE_DIAGRAM,
            "confidence": 0.8,
            "keywords_found": [kw for kw in diagram_keywords if kw in message_lower]
        }

    # Check for code intent
    if any(keyword in message_lower for keyword in code_keywords):
        return {
            "intent": RESPONSE_TYPE_CODE,
            "confidence": 0.7,
            "keywords_found": [kw for kw in code_keywords if kw in message_lower]
        }

    # Check for explanation intent
    if any(keyword in message_lower for keyword in explanation_keywords):
        return {
            "intent": RESPONSE_TYPE_EXPLANATION,
            "confidence": 0.6,
            "keywords_found": [kw for kw in explanation_keywords if kw in message_lower]
        }

    # Default to question if unclear
    return {
        "intent": RESPONSE_TYPE_QUESTION,
        "confidence": 0.3,
        "keywords_found": []
    }


def generate_clarifying_questions(message: str) -> List[str]:
    """
    Generate clarifying questions based on user message
    
    Args:
        message: User message
        
    Returns:
        List[str]: List of clarifying questions
    """
    questions = [
        "Could you provide more details about what you're looking for?",
        "Are you looking for a specific type of diagram or architecture?",
        "Do you need help with a particular technology or platform?",
        "Would you like me to create a diagram, provide code examples, or explain concepts?"
    ]

    # Add context-specific questions based on message content
    message_lower = message.lower()

    if "architecture" in message_lower:
        questions.append("What type of architecture are you interested in? (web, serverless, microservices, etc.)")

    if "cloud" in message_lower:
        questions.append("Which cloud platform are you working with? (AWS, Azure, GCP)")

    if "database" in message_lower:
        questions.append("What type of database are you considering? (SQL, NoSQL, cache)")

    return questions[:4]  # Return maximum 4 questions


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to remove invalid characters
    
    Args:
        filename: Original filename
        
    Returns:
        str: Sanitized filename
    """
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    sanitized = filename

    for char in invalid_chars:
        sanitized = sanitized.replace(char, '_')

    return sanitized


def format_error_response(error: Exception, context: str = "") -> Dict[str, Any]:
    """
    Format error response in a consistent way
    
    Args:
        error: Exception that occurred
        context: Additional context about the error
        
    Returns:
        Dict[str, Any]: Formatted error response
    """
    return {
        "success": False,
        "error": str(error),
        "context": context,
        "timestamp": get_current_timestamp().isoformat()
    }
