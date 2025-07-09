"""
MCP tools for diagram generation
Individual tool functions that can be used by the MCP server
"""
import glob
import logging
import os
import tempfile
from typing import Dict, Optional, Any
from uuid import uuid4

from diagrams import Diagram, Cluster
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.integration import SQS
from diagrams.aws.management import Cloudwatch
from diagrams.aws.network import ALB, APIGateway

from ..core.constants import NODE_TYPES
from ..utils import ensure_directory, cleanup_temp_files

# Configure logging
logger = logging.getLogger(__name__)

# Global storage for canvases, nodes, and clusters
_CANVASES: Dict[str, Diagram] = {}
_NODES: Dict[str, Dict[str, object]] = {}
_CLUSTERS: Dict[str, Dict[str, Cluster]] = {}
_TEMP_DIR = tempfile.mkdtemp()
_CREATED_FILES: set = set()


def get_temp_dir() -> str:
    """
    Get the temporary directory for diagram files
    
    Returns:
        str: Temporary directory path
    """
    return _TEMP_DIR


def track_created_file(file_path: str) -> None:
    """
    Track a created file for cleanup
    
    Args:
        file_path: Path to file to track
    """
    _CREATED_FILES.add(file_path)


def create_canvas(title: str = "Architecture Diagram") -> str:
    """
    Create a new diagram canvas

    Args:
        title: Title for the diagram canvas
        
    Returns:
        str: ID of the created canvas
    """
    canvas_id = str(uuid4())

    # Ensure temp directory exists
    ensure_directory(_TEMP_DIR)

    # Create diagram with temporary file handling
    diagram_path = os.path.join(_TEMP_DIR, f"diagram_{canvas_id}")

    diagram = Diagram(
        name=title,
        filename=diagram_path,
        outformat="png",
        show=False,
        graph_attr={
            "rankdir": "LR",
            "splines": "ortho",
            "nodesep": "0.6",
            "ranksep": "0.8"
        }
    )

    _CANVASES[canvas_id] = diagram
    _NODES[canvas_id] = {}
    _CLUSTERS[canvas_id] = {}

    return canvas_id


def create_cluster(canvas_id: str, cluster_id: str, cluster_name: str) -> None:
    """
    Create a cluster/submodule to group related services
    
    Args:
        canvas_id: Target canvas identifier
        cluster_id: Unique identifier for the cluster
        cluster_name: Display name for the cluster
        
    Raises:
        ValueError: If canvas not found or cluster already exists
    """
    if canvas_id not in _CANVASES:
        raise ValueError(f"Canvas {canvas_id} not found")

    if cluster_id in _CLUSTERS[canvas_id]:
        raise ValueError(f"Cluster {cluster_id} already exists on canvas {canvas_id}")

    diagram = _CANVASES[canvas_id]

    # Create cluster within diagram context
    with diagram:
        cluster = Cluster(cluster_name)
        _CLUSTERS[canvas_id][cluster_id] = cluster


def add_node(
        canvas_id: str,
        node_id: str,
        node_type: str,
        label: Optional[str] = None,
        cluster_id: Optional[str] = None
) -> None:
    """
    Add a node of the specified type to an existing canvas or cluster
    
    Args:
        canvas_id: Target canvas identifier
        node_id: Unique identifier for the new node
        node_type: Type of node to create from available options
        label: Optional custom label for the node
        cluster_id: Optional cluster to add the node to
        
    Raises:
        ValueError: If canvas not found, node already exists, or unsupported node type
    """
    if canvas_id not in _CANVASES:
        raise ValueError(f"Canvas {canvas_id} not found")

    if node_id in _NODES[canvas_id]:
        raise ValueError(f"Node {node_id} already exists on canvas {canvas_id}")

    if cluster_id and cluster_id not in _CLUSTERS[canvas_id]:
        raise ValueError(f"Cluster {cluster_id} not found on canvas {canvas_id}")

    diagram = _CANVASES[canvas_id]
    display_label = label or node_id

    # Tightened node type mapping - only 6 core types to reduce hallucinations
    node_map = {
        # Core API Gateway
        "api_gateway": lambda: APIGateway(display_label),

        # Load Balancer (default to ALB)
        "load_balancer": lambda: ALB(display_label),

        # Service (default to EC2 for general services)
        "service": lambda: EC2(display_label),

        # Database (default to RDS)
        "database": lambda: RDS(display_label),

        # Queue (default to SQS)
        "queue": lambda: SQS(display_label),

        # Monitoring (default to CloudWatch)
        "monitoring": lambda: Cloudwatch(display_label),
    }

    if node_type not in node_map:
        raise ValueError(f"Unsupported node type: {node_type}. Supported types: {list(node_map.keys())}")

    # Create node within diagram context
    with diagram:
        if cluster_id:
            # Add node to cluster
            cluster = _CLUSTERS[canvas_id][cluster_id]
            with cluster:
                _NODES[canvas_id][node_id] = node_map[node_type]()
        else:
            # Add node to canvas directly
            _NODES[canvas_id][node_id] = node_map[node_type]()


def add_edge(canvas_id: str, source_node_id: str, target_node_id: str) -> None:
    """
    Connect two existing nodes on the same canvas with a directed edge
    
    NOTE: services must connect to all shared infra nodes.
    The agent's post-processor enforces this rule if the LLM misses an edge.
    
    Args:
        canvas_id: Target canvas identifier
        source_node_id: Source node identifier
        target_node_id: Target node identifier
        
    Raises:
        ValueError: If canvas or nodes not found
    """
    if canvas_id not in _CANVASES:
        raise ValueError(f"Canvas {canvas_id} not found")

    if source_node_id not in _NODES[canvas_id]:
        raise ValueError(f"Source node {source_node_id} not found on canvas {canvas_id}")

    if target_node_id not in _NODES[canvas_id]:
        raise ValueError(f"Target node {target_node_id} not found on canvas {canvas_id}")

    # Create connection between nodes
    _NODES[canvas_id][source_node_id] >> _NODES[canvas_id][target_node_id]


def list_canvas_nodes(canvas_id: str) -> Dict[str, Dict[str, str]]:
    """
    List all nodes present on a specific canvas
    
    Args:
        canvas_id: Target canvas identifier
        
    Returns:
        Dict[str, Dict[str, str]]: Dictionary mapping node IDs to their information
        
    Raises:
        ValueError: If canvas not found
    """
    if canvas_id not in _CANVASES:
        raise ValueError(f"Canvas {canvas_id} not found")

    nodes_info = {}
    for node_id in _NODES[canvas_id]:
        # Try to determine node type from the node object
        node_obj = _NODES[canvas_id][node_id]
        node_type = type(node_obj).__name__.lower()

        nodes_info[node_id] = {
            "node_id": node_id,
            "node_type": node_type
        }

    return nodes_info


def list_canvas_clusters(canvas_id: str) -> Dict[str, Dict[str, str]]:
    """
    List all clusters present on a specific canvas
    
    Args:
        canvas_id: Target canvas identifier
        
    Returns:
        Dict[str, Dict[str, str]]: Dictionary mapping cluster IDs to their information
        
    Raises:
        ValueError: If canvas not found
    """
    if canvas_id not in _CANVASES:
        raise ValueError(f"Canvas {canvas_id} not found")

    clusters_info = {}
    for cluster_id in _CLUSTERS[canvas_id]:
        cluster_obj = _CLUSTERS[canvas_id][cluster_id]

        clusters_info[cluster_id] = {
            "cluster_id": cluster_id,
            "cluster_name": cluster_obj.label if hasattr(cluster_obj, 'label') else cluster_id
        }

    return clusters_info


def get_canvas_info(canvas_id: str) -> Dict[str, Any]:
    """
    Get information about a specific canvas
    
    Args:
        canvas_id: Target canvas identifier
        
    Returns:
        Dict[str, Any]: Canvas information
        
    Raises:
        ValueError: If canvas not found
    """
    if canvas_id not in _CANVASES:
        raise ValueError(f"Canvas {canvas_id} not found")

    diagram = _CANVASES[canvas_id]
    node_count = len(_NODES[canvas_id])
    cluster_count = len(_CLUSTERS[canvas_id])

    return {
        "canvas_id": canvas_id,
        "title": diagram.name,
        "node_count": node_count,
        "cluster_count": cluster_count
    }


def render_diagram(canvas_id: str) -> str:
    """
    Render the canvas to a PNG image file and return the file path
    
    Args:
        canvas_id: Target canvas identifier
        
    Returns:
        str: Path to the generated PNG file
        
    Raises:
        ValueError: If canvas not found
        FileNotFoundError: If rendered file cannot be found
    """
    if canvas_id not in _CANVASES:
        raise ValueError(f"Canvas {canvas_id} not found")

    diagram = _CANVASES[canvas_id]

    # Close the diagram context to trigger rendering
    diagram.__exit__(None, None, None)

    # Find the generated PNG file
    expected_path = f"{diagram.filename}.png"

    # Look for the file in various locations
    possible_paths = [
        expected_path,
        os.path.join(_TEMP_DIR, f"diagram_{canvas_id}.png"),
        os.path.join(_TEMP_DIR, f"{canvas_id}.png"),
    ]

    for path in possible_paths:
        if os.path.exists(path):
            track_created_file(path)
            return path

    # If not found, try to find any PNG file that might be our diagram
    pattern = os.path.join(_TEMP_DIR, "*.png")
    files = glob.glob(pattern)

    if files:
        # Return the most recently created file
        latest_file = max(files, key=os.path.getctime)
        track_created_file(latest_file)
        return latest_file

    raise FileNotFoundError(f"Could not find rendered diagram for canvas {canvas_id}")


def clear_canvas(canvas_id: str) -> None:
    """
    Clear all nodes and clusters from a canvas
    
    Args:
        canvas_id: Target canvas identifier
        
    Raises:
        ValueError: If canvas not found
    """
    if canvas_id not in _CANVASES:
        raise ValueError(f"Canvas {canvas_id} not found")

    _NODES[canvas_id] = {}
    _CLUSTERS[canvas_id] = {}


def cleanup_all_temp_files() -> None:
    """
    Clean up all temporary files created during diagram generation
    """
    try:
        # Remove tracked files
        for file_path in _CREATED_FILES:
            if os.path.exists(file_path):
                os.remove(file_path)
        _CREATED_FILES.clear()

        # Clean up any remaining diagram files
        cleanup_temp_files(_TEMP_DIR, "*.png")
        cleanup_temp_files(_TEMP_DIR, "diagram_*")

    except Exception as e:
        logger.warning(f"Could not clean up all temporary files: {e}")


def get_available_node_types() -> Dict[str, str]:
    """
    Get available node types and their descriptions
    
    Returns:
        Dict[str, str]: Mapping of node types to descriptions
    """
    return NODE_TYPES
