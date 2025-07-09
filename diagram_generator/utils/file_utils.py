"""
File utilities for the diagram generator service
"""
import base64
import glob
import os
from pathlib import Path
from typing import List


def ensure_directory(path: str) -> None:
    """
    Ensure a directory exists, create it if it doesn't
    
    Args:
        path: Directory path to ensure exists
    """
    Path(path).mkdir(parents=True, exist_ok=True)


def get_temp_filename(prefix: str = "diagram", suffix: str = ".png") -> str:
    """
    Generate a temporary filename
    
    Args:
        prefix: Filename prefix
        suffix: Filename suffix
        
    Returns:
        str: Temporary filename
    """
    return f"{prefix}_{os.urandom(8).hex()}{suffix}"


def save_base64_image(image_data: str, filename: str) -> str:
    """
    Save base64 encoded image data to a file
    
    Args:
        image_data: Base64 encoded image data
        filename: Output filename
        
    Returns:
        str: Path to saved file
    """
    image_bytes = base64.b64decode(image_data)
    with open(filename, "wb") as f:
        f.write(image_bytes)
    return filename


def load_image_as_base64(filepath: str) -> str:
    """
    Load an image file and return as base64 encoded string
    
    Args:
        filepath: Path to an image file
        
    Returns:
        str: Base64 encoded image data
    """
    with open(filepath, "rb") as f:
        image_bytes = f.read()
    return base64.b64encode(image_bytes).decode('utf-8')


def find_diagram_files(directory: str, pattern: str = "*diagram*.png") -> List[str]:
    """
    Find diagram files in a directory
    
    Args:
        directory: Directory to search
        pattern: File pattern to match
        
    Returns:
        List[str]: List of found file paths
    """
    search_pattern = os.path.join(directory, pattern)
    return glob.glob(search_pattern)


def cleanup_temp_files(directory: str = "/tmp", pattern: str = "diagram_*.png") -> None:
    """
    Clean up temporary diagram files
    
    Args:
        directory: Directory to clean
        pattern: File pattern to match for cleanup
    """
    try:
        search_pattern = os.path.join(directory, pattern)
        for file_path in glob.glob(search_pattern):
            try:
                os.remove(file_path)
            except OSError:
                pass
    except Exception:
        pass


def get_file_size(filepath: str) -> int:
    """
    Get file size in bytes
    
    Args:
        filepath: Path to file
        
    Returns:
        int: File size in bytes
    """
    return os.path.getsize(filepath)


def file_exists(filepath: str) -> bool:
    """
    Check if a file exists
    
    Args:
        filepath: Path to file
        
    Returns:
        bool: True if a file exists, False otherwise
    """
    return os.path.exists(filepath) and os.path.isfile(filepath)
