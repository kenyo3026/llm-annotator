"""
FastMCP-based MCP interface for LLM Tag Annotator

This module provides the MCP (Model Context Protocol) interface for the annotator.
It supports both stdio and streamable-http transports.
"""

import argparse
from typing import Optional
from dataclasses import asdict

from fastmcp import FastMCP

from .main import Main
from .annotator import AnnotationResponse
from .annotator.base import AnnotationResponseMetadata, AnnotationResponseStatus
from .utils import resolve_config_path


def create_mcp_server(config_path: str = "configs/config.yaml") -> FastMCP:
    """
    Create and configure FastMCP server

    Args:
        config_path: Path to configuration file

    Returns:
        Configured FastMCP server instance
    """
    # Resolve config path
    config_path = resolve_config_path(config_path)

    # Initialize MCP server
    mcp = FastMCP("LLM Annotator")

    # Initialize Main instance
    main = Main(config_path=config_path)

    # Register tool: annotate
    @mcp.tool()
    def annotate(
        context: str,
        annotator: Optional[str] = None,
        model: Optional[str] = None
    ) -> dict:
        """
        Annotate text with tags using LLM

        Args:
            context: Text context to annotate
            annotator: Annotator name to use (default: first annotator in config)
            model: Model name to use (default: first model in config)

        Returns:
            Dictionary with tags, status, and metadata
        """
        try:
            response: AnnotationResponse = main.annotate(
                context=context,
                annotator_name=annotator,
                model_name=model
            )

            # Convert to dict for JSON serialization
            return asdict(response)

        except Exception as e:
            # Return error as AnnotationResponse for consistency
            error_response = AnnotationResponse(
                tags=[],
                status=AnnotationResponseStatus.failed,
                metadata=AnnotationResponseMetadata(error=str(e))
            )
            return asdict(error_response)

    # Register resource: list annotators
    @mcp.resource("annotator://annotators")
    def get_annotators() -> str:
        """
        List all available annotators

        Returns:
            JSON string with list of annotator names
        """
        import json
        annotators = main.list_annotators()
        return json.dumps({"annotators": annotators}, indent=2)

    # Register resource: list models
    @mcp.resource("annotator://models")
    def get_models() -> str:
        """
        List all available models

        Returns:
            JSON string with list of model names
        """
        import json
        models = main.list_models()
        return json.dumps({"models": models}, indent=2)

    return mcp


def main():
    """
    Main entry point for annotator-mcp command
    """
    parser = argparse.ArgumentParser(
        description="Run LLM Tag Annotator MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with stdio transport (for local tools like Claude Desktop)
  annotator-mcp --transport stdio

  # Run with streamable-http transport (for remote deployment)
  annotator-mcp --transport streamable-http --port 8001

  # Use custom config file
  annotator-mcp -c configs/custom.yaml --transport stdio
"""
    )

    parser.add_argument(
        "-c", "--config",
        default="configs/config.yaml",
        help="Path to configuration file (default: configs/config.yaml)"
    )

    parser.add_argument(
        "--transport",
        choices=["stdio", "streamable-http"],
        default="stdio",
        help="Transport protocol to use (default: stdio)"
    )

    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to for streamable-http (default: 0.0.0.0)"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8001,
        help="Port to bind to for streamable-http (default: 8001)"
    )

    parser.add_argument(
        "--path",
        default="/mcp",
        help="Path for streamable-http endpoint (default: /mcp)"
    )

    args = parser.parse_args()

    try:
        # Create MCP server
        mcp = create_mcp_server(config_path=args.config)

        # Run server with specified transport
        if args.transport == "stdio":
            # NOTE: In stdio mode, we MUST NOT print anything to stdout
            # as it will interfere with JSON-RPC communication
            # Disable banner in stdio mode to prevent JSON-RPC errors
            mcp.run(transport="stdio", show_banner=False)
        else:
            print(f"🚀 Starting MCP server with streamable-http transport...", flush=True)
            print(f"   Host: {args.host}", flush=True)
            print(f"   Port: {args.port}", flush=True)
            print(f"   Path: {args.path}", flush=True)
            mcp.run(
                transport="streamable-http",
                host=args.host,
                port=args.port,
                path=args.path
            )

    except FileNotFoundError as e:
        # Use stderr for error messages in stdio mode
        import sys
        print(f"❌ Error: {e}", file=sys.stderr, flush=True)
        return 1
    except Exception as e:
        import sys
        import traceback
        print(f"❌ Error: {e}", file=sys.stderr, flush=True)
        traceback.print_exc(file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
