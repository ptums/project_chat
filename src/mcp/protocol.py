"""
JSON-RPC 2.0 protocol handler for MCP.

Handles MCP protocol messages over stdio.
"""
import json
import sys
import logging
from typing import Dict, Any, Optional, Callable

logger = logging.getLogger(__name__)

# MCP Protocol version
MCP_PROTOCOL_VERSION = "2024-11-05"


class MCPProtocolHandler:
    """Handler for MCP JSON-RPC 2.0 protocol over stdio."""
    
    def __init__(self):
        """Initialize protocol handler."""
        self.methods: Dict[str, Callable] = {}
        self.initialized = False
        self.capabilities = {}
    
    def register_method(self, method_name: str, handler: Callable):
        """
        Register a method handler.
        
        Args:
            method_name: Method name (e.g., "resources/list")
            handler: Callable that handles the method
        """
        self.methods[method_name] = handler
    
    def send_response(self, request_id: Any, result: Optional[Dict[str, Any]] = None, error: Optional[Dict[str, Any]] = None):
        """
        Send JSON-RPC response.
        
        Args:
            request_id: Request ID from original request
            result: Result data (if success)
            error: Error data (if error)
        """
        response = {
            "jsonrpc": "2.0",
            "id": request_id
        }
        
        if error:
            response["error"] = error
        else:
            response["result"] = result or {}
        
        response_json = json.dumps(response) + "\n"
        sys.stdout.write(response_json)
        sys.stdout.flush()
    
    def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle initialize request.
        
        Args:
            params: Initialize parameters
            
        Returns:
            Initialize result with capabilities
        """
        protocol_version = params.get("protocolVersion")
        client_info = params.get("clientInfo", {})
        
        logger.info(f"Initializing MCP server for client: {client_info.get('name', 'unknown')}")
        
        self.initialized = True
        self.capabilities = {
            "resources": {},
            "tools": {}
        }
        
        return {
            "protocolVersion": MCP_PROTOCOL_VERSION,
            "capabilities": self.capabilities,
            "serverInfo": {
                "name": "meditation-notes-mcp",
                "version": "1.0.0"
            }
        }
    
    def handle_request(self, request: Dict[str, Any]):
        """
        Handle a JSON-RPC request.
        
        Args:
            request: JSON-RPC request dict
        """
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})
        
        try:
            # Handle initialize specially
            if method == "initialize":
                if self.initialized:
                    self.send_response(request_id, error={
                        "code": -32000,
                        "message": "Server already initialized"
                    })
                    return
                
                result = self.handle_initialize(params)
                self.send_response(request_id, result=result)
                return
            
            # Check if initialized
            if not self.initialized and method != "initialize":
                self.send_response(request_id, error={
                    "code": -32002,
                    "message": "Server not initialized"
                })
                return
            
            # Handle initialized notification
            if method == "initialized":
                logger.info("Client initialized")
                return
            
            # Handle shutdown
            if method == "shutdown":
                logger.info("Shutdown requested")
                self.send_response(request_id, result={})
                sys.exit(0)
            
            # Handle registered methods
            if method in self.methods:
                handler = self.methods[method]
                result = handler(params)
                self.send_response(request_id, result=result)
            else:
                self.send_response(request_id, error={
                    "code": -32601,
                    "message": f"Method not found: {method}"
                })
                
        except Exception as e:
            logger.error(f"Error handling request {method}: {e}", exc_info=True)
            self.send_response(request_id, error={
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            })
    
    def run(self):
        """Run the protocol handler, reading from stdin."""
        logger.info("MCP server starting, reading from stdin...")
        
        try:
            for line in sys.stdin:
                line = line.strip()
                if not line:
                    continue
                
                try:
                    request = json.loads(line)
                    self.handle_request(request)
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON: {e}")
                    # Send error response
                    self.send_response(None, error={
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    })
                except Exception as e:
                    logger.error(f"Unexpected error: {e}", exc_info=True)
                    
        except KeyboardInterrupt:
            logger.info("Shutdown requested via interrupt")
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
            sys.exit(1)