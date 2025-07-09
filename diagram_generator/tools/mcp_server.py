"""
MCP server that wraps diagram generation tools
"""
import atexit
import logging
from typing import Dict, Literal, Optional

from fastmcp import FastMCP
from pydantic import BaseModel, Field

from . import mcp_tools

# Configure logging to use uppercase log levels to avoid MCP validation errors
log_level = "INFO"
logging.basicConfig(level=getattr(logging, log_level, logging.INFO))

# MCP server instance
mcp = FastMCP("diagram-tools")


class CanvasInfoResponse(BaseModel):
    """Information about a diagram canvas"""
    canvas_id: str = Field(..., description="Unique canvas identifier")
    title: str = Field(..., description="Canvas title")
    node_count: int = Field(..., description="Number of nodes on canvas")
    cluster_count: int = Field(..., description="Number of clusters on canvas")


class NodeInfoResponse(BaseModel):
    """Information about a node on a canvas"""
    node_id: str = Field(..., description="Node identifier")
    node_type: str = Field(..., description="Type of the node")


class ClusterInfoResponse(BaseModel):
    """Information about a cluster on a canvas"""
    cluster_id: str = Field(..., description="Cluster identifier")
    cluster_name: str = Field(..., description="Display name of the cluster")


# Register a cleanup function to run on exit
atexit.register(mcp_tools.cleanup_all_temp_files)


@mcp.tool()
def create_canvas() -> str:
    """
    Create a new diagram canvas

    Returns:
        str: ID of the created canvas
    """
    return mcp_tools.create_canvas()


@mcp.tool()
def create_cluster(canvas_id: str, cluster_id: str, cluster_name: str) -> None:
    """
    Create a cluster/submodule to group related services
    
    Args:
        canvas_id: Target canvas identifier
        cluster_id: Unique identifier for the cluster
        cluster_name: Display name for the cluster
    """
    mcp_tools.create_cluster(canvas_id, cluster_id, cluster_name)


@mcp.tool()
def add_node(
        canvas_id: str,
        node_id: str,
        node_type: Literal[
            # Compute Services
            "compute_ec2", "compute_ecs", "compute_lambda", "compute_fargate",
                # Database Services
            "database_rds", "database_dynamodb", "database_elasticache", "database_aurora",
                # Network & API Services
            "network_alb", "network_nlb", "network_cloudfront", "network_route53",
            "network_api_gateway", "network_api_gateway_v2",
                # Storage Services
            "storage_s3", "storage_efs",
                # Messaging & Queue Services
            "messaging_sqs", "messaging_sns", "messaging_eventbridge", "messaging_kinesis",
                # Monitoring & Logging
            "monitoring_cloudwatch", "monitoring_xray", "monitoring_cloudtrail",
                # Security & Identity
            "security_iam", "security_cognito", "security_secrets_manager",
                # Container & Orchestration
            "container_eks", "container_ecr",
                # Integration Services
            "integration_step_functions", "integration_app_sync"
        ],
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
    """
    mcp_tools.add_node(canvas_id, node_id, node_type, label, cluster_id)


@mcp.tool()
def add_edge(canvas_id: str, source_node_id: str, target_node_id: str) -> None:
    """
    Connect two existing nodes on the same canvas with a directed edge
    
    Args:
        canvas_id: Target canvas identifier
        source_node_id: Source node identifier
        target_node_id: Target node identifier
    """
    mcp_tools.add_edge(canvas_id, source_node_id, target_node_id)


@mcp.tool()
def list_canvas_nodes(canvas_id: str) -> Dict[str, NodeInfoResponse]:
    """
    List all nodes present on a specific canvas
    
    Args:
        canvas_id: Target canvas identifier
        
    Returns:
        Dict[str, NodeInfoResponse]: Dictionary mapping node IDs to their information
    """
    nodes_info = mcp_tools.list_canvas_nodes(canvas_id)
    return {
        node_id: NodeInfoResponse(
            node_id=info["node_id"],
            node_type=info["node_type"]
        )
        for node_id, info in nodes_info.items()
    }


@mcp.tool()
def list_canvas_clusters(canvas_id: str) -> Dict[str, ClusterInfoResponse]:
    """
    List all clusters present on a specific canvas
    
    Args:
        canvas_id: Target canvas identifier
        
    Returns:
        Dict[str, ClusterInfoResponse]: Dictionary mapping cluster IDs to their information
    """
    clusters_info = mcp_tools.list_canvas_clusters(canvas_id)
    return {
        cluster_id: ClusterInfoResponse(
            cluster_id=info["cluster_id"],
            cluster_name=info["cluster_name"]
        )
        for cluster_id, info in clusters_info.items()
    }


@mcp.tool()
def get_canvas_info(canvas_id: str) -> CanvasInfoResponse:
    """
    Get information about a specific canvas
    
    Args:
        canvas_id: Target canvas identifier
        
    Returns:
        CanvasInfoResponse: Canvas information
    """
    info = mcp_tools.get_canvas_info(canvas_id)
    return CanvasInfoResponse(
        canvas_id=info["canvas_id"],
        title=info["title"],
        node_count=info["node_count"],
        cluster_count=info["cluster_count"]
    )


@mcp.tool()
def render_diagram(canvas_id: str) -> str:
    """
    Render the canvas to a PNG image file and return the file path
    
    Args:
        canvas_id: Target canvas identifier
        
    Returns:
        str: Path to the generated PNG file
    """
    return mcp_tools.render_diagram(canvas_id)


@mcp.tool()
def clear_canvas(canvas_id: str) -> None:
    """
    Clear all nodes and clusters from a canvas
    
    Args:
        canvas_id: Target canvas identifier
    """
    mcp_tools.clear_canvas(canvas_id)


@mcp.tool()
def get_available_node_types() -> Dict[str, str]:
    """
    Get available node types and their descriptions
    
    Returns:
        Dict[str, str]: Mapping of node types to descriptions
    """
    return mcp_tools.get_available_node_types()


# Function to get the MCP server instance
def get_mcp_server() -> FastMCP:
    """
    Get the MCP server instance
    
    Returns:
        FastMCP: MCP server instance
    """
    return mcp
