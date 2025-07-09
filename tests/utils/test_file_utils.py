"""
Tests for diagram_generator.utils.file_utils module
"""
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

import pytest

from diagram_generator.utils.file_utils import (
    ensure_directory,
    get_temp_filename,
    save_base64_image,
    load_image_as_base64,
    find_diagram_files,
    cleanup_temp_files,
    get_file_size,
    file_exists
)


class TestEnsureDirectory:
    """Test ensure_directory function"""
    
    def test_creates_directory_if_not_exists(self, temp_dir):
        """Test that directory is created if it doesn't exist"""
        test_path = os.path.join(temp_dir, "test_dir")
        ensure_directory(test_path)
        assert os.path.exists(test_path)
        assert os.path.isdir(test_path)
    
    def test_no_error_if_directory_exists(self, temp_dir):
        """Test that no error occurs if directory already exists"""
        ensure_directory(temp_dir)  # Should not raise any error
        assert os.path.exists(temp_dir)
    
    def test_creates_nested_directories(self, temp_dir):
        """Test that nested directories are created"""
        nested_path = os.path.join(temp_dir, "level1", "level2", "level3")
        ensure_directory(nested_path)
        assert os.path.exists(nested_path)
        assert os.path.isdir(nested_path)


class TestGetTempFilename:
    """Test get_temp_filename function"""
    
    def test_default_parameters(self):
        """Test filename generation with default parameters"""
        filename = get_temp_filename()
        assert filename.startswith("diagram_")
        assert filename.endswith(".png")
        assert len(filename) > 20  # Should have random hex component
    
    def test_custom_parameters(self):
        """Test filename generation with custom parameters"""
        filename = get_temp_filename(prefix="test", suffix=".jpg")
        assert filename.startswith("test_")
        assert filename.endswith(".jpg")
    
    def test_unique_filenames(self):
        """Test that generated filenames are unique"""
        filename1 = get_temp_filename()
        filename2 = get_temp_filename()
        assert filename1 != filename2


class TestSaveBase64Image:
    """Test save_base64_image function"""
    
    def test_saves_image_correctly(self, temp_dir, sample_image_data):
        """Test that base64 image is saved correctly"""
        filepath = os.path.join(temp_dir, "test.png")
        result = save_base64_image(sample_image_data, filepath)
        
        assert result == filepath
        assert os.path.exists(filepath)
        assert os.path.getsize(filepath) > 0
    
    def test_handles_invalid_base64(self, temp_dir):
        """Test handling of invalid base64 data"""
        filepath = os.path.join(temp_dir, "test.png")
        with pytest.raises(Exception):  # Should raise base64 decoding error
            save_base64_image("invalid_base64", filepath)


class TestLoadImageAsBase64:
    """Test load_image_as_base64 function"""
    
    def test_loads_image_as_base64(self, temp_dir, sample_image_data):
        """Test that image is loaded and converted to base64"""
        # First save an image
        filepath = os.path.join(temp_dir, "test.png")
        save_base64_image(sample_image_data, filepath)
        
        # Then load it back
        result = load_image_as_base64(filepath)
        assert isinstance(result, str)
        assert len(result) > 0
        assert result == sample_image_data
    
    def test_handles_nonexistent_file(self):
        """Test handling of non-existent file"""
        with pytest.raises(FileNotFoundError):
            load_image_as_base64("nonexistent.png")


class TestFindDiagramFiles:
    """Test find_diagram_files function"""
    
    def test_finds_diagram_files(self, temp_dir):
        """Test finding diagram files with default pattern"""
        # Create test files
        diagram_file = os.path.join(temp_dir, "test_diagram_1.png")
        other_file = os.path.join(temp_dir, "test_other.png")
        
        Path(diagram_file).touch()
        Path(other_file).touch()
        
        files = find_diagram_files(temp_dir)
        assert diagram_file in files
        assert other_file not in files
    
    def test_finds_files_with_custom_pattern(self, temp_dir):
        """Test finding files with custom pattern"""
        # Create test files
        test_file = os.path.join(temp_dir, "custom_test.png")
        other_file = os.path.join(temp_dir, "other.png")
        
        Path(test_file).touch()
        Path(other_file).touch()
        
        files = find_diagram_files(temp_dir, "custom_*.png")
        assert test_file in files
        assert other_file not in files
    
    def test_returns_empty_list_if_no_files(self, temp_dir):
        """Test returns empty list if no matching files found"""
        files = find_diagram_files(temp_dir)
        assert files == []


class TestCleanupTempFiles:
    """Test cleanup_temp_files function"""
    
    def test_removes_matching_files(self, temp_dir):
        """Test that matching files are removed"""
        # Create test files
        diagram_file = os.path.join(temp_dir, "diagram_test.png")
        other_file = os.path.join(temp_dir, "other.png")
        
        Path(diagram_file).touch()
        Path(other_file).touch()
        
        cleanup_temp_files(temp_dir, "diagram_*.png")
        
        assert not os.path.exists(diagram_file)
        assert os.path.exists(other_file)
    
    def test_handles_nonexistent_directory(self):
        """Test handling of non-existent directory"""
        # Should not raise error
        cleanup_temp_files("/nonexistent/directory")
    
    def test_handles_permission_errors(self, temp_dir):
        """Test handling of permission errors during cleanup"""
        with patch('os.remove', side_effect=OSError("Permission denied")):
            cleanup_temp_files(temp_dir)  # Should not raise error


class TestGetFileSize:
    """Test get_file_size function"""
    
    def test_returns_correct_size(self, temp_dir):
        """Test that correct file size is returned"""
        test_file = os.path.join(temp_dir, "test.txt")
        test_content = "Hello, World!"
        
        with open(test_file, "w") as f:
            f.write(test_content)
        
        size = get_file_size(test_file)
        assert size == len(test_content)
    
    def test_handles_nonexistent_file(self):
        """Test handling of non-existent file"""
        with pytest.raises(FileNotFoundError):
            get_file_size("nonexistent.txt")


class TestFileExists:
    """Test file_exists function"""
    
    def test_returns_true_for_existing_file(self, temp_dir):
        """Test returns True for existing file"""
        test_file = os.path.join(temp_dir, "test.txt")
        Path(test_file).touch()
        
        assert file_exists(test_file) is True
    
    def test_returns_false_for_nonexistent_file(self):
        """Test returns False for non-existent file"""
        assert file_exists("nonexistent.txt") is False
    
    def test_returns_false_for_directory(self, temp_dir):
        """Test returns False for directory"""
        assert file_exists(temp_dir) is False 