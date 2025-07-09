"""
Utility modules for the diagram generator service
"""

from .file_utils import (
    ensure_directory,
    get_temp_filename,
    save_base64_image,
    load_image_as_base64,
    find_diagram_files,
    cleanup_temp_files,
    get_file_size,
    file_exists
)

from .gemini_client import (
    GeminiClient,
    create_gemini_client
)

from .helpers import (
    measure_time,
    measure_time_async,
    get_current_timestamp,
    analyze_user_intent,
    generate_clarifying_questions,
    sanitize_filename,
    format_error_response
)

__all__ = [
    # File utilities
    "ensure_directory",
    "get_temp_filename",
    "save_base64_image",
    "load_image_as_base64",
    "find_diagram_files",
    "cleanup_temp_files",
    "get_file_size",
    "file_exists",

    # Gemini client
    "GeminiClient",
    "create_gemini_client",

    # Helpers
    "measure_time",
    "measure_time_async",
    "get_current_timestamp",
    "analyze_user_intent",
    "generate_clarifying_questions",
    "sanitize_filename",
    "format_error_response"
]
