"""
Diagram agent for generating architecture diagrams using Gemini API
"""
import json
import logging
import os
from typing import Dict, Any, Optional

from dotenv import load_dotenv

from ..api.models import DiagramRequest, DiagramResponse, ToolCall
from ..core.config import settings
from ..core.constants import MICROSERVICES_PATTERNS, NODE_TYPES
from ..tools import mcp_tools
from ..utils import GeminiClient

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DiagramAgent:
    """
    Agent that uses Gemini API to generate architecture diagrams via MCP tools
    All prompt logic is explicitly defined and documented
    """

    def __init__(self, gemini_api_key: Optional[str] = None):
        """
        Initialize the diagram agent
        
        Args:
            gemini_api_key: Google Gemini API key
        """
        # Get an API key from multiple sources
        self.gemini_api_key = self._get_api_key(gemini_api_key)

        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required but not found in environment variables")

        self.gemini_client = GeminiClient(self.gemini_api_key)

        # Available tools from the MCP server with cluster support
        self.available_tools = {
            "create_canvas": {
                "description": "Create a new empty diagram canvas for building architecture diagrams. This tool wraps an internal library; do not reference that library.",
                "parameters": {
                    "title": {"type": "string",
                              "description": "Title for the diagram canvas - use descriptive architecture names like 'Basic Web Application' or 'Microservices Architecture'",
                              "required": True}
                }
            },
            "create_cluster": {
                "description": "Create a cluster/submodule to group related services (e.g., 'Routing', 'Web Tier', 'Shared Infra'). This tool wraps an internal library; do not reference that library.",
                "parameters": {
                    "canvas_id": {"type": "string", "description": "Target canvas identifier"},
                    "cluster_id": {"type": "string", "description": "Unique identifier for the cluster"},
                    "cluster_name": {"type": "string", "description": "Display name for the cluster"}
                }
            },
            "add_node": {
                "description": "Add a node of the specified type to an existing canvas or cluster. This tool wraps an internal library; do not reference that library.",
                "parameters": {
                    "canvas_id": {"type": "string", "description": "Target canvas identifier"},
                    "node_id": {"type": "string", "description": "Unique identifier for the new node"},
                    "node_type": {
                        "type": "string",
                        "enum": ["api_gateway", "load_balancer", "service", "database", "queue", "monitoring"],
                        "description": "Type of node to create from available options"
                    },
                    "label": {"type": "string", "description": "Optional custom label for the node"},
                    "cluster_id": {"type": "string", "description": "Optional cluster to add the node to"}
                }
            },
            "add_edge": {
                "description": "Connect two existing nodes on the same canvas with a directed edge. This tool wraps an internal library; do not reference that library.",
                "parameters": {
                    "canvas_id": {"type": "string", "description": "Target canvas identifier"},
                    "source_node_id": {"type": "string", "description": "Source node identifier"},
                    "target_node_id": {"type": "string", "description": "Target node identifier"}
                }
            },
            "render_diagram": {
                "description": "Render the canvas to a PNG image file and return the file path. This tool wraps an internal library; do not reference that library.",
                "parameters": {
                    "canvas_id": {"type": "string", "description": "Target canvas identifier"}
                }
            }
        }

        logger.info(f"Diagram agent initialized with API key: {self.gemini_api_key[:10]}...")

    def _get_api_key(self, provided_key: Optional[str] = None) -> Optional[str]:
        """
        Get API key from multiple sources with fallback
        
        Args:
            provided_key: Optional provided API key
            
        Returns:
            Optional[str]: API key or None if not found
        """
        # Try provided key first
        if provided_key and provided_key.strip():
            return provided_key.strip()

        # Try settings
        if settings.GEMINI_API_KEY:
            return settings.GEMINI_API_KEY

        # Try multiple environment variable names
        possible_keys = [
            "GEMINI_API_KEY",
            "GOOGLE_API_KEY",
            "GOOGLE_GEMINI_API_KEY"
        ]

        for key_name in possible_keys:
            api_key = os.getenv(key_name)
            if api_key and api_key.strip():
                return api_key.strip()

        return None

    def _build_system_prompt(self) -> str:
        """
        Build the system prompt for the LLM with microservices expertise
        All prompt logic is explicit and documented
        """
        # EXPLICIT PROMPT LOGIC: Define the agent's role and microservices expertise
        mini_example = [
            {"name": "create_canvas", "args": {"title": "Microservices Architecture"}},
            {"name": "create_cluster",
             "args": {"canvas_id": "CANVAS_ID", "cluster_id": "routing", "cluster_name": "Routing"}},
            {"name": "create_cluster",
             "args": {"canvas_id": "CANVAS_ID", "cluster_id": "services", "cluster_name": "Microservices"}},
            {"name": "create_cluster",
             "args": {"canvas_id": "CANVAS_ID", "cluster_id": "infra", "cluster_name": "Shared Infra"}},
            {"name": "add_node",
             "args": {"canvas_id": "CANVAS_ID", "node_id": "routing_api_gateway", "node_type": "api_gateway",
                      "cluster_id": "routing", "label": "API Gateway"}},
            {"name": "add_node", "args": {"canvas_id": "CANVAS_ID", "node_id": "services_auth", "node_type": "service",
                                          "cluster_id": "services", "label": "Authentication Service"}},
            {"name": "add_node", "args": {"canvas_id": "CANVAS_ID", "node_id": "services_order", "node_type": "service",
                                          "cluster_id": "services", "label": "Order Service"}},
            {"name": "add_node",
             "args": {"canvas_id": "CANVAS_ID", "node_id": "services_payment", "node_type": "service",
                      "cluster_id": "services", "label": "Payment Service"}},
            {"name": "add_node",
             "args": {"canvas_id": "CANVAS_ID", "node_id": "infra_rds", "node_type": "database", "cluster_id": "infra",
                      "label": "RDS Database"}},
            {"name": "add_node",
             "args": {"canvas_id": "CANVAS_ID", "node_id": "infra_sqs", "node_type": "queue", "cluster_id": "infra",
                      "label": "SQS Queue"}},
            {"name": "add_node",
             "args": {"canvas_id": "CANVAS_ID", "node_id": "infra_cloudwatch", "node_type": "monitoring",
                      "cluster_id": "infra", "label": "CloudWatch"}},
            {"name": "add_edge", "args": {"canvas_id": "CANVAS_ID", "source_node_id": "routing_api_gateway",
                                          "target_node_id": "services_auth"}},
            {"name": "add_edge",
             "args": {"canvas_id": "CANVAS_ID", "source_node_id": "services_auth", "target_node_id": "infra_sqs"}},
            {"name": "add_edge",
             "args": {"canvas_id": "CANVAS_ID", "source_node_id": "services_order", "target_node_id": "infra_rds"}},
            {"name": "add_edge", "args": {"canvas_id": "CANVAS_ID", "source_node_id": "services_payment",
                                          "target_node_id": "infra_cloudwatch"}},
            {"name": "render_diagram", "args": {"canvas_id": "CANVAS_ID"}}
        ]

        # Use tightened node types from constants
        core_node_types = NODE_TYPES

        system_prompt = f'''YOU ARE A DIAGRAM TOOL AGENT.
You must:
- Think step-by-step.
- Call the provided tools only.
- Never output source code or mention the underlying library.

You are an expert cloud architecture and microservices diagram generator. You specialize in creating visual representations of complex distributed systems, microservices architectures, and cloud infrastructure. Never output raw code or instructions to write code.

AVAILABLE TOOLS:
{json.dumps(self.available_tools, indent=2)}

SUPPORTED NODE TYPES (tightened enumeration):
{json.dumps(core_node_types, indent=2)}

        VISUAL STYLE GUIDELINES:
Flow Left to Right, three columns
1. Routing (API Gateway, ALB)
2. Services (Web Tier or Microservices cluster)
3. Shared Infrastructure (database, queue, monitoring)

EXAMPLE TASK: If user asks for "a microservices architecture with authentication, payment, and order services", respond with:
{json.dumps(mini_example, indent=2)}

BUSINESS LOGIC:
- Create clusters for logical grouping
- Use clear, descriptive labels
- Services must connect to shared infrastructure
- API Gateway routes traffic to services
- Include monitoring for production readiness

CONSTRAINTS:
- Never output raw code
- Only use the 6 provided node types
- All services must connect to shared infrastructure
- Canvas IDs are placeholders - use "CANVAS_ID" in your tool calls
- Always render the diagram as the final step

SAFETY RULES:
- Never reference the underlying library
- Never output code or installation instructions
- Use only the provided tool calls
- If you cannot satisfy a request with the available tools, explain limitations politely

You must output JSON in this format:
{{
  "reasoning": "Brief explanation of architecture choices",
  "tool_calls": [
    // Array of tool calls as shown in the example
  ]
}}'''

        return system_prompt

    def _extract_allowed_components(self, description: str) -> set:
        """
        Extract allowed components from the description using simple keyword matching

        Args:
            description: User's description of the architecture

        Returns:
            set: Set of allowed component types
        """
        # NORMALIZED KEYWORD MATCHING: Map synonyms to node types to increase recall
        synonyms = {
            "api_gateway": ["api gateway", "gateway"],
            "load_balancer": ["load balancer", "alb", "application load balancer", "nlb"],
            "service": ["service", "microservice", "server", "ec2", "ecs", "lambda"],
            "database": ["database", "rds", "aurora", "db", "dynamodb"],
            "queue": ["queue", "sqs", "sns", "kinesis", "eventbridge"],
            "monitoring": ["monitoring", "cloudwatch", "logging", "observability", "xray", "cloudtrail"]
        }

        allowed_components = set()
        description_lower = description.lower()

        for component, keywords in synonyms.items():
            if any(word in description_lower for word in keywords):
                allowed_components.add(component)

        # Always include core components so the diagram is at least functional
        default_components = {"api_gateway", "service", "database", "queue", "monitoring", "load_balancer"}
        allowed_components.update(default_components)

        logger.info(f"Extracted components from description: {allowed_components}")
        return allowed_components

    def _build_user_prompt(self, request: DiagramRequest) -> str:
        """
        Build the user prompt for the specific request
        
        Args:
            request: Diagram generation request
            
        Returns:
            str: User prompt for the LLM
        """
        # EXPLICIT PROMPT LOGIC: Structure the user request with context
        user_prompt = f"""Please generate a microservices architecture diagram for the following requirements:

DESCRIPTION: {request.description}

REQUIREMENTS:
- Use the available tools to create a complete diagram
- Follow the visual style guidelines (left-to-right flow)
- Create logical clusters for grouping related components
- Ensure all services connect to shared infrastructure
- Include monitoring and observability components
- Use clear, descriptive labels for all components
- Render the final diagram

Remember: You are a diagram tool agent. Only use the provided tools. Never output code or reference the underlying library. Your output must be valid JSON with reasoning and tool_calls.

Generate the diagram now."""

        return user_prompt

    def _standardize_cluster_name(self, cluster_name: str) -> str:
        """
        Standardize cluster names for consistency
        
        Args:
            cluster_name: Original cluster name
            
        Returns:
            str: Standardized cluster name
        """
        # EXPLICIT STANDARDIZATION: Map variations to standard names
        standardization_map = {
            "microservices": "Microservices",
            "services": "Microservices",
            "web tier": "Web Tier",
            "web": "Web Tier",
            "routing": "Routing",
            "shared infra": "Shared Infra",
            "shared infrastructure": "Shared Infra",
            "infrastructure": "Shared Infra",
            "infra": "Shared Infra",
            "data": "Data Layer",
            "data layer": "Data Layer",
            "cache": "Cache Layer",
            "cache layer": "Cache Layer"
        }

        # Normalize the cluster name
        normalized = cluster_name.lower().strip()
        return standardization_map.get(normalized, cluster_name)

    def _validate_tool_call(self, tool_call: Dict[str, Any]) -> bool:
        """
        Validate a tool call against the available tools
        
        Args:
            tool_call: Tool call to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        # EXPLICIT VALIDATION: Check tool call structure and parameters
        if not isinstance(tool_call, dict):
            return False

        tool_name = tool_call.get("name")
        if not tool_name or tool_name not in self.available_tools:
            return False

        args = tool_call.get("args", {})
        if not isinstance(args, dict):
            return False

        # Check required parameters for each tool
        required_params = {
            "create_canvas": ["title"],
            "create_cluster": ["canvas_id", "cluster_id", "cluster_name"],
            "add_node": ["canvas_id", "node_id", "node_type"],
            "add_edge": ["canvas_id", "source_node_id", "target_node_id"],
            "render_diagram": ["canvas_id"]
        }

        for param in required_params.get(tool_name, []):
            if param not in args:
                return False

        return True

    def _check_duplicate_node(self, canvas_id: str, node_id: str) -> bool:
        """
        Check if a node already exists in the canvas
        
        Args:
            canvas_id: Canvas identifier
            node_id: Node identifier to check
            
        Returns:
            bool: True if duplicate, False otherwise
        """
        # This is a simplified check - in a full implementation,
        # we would track created nodes more comprehensively
        return False

    def _enforce_shared_edges(
            self,
            canvas_id: str,
            created_nodes: Optional[Dict[str, str]] = None,
            existing_edges: Optional[set[tuple[str, str]]] = None
    ) -> None:
        """
        Ensure that each service node is connected to all shared infrastructure nodes (database, queue, monitoring)

        Args:
            canvas_id: Canvas identifier
            created_nodes: Mapping of node_id to node_type created during generation
        """
        try:
            # If no created_nodes info provided, skip enforcement to preserve backward compatibility
            if not created_nodes:
                logger.debug("No created_nodes map provided, skipping shared edge enforcement")
                return

            # Identify service and shared infra nodes using the map provided
            service_nodes = [n for n, t in created_nodes.items() if t == "service"]
            shared_nodes = [n for n, t in created_nodes.items() if t in {"database", "queue", "monitoring"}]

            # Connect routing nodes (API Gateway / Load Balancer) to every service
            routing_nodes = [n for n, t in created_nodes.items() if t in {"api_gateway", "load_balancer"}]

            existing_edges = existing_edges or set()

            for route in routing_nodes:
                for svc in service_nodes:
                    if (route, svc) in existing_edges:
                        continue
                    try:
                        mcp_tools.add_edge(canvas_id, route, svc)
                        existing_edges.add((route, svc))
                    except Exception as e:
                        logger.debug(f"Edge {route}->{svc} not added: {e}")

            # Connect each service node to every shared node if not already connected
            for svc in service_nodes:
                for shared in shared_nodes:
                    if (svc, shared) in existing_edges:
                        continue
                    try:
                        mcp_tools.add_edge(canvas_id, svc, shared)
                        existing_edges.add((svc, shared))
                    except Exception as e:
                        logger.debug(f"Edge {svc}->{shared} not added: {e}")

            # Make monitoring more prominent: connect monitoring to all services and API Gateway
            monitoring_nodes = [n for n, t in created_nodes.items() if t == "monitoring"]
            for mon in monitoring_nodes:
                for node in service_nodes + routing_nodes:
                    if (node, mon) in existing_edges:
                        continue
                    try:
                        mcp_tools.add_edge(canvas_id, node, mon)
                        existing_edges.add((node, mon))
                    except Exception as e:
                        logger.debug(f"Edge {node}->{mon} not added: {e}")
        except Exception as e:
            logger.warning(f"Failed to enforce shared edges: {e}")

    async def _call_mcp_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call an MCP tool with the given arguments
        
        Args:
            tool_name: Name of the tool to call
            args: Arguments for the tool
            
        Returns:
            Dict[str, Any]: Tool response
        """
        try:
            # EXPLICIT TOOL ROUTING: Route to appropriate MCP tool functions
            if tool_name == "create_canvas":
                canvas_id = mcp_tools.create_canvas(args["title"])
                return {"result": canvas_id}
            elif tool_name == "create_cluster":
                mcp_tools.create_cluster(
                    args["canvas_id"],
                    args["cluster_id"],
                    args["cluster_name"]
                )
                return {"result": "Cluster created successfully"}
            elif tool_name == "add_node":
                mcp_tools.add_node(
                    args["canvas_id"],
                    args["node_id"],
                    args["node_type"],
                    args.get("label"),
                    args.get("cluster_id")
                )
                return {"result": "Node added successfully"}
            elif tool_name == "add_edge":
                mcp_tools.add_edge(
                    args["canvas_id"],
                    args["source_node_id"],
                    args["target_node_id"]
                )
                return {"result": "Edge added successfully"}
            elif tool_name == "render_diagram":
                result = mcp_tools.render_diagram(args["canvas_id"])
                return {"result": result}
            else:
                raise ValueError(f"Unknown tool: {tool_name}")

        except Exception as e:
            logger.error(f"Error calling MCP tool {tool_name}: {e}")
            return {"error": str(e)}

    async def generate_diagram(self, request: DiagramRequest) -> DiagramResponse:
        """
        Generate a microservices architecture diagram based on the request
        
        Args:
            request: Diagram generation request
            
        Returns:
            DiagramResponse: Response with generated diagram information
        """
        try:
            # Extract allowed components from description
            allowed_components = self._extract_allowed_components(request.description)
            description_lower = request.description.lower()
            monitoring_requested = any(word in description_lower for word in [
                "monitoring", "cloudwatch", "observability", "xray", "logging"
            ])
            logger.info(f"Allowed components: {allowed_components}")

            # Build prompts with microservices expertise
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(request)

            # Combine prompts
            full_prompt = f"{system_prompt}\n\n{user_prompt}"

            # Generate response from Gemini
            response = await self.gemini_client.generate_json_response(full_prompt)

            reasoning = response.get("reasoning", "")
            tool_calls = response.get("tool_calls", [])

            logger.info(f"Generated {len(tool_calls)} tool calls for microservices architecture")
            logger.info(f"Reasoning: {reasoning}")

            # Execute tool calls with validation
            canvas_id = None
            image_path = None
            created_nodes: Dict[str, str] = {}  # Track nodes and their types
            existing_edges: set[tuple[str, str]] = set()

            for tool_call in tool_calls:
                # Validate tool call at runtime
                if not self._validate_tool_call(tool_call):
                    logger.warning(f"Invalid tool call, skipping: {tool_call}")
                    continue

                tool_name = tool_call.get("name")
                args = tool_call.get("args", {})

                # Replace CANVAS_ID placeholder with actual canvas ID
                if canvas_id and "canvas_id" in args and args["canvas_id"] == "CANVAS_ID":
                    args["canvas_id"] = canvas_id

                # Standardize cluster names
                if tool_name == "create_cluster" and "cluster_name" in args:
                    args["cluster_name"] = self._standardize_cluster_name(args["cluster_name"])

                # Filter components not in allowed set
                if tool_name == "add_node":
                    node_type = args.get("node_type", "")
                    node_id = args.get("node_id", "")

                    # Do not add monitoring nodes unless explicitly requested
                    if node_type == "monitoring" and not monitoring_requested:
                        logger.info(f"Skipping monitoring node {node_id} - not requested in description")
                        continue

                    # Check if node type is allowed
                    if node_type not in allowed_components:
                        logger.info(f"Skipping node {node_id} with type {node_type} - not in allowed components")
                        continue

                    # Check for duplicate nodes
                    if canvas_id and self._check_duplicate_node(canvas_id, node_id):
                        continue

                # Filter edges that reference non-existent nodes
                if tool_name == "add_edge":
                    source_node_id = args.get("source_node_id", "")
                    target_node_id = args.get("target_node_id", "")

                    # Ensure both nodes were created to prevent invalid edges
                    if source_node_id not in created_nodes or target_node_id not in created_nodes:
                        logger.info(
                            f"Skipping edge from {source_node_id} to {target_node_id} - node(s) not created")
                        continue

                    existing_edges.add((source_node_id, target_node_id))
                    logger.info(f"Edge {source_node_id}->{target_node_id} recorded in existing_edges")

                logger.info(f"Calling tool: {tool_name} with args: {args}")

                result = await self._call_mcp_tool(tool_name, args)

                if "error" in result:
                    logger.error(f"Tool call failed: {result['error']}")
                    return DiagramResponse(
                        success=False,
                        error=f"Tool call failed: {result['error']}",
                        reasoning=reasoning
                    )

                # Handle specific tool responses
                if tool_name == "create_canvas":
                    canvas_id = result["result"]
                    logger.info(f"Canvas created with ID: {canvas_id}")

                elif tool_name == "add_node":
                    node_id = args.get("node_id", "")
                    node_type = args.get("node_type", "")
                    if node_id:
                        created_nodes[node_id] = node_type
                        logger.info(f"Node {node_id} of type {node_type} added to created_nodes map")

                elif tool_name == "render_diagram":
                    image_path = result["result"]
                    logger.info(f"Diagram rendered to: {image_path}")

            # Post-processor: Ensure all services are connected to all shared components
            if canvas_id:
                self._enforce_shared_edges(canvas_id, created_nodes, existing_edges)

                # Re-render diagram to capture any new edges added by enforcement logic
                try:
                    result_path = mcp_tools.render_diagram(canvas_id)
                    if isinstance(result_path, str) and result_path:
                        image_path = result_path
                    logger.info(f"Diagram re-rendered after enforcement to: {result_path}")
                except Exception as e:
                    logger.error(f"Re-render after enforcement failed: {e}")

            if not image_path and created_nodes:
                # Attempt second render in case of slow file write or missing render call
                try:
                    image_path = mcp_tools.render_diagram(canvas_id)
                except Exception as e:
                    logger.error(f"Second render attempt failed: {e}")

                if not image_path:
                    return DiagramResponse(
                        success=False,
                        error="No diagram was rendered",
                        reasoning=reasoning
                    )

            # Final safety check – if still no image_path, treat as failure
            if not image_path:
                return DiagramResponse(
                    success=False,
                    error="No diagram was rendered",
                    reasoning=reasoning
                )

            # Return successful response
            return DiagramResponse(
                success=True,
                image_path=image_path,
                reasoning=reasoning,
                tool_calls=[
                    ToolCall(name=call.get("name", ""), args=call.get("args", {}))
                    for call in tool_calls
                ]
            )

        except Exception as e:
            logger.error(f"Error generating diagram: {e}")
            return DiagramResponse(
                success=False,
                error=str(e),
                reasoning="Error occurred during diagram generation"
            )


async def create_diagram_agent(api_key: Optional[str] = None) -> Optional[DiagramAgent]:
    """
    Create a diagram agent instance
    
    Args:
        api_key: Optional Gemini API key
        
    Returns:
        Optional[DiagramAgent]: Agent instance or None if no API key
    """
    try:
        # Use provided key or get from settings
        effective_key = api_key or settings.GEMINI_API_KEY

        if not effective_key:
            logger.error("No GEMINI_API_KEY found in environment variables")
            return None

        return DiagramAgent(effective_key)

    except Exception as e:
        logger.error(f"Error creating diagram agent: {e}")
        return None
