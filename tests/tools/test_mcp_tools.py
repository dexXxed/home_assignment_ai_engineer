"""
Tests for diagram_generator.tools.mcp_tools module
"""
import os
import tempfile
from unittest.mock import patch, MagicMock, Mock

import pytest

from diagram_generator.tools.mcp_tools import (
    get_temp_dir,
    track_created_file,
    create_canvas,
    create_cluster,
    add_node,
    add_edge,
    list_canvas_nodes,
    list_canvas_clusters,
    get_canvas_info,
    render_diagram,
    clear_canvas,
    cleanup_all_temp_files,
    get_available_node_types,
    _CANVASES,
    _NODES,
    _CLUSTERS,
    _CREATED_FILES
)


class TestGetTempDir:
    """Test get_temp_dir function"""
    
    def test_returns_temp_directory_path(self):
        """Test that temp directory path is returned"""
        temp_dir = get_temp_dir()
        assert isinstance(temp_dir, str)
        assert len(temp_dir) > 0
        assert os.path.exists(temp_dir)


class TestTrackCreatedFile:
    """Test track_created_file function"""
    
    def test_tracks_file_path(self):
        """Test that file path is tracked"""
        test_file = "test_file.png"
        initial_count = len(_CREATED_FILES)
        
        track_created_file(test_file)
        
        assert len(_CREATED_FILES) == initial_count + 1
        assert test_file in _CREATED_FILES
    
    def test_tracks_multiple_files(self):
        """Test that multiple files can be tracked"""
        test_files = ["file1.png", "file2.png", "file3.png"]
        initial_count = len(_CREATED_FILES)
        
        for file in test_files:
            track_created_file(file)
        
        assert len(_CREATED_FILES) == initial_count + len(test_files)
        for file in test_files:
            assert file in _CREATED_FILES


class TestCreateCanvas:
    """Test create_canvas function"""
    
    def teardown_method(self):
        """Clean up after each test"""
        # Clear global state
        _CANVASES.clear()
        _NODES.clear()
        _CLUSTERS.clear()
    
    @patch('diagram_generator.tools.mcp_tools.Diagram')
    def test_creates_canvas_with_default_title(self, mock_diagram):
        """Test creating canvas with default title"""
        mock_diagram_instance = MagicMock()
        mock_diagram.return_value = mock_diagram_instance
        
        canvas_id = create_canvas()
        
        assert isinstance(canvas_id, str)
        assert canvas_id in _CANVASES
        assert canvas_id in _NODES
        assert canvas_id in _CLUSTERS
        assert _NODES[canvas_id] == {}
        assert _CLUSTERS[canvas_id] == {}
    
    @patch('diagram_generator.tools.mcp_tools.Diagram')
    def test_creates_canvas_with_custom_title(self, mock_diagram):
        """Test creating canvas with custom title"""
        mock_diagram_instance = MagicMock()
        mock_diagram.return_value = mock_diagram_instance
        
        canvas_id = create_canvas("Custom Architecture")
        
        assert isinstance(canvas_id, str)
        assert canvas_id in _CANVASES
        mock_diagram.assert_called_once()
    
    @patch('diagram_generator.tools.mcp_tools.Diagram')
    def test_creates_unique_canvas_ids(self, mock_diagram):
        """Test that unique canvas IDs are generated"""
        mock_diagram_instance = MagicMock()
        mock_diagram.return_value = mock_diagram_instance
        
        canvas_id1 = create_canvas()
        canvas_id2 = create_canvas()
        
        assert canvas_id1 != canvas_id2
        assert canvas_id1 in _CANVASES
        assert canvas_id2 in _CANVASES


class TestCreateCluster:
    """Test create_cluster function"""
    
    def setup_method(self):
        """Setup for each test"""
        _CANVASES.clear()
        _NODES.clear()
        _CLUSTERS.clear()
    
    @patch('diagram_generator.tools.mcp_tools.Diagram')
    @patch('diagram_generator.tools.mcp_tools.Cluster')
    def test_creates_cluster_on_canvas(self, mock_cluster, mock_diagram):
        """Test creating cluster on existing canvas"""
        mock_diagram_instance = MagicMock()
        mock_diagram.return_value = mock_diagram_instance
        mock_cluster_instance = MagicMock()
        mock_cluster.return_value = mock_cluster_instance
        
        canvas_id = create_canvas()
        create_cluster(canvas_id, "routing", "Routing Layer")
        
        assert "routing" in _CLUSTERS[canvas_id]
        mock_cluster.assert_called_once_with("Routing Layer")
    
    @patch('diagram_generator.tools.mcp_tools.Diagram')
    def test_create_cluster_invalid_canvas(self, mock_diagram):
        """Test creating cluster on non-existent canvas"""
        with pytest.raises(ValueError, match="Canvas invalid_canvas not found"):
            create_cluster("invalid_canvas", "cluster1", "Cluster 1")
    
    @patch('diagram_generator.tools.mcp_tools.Diagram')
    @patch('diagram_generator.tools.mcp_tools.Cluster')
    def test_create_duplicate_cluster(self, mock_cluster, mock_diagram):
        """Test creating duplicate cluster raises error"""
        mock_diagram_instance = MagicMock()
        mock_diagram.return_value = mock_diagram_instance
        mock_cluster_instance = MagicMock()
        mock_cluster.return_value = mock_cluster_instance
        
        canvas_id = create_canvas()
        create_cluster(canvas_id, "routing", "Routing Layer")
        
        with pytest.raises(ValueError, match="Cluster routing already exists"):
            create_cluster(canvas_id, "routing", "Another Routing Layer")


class TestAddNode:
    """Test add_node function"""
    
    def setup_method(self):
        """Setup for each test"""
        _CANVASES.clear()
        _NODES.clear()
        _CLUSTERS.clear()
    
    @patch('diagram_generator.tools.mcp_tools.Diagram')
    @patch('diagram_generator.tools.mcp_tools.APIGateway')
    def test_adds_node_to_canvas(self, mock_api_gateway, mock_diagram):
        """Test adding node to canvas"""
        mock_diagram_instance = MagicMock()
        mock_diagram.return_value = mock_diagram_instance
        mock_node_instance = MagicMock()
        mock_api_gateway.return_value = mock_node_instance
        
        canvas_id = create_canvas()
        add_node(canvas_id, "api_gateway_1", "api_gateway", "API Gateway")
        
        assert "api_gateway_1" in _NODES[canvas_id]
        mock_api_gateway.assert_called_once_with("API Gateway")
    
    @patch('diagram_generator.tools.mcp_tools.Diagram')
    def test_add_node_invalid_canvas(self, mock_diagram):
        """Test adding node to non-existent canvas"""
        with pytest.raises(ValueError, match="Canvas invalid_canvas not found"):
            add_node("invalid_canvas", "node1", "api_gateway")
    
    @patch('diagram_generator.tools.mcp_tools.Diagram')
    def test_add_node_invalid_type(self, mock_diagram):
        """Test adding node with invalid type"""
        mock_diagram_instance = MagicMock()
        mock_diagram.return_value = mock_diagram_instance
        
        canvas_id = create_canvas()
        with pytest.raises(ValueError, match="Unsupported node type"):
            add_node(canvas_id, "node1", "invalid_type")
    
    @patch('diagram_generator.tools.mcp_tools.Diagram')
    @patch('diagram_generator.tools.mcp_tools.APIGateway')
    def test_add_duplicate_node(self, mock_api_gateway, mock_diagram):
        """Test adding duplicate node raises error"""
        mock_diagram_instance = MagicMock()
        mock_diagram.return_value = mock_diagram_instance
        mock_node_instance = MagicMock()
        mock_api_gateway.return_value = mock_node_instance
        
        canvas_id = create_canvas()
        add_node(canvas_id, "api_gateway_1", "api_gateway")
        
        with pytest.raises(ValueError, match="Node api_gateway_1 already exists"):
            add_node(canvas_id, "api_gateway_1", "api_gateway")


class TestAddEdge:
    """Test add_edge function"""
    
    def setup_method(self):
        """Setup for each test"""
        _CANVASES.clear()
        _NODES.clear()
        _CLUSTERS.clear()
    
    @patch('diagram_generator.tools.mcp_tools.Diagram')
    @patch('diagram_generator.tools.mcp_tools.APIGateway')
    @patch('diagram_generator.tools.mcp_tools.EC2')
    def test_adds_edge_between_nodes(self, mock_ec2, mock_api_gateway, mock_diagram):
        """Test adding edge between nodes"""
        mock_diagram_instance = MagicMock()
        mock_diagram.return_value = mock_diagram_instance
        mock_api_gateway_instance = MagicMock()
        mock_api_gateway.return_value = mock_api_gateway_instance
        mock_ec2_instance = MagicMock()
        mock_ec2.return_value = mock_ec2_instance
        
        canvas_id = create_canvas()
        add_node(canvas_id, "api_gateway", "api_gateway")
        add_node(canvas_id, "service", "service")
        
        add_edge(canvas_id, "api_gateway", "service")
        
        # Verify the edge was created (>> operator was called)
        mock_api_gateway_instance.__rshift__.assert_called_once_with(mock_ec2_instance)
    
    @patch('diagram_generator.tools.mcp_tools.Diagram')
    def test_add_edge_invalid_canvas(self, mock_diagram):
        """Test adding edge to non-existent canvas"""
        with pytest.raises(ValueError, match="Canvas invalid_canvas not found"):
            add_edge("invalid_canvas", "node1", "node2")
    
    @patch('diagram_generator.tools.mcp_tools.Diagram')
    @patch('diagram_generator.tools.mcp_tools.APIGateway')
    def test_add_edge_invalid_source_node(self, mock_api_gateway, mock_diagram):
        """Test adding edge with invalid source node"""
        mock_diagram_instance = MagicMock()
        mock_diagram.return_value = mock_diagram_instance
        mock_node_instance = MagicMock()
        mock_api_gateway.return_value = mock_node_instance
        
        canvas_id = create_canvas()
        add_node(canvas_id, "api_gateway", "api_gateway")
        
        with pytest.raises(ValueError, match="Source node invalid_node not found"):
            add_edge(canvas_id, "invalid_node", "api_gateway")
    
    @patch('diagram_generator.tools.mcp_tools.Diagram')
    @patch('diagram_generator.tools.mcp_tools.APIGateway')
    def test_add_edge_invalid_target_node(self, mock_api_gateway, mock_diagram):
        """Test adding edge with invalid target node"""
        mock_diagram_instance = MagicMock()
        mock_diagram.return_value = mock_diagram_instance
        mock_node_instance = MagicMock()
        mock_api_gateway.return_value = mock_node_instance
        
        canvas_id = create_canvas()
        add_node(canvas_id, "api_gateway", "api_gateway")
        
        with pytest.raises(ValueError, match="Target node invalid_node not found"):
            add_edge(canvas_id, "api_gateway", "invalid_node")


class TestListCanvasNodes:
    """Test list_canvas_nodes function"""
    
    def setup_method(self):
        """Setup for each test"""
        _CANVASES.clear()
        _NODES.clear()
        _CLUSTERS.clear()
    
    @patch('diagram_generator.tools.mcp_tools.Diagram')
    @patch('diagram_generator.tools.mcp_tools.APIGateway')
    def test_lists_canvas_nodes(self, mock_api_gateway, mock_diagram):
        """Test listing nodes on canvas"""
        mock_diagram_instance = MagicMock()
        mock_diagram.return_value = mock_diagram_instance
        mock_node_instance = MagicMock()
        mock_api_gateway.return_value = mock_node_instance
        
        canvas_id = create_canvas()
        add_node(canvas_id, "api_gateway", "api_gateway")
        
        nodes = list_canvas_nodes(canvas_id)
        
        assert isinstance(nodes, dict)
        assert "api_gateway" in nodes
        assert nodes["api_gateway"]["node_id"] == "api_gateway"
    
    @patch('diagram_generator.tools.mcp_tools.Diagram')
    def test_list_nodes_empty_canvas(self, mock_diagram):
        """Test listing nodes on empty canvas"""
        mock_diagram_instance = MagicMock()
        mock_diagram.return_value = mock_diagram_instance
        
        canvas_id = create_canvas()
        nodes = list_canvas_nodes(canvas_id)
        
        assert nodes == {}
    
    @patch('diagram_generator.tools.mcp_tools.Diagram')
    def test_list_nodes_invalid_canvas(self, mock_diagram):
        """Test listing nodes on non-existent canvas"""
        with pytest.raises(ValueError, match="Canvas invalid_canvas not found"):
            list_canvas_nodes("invalid_canvas")


class TestListCanvasClusters:
    """Test list_canvas_clusters function"""
    
    def setup_method(self):
        """Setup for each test"""
        _CANVASES.clear()
        _NODES.clear()
        _CLUSTERS.clear()
    
    @patch('diagram_generator.tools.mcp_tools.Diagram')
    @patch('diagram_generator.tools.mcp_tools.Cluster')
    def test_lists_canvas_clusters(self, mock_cluster, mock_diagram):
        """Test listing clusters on canvas"""
        mock_diagram_instance = MagicMock()
        mock_diagram.return_value = mock_diagram_instance
        mock_cluster_instance = MagicMock()
        mock_cluster_instance.label = "Routing Layer"
        mock_cluster.return_value = mock_cluster_instance
        
        canvas_id = create_canvas()
        create_cluster(canvas_id, "routing", "Routing Layer")
        
        clusters = list_canvas_clusters(canvas_id)
        
        assert isinstance(clusters, dict)
        assert "routing" in clusters
        assert clusters["routing"]["cluster_id"] == "routing"
        assert clusters["routing"]["cluster_name"] == "Routing Layer"
    
    @patch('diagram_generator.tools.mcp_tools.Diagram')
    def test_list_clusters_empty_canvas(self, mock_diagram):
        """Test listing clusters on empty canvas"""
        mock_diagram_instance = MagicMock()
        mock_diagram.return_value = mock_diagram_instance
        
        canvas_id = create_canvas()
        clusters = list_canvas_clusters(canvas_id)
        
        assert clusters == {}
    
    @patch('diagram_generator.tools.mcp_tools.Diagram')
    def test_list_clusters_invalid_canvas(self, mock_diagram):
        """Test listing clusters on non-existent canvas"""
        with pytest.raises(ValueError, match="Canvas invalid_canvas not found"):
            list_canvas_clusters("invalid_canvas")


class TestGetCanvasInfo:
    """Test get_canvas_info function"""
    
    def setup_method(self):
        """Setup for each test"""
        _CANVASES.clear()
        _NODES.clear()
        _CLUSTERS.clear()
    
    @patch('diagram_generator.tools.mcp_tools.Diagram')
    def test_gets_canvas_info(self, mock_diagram):
        """Test getting canvas information"""
        mock_diagram_instance = MagicMock()
        mock_diagram_instance.name = "Test Architecture"
        mock_diagram.return_value = mock_diagram_instance
        
        canvas_id = create_canvas("Test Architecture")
        info = get_canvas_info(canvas_id)
        
        assert isinstance(info, dict)
        assert info["canvas_id"] == canvas_id
        assert info["title"] == "Test Architecture"
        assert info["node_count"] == 0
        assert info["cluster_count"] == 0
    
    @patch('diagram_generator.tools.mcp_tools.Diagram')
    def test_get_canvas_info_invalid_canvas(self, mock_diagram):
        """Test getting info for non-existent canvas"""
        with pytest.raises(ValueError, match="Canvas invalid_canvas not found"):
            get_canvas_info("invalid_canvas")


class TestRenderDiagram:
    """Test render_diagram function"""
    
    def setup_method(self):
        """Setup for each test"""
        _CANVASES.clear()
        _NODES.clear()
        _CLUSTERS.clear()
    
    @patch('diagram_generator.tools.mcp_tools.Diagram')
    @patch('os.path.exists')
    def test_renders_diagram(self, mock_exists, mock_diagram):
        """Test rendering diagram"""
        mock_diagram_instance = MagicMock()
        mock_diagram_instance.filename = "test_diagram"
        mock_diagram.return_value = mock_diagram_instance
        mock_exists.return_value = True
        
        canvas_id = create_canvas()
        
        with patch('diagram_generator.tools.mcp_tools.track_created_file') as mock_track:
            result = render_diagram(canvas_id)
            
            assert isinstance(result, str)
            assert result.endswith(".png")
            mock_track.assert_called_once()
    
    @patch('diagram_generator.tools.mcp_tools.Diagram')
    def test_render_diagram_invalid_canvas(self, mock_diagram):
        """Test rendering non-existent canvas"""
        with pytest.raises(ValueError, match="Canvas invalid_canvas not found"):
            render_diagram("invalid_canvas")


class TestClearCanvas:
    """Test clear_canvas function"""
    
    def setup_method(self):
        """Setup for each test"""
        _CANVASES.clear()
        _NODES.clear()
        _CLUSTERS.clear()
    
    @patch('diagram_generator.tools.mcp_tools.Diagram')
    @patch('diagram_generator.tools.mcp_tools.APIGateway')
    def test_clears_canvas(self, mock_api_gateway, mock_diagram):
        """Test clearing canvas"""
        mock_diagram_instance = MagicMock()
        mock_diagram.return_value = mock_diagram_instance
        mock_node_instance = MagicMock()
        mock_api_gateway.return_value = mock_node_instance
        
        canvas_id = create_canvas()
        add_node(canvas_id, "api_gateway", "api_gateway")
        
        assert len(_NODES[canvas_id]) == 1
        
        clear_canvas(canvas_id)
        
        assert len(_NODES[canvas_id]) == 0
        assert len(_CLUSTERS[canvas_id]) == 0
    
    @patch('diagram_generator.tools.mcp_tools.Diagram')
    def test_clear_canvas_invalid_canvas(self, mock_diagram):
        """Test clearing non-existent canvas"""
        with pytest.raises(ValueError, match="Canvas invalid_canvas not found"):
            clear_canvas("invalid_canvas")


class TestCleanupAllTempFiles:
    """Test cleanup_all_temp_files function"""
    
    def test_cleanup_removes_tracked_files(self):
        """Test that cleanup removes tracked files"""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name
        
        # Track the file
        track_created_file(tmp_path)
        
        # Verify file exists and is tracked
        assert os.path.exists(tmp_path)
        assert tmp_path in _CREATED_FILES
        
        # Cleanup
        cleanup_all_temp_files()
        
        # Verify file is removed and not tracked
        assert not os.path.exists(tmp_path)
        assert tmp_path not in _CREATED_FILES
    
    def test_cleanup_handles_missing_files(self):
        """Test that cleanup handles missing files gracefully"""
        # Track a non-existent file
        track_created_file("non_existent_file.png")
        
        # Cleanup should not raise error
        cleanup_all_temp_files()
        
        # File should be removed from tracking
        assert "non_existent_file.png" not in _CREATED_FILES


class TestGetAvailableNodeTypes:
    """Test get_available_node_types function"""
    
    def test_returns_node_types_dict(self):
        """Test that available node types are returned"""
        node_types = get_available_node_types()
        
        assert isinstance(node_types, dict)
        assert len(node_types) > 0
        
        # Check expected node types
        expected_types = [
            "api_gateway",
            "load_balancer", 
            "service",
            "database",
            "queue",
            "monitoring"
        ]
        
        for node_type in expected_types:
            assert node_type in node_types
            assert isinstance(node_types[node_type], str)
            assert len(node_types[node_type]) > 0 