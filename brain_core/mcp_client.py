"""
MCP (Model Context Protocol) client implementation.

Provides functionality to communicate with MCP servers via JSON-RPC 2.0 over stdio.
Supports resource discovery, resource reading, and tool invocation.
"""

import json
import logging
import os
import subprocess
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

# Protocol version
MCP_PROTOCOL_VERSION = "2024-11-05"

# Timeout constants (in seconds)
INITIALIZE_TIMEOUT = 2.0
RESOURCE_TIMEOUT = 0.5
TOOL_TIMEOUT = 1.0


class MCPClient:
    """
    Client for communicating with MCP servers via JSON-RPC 2.0 over stdio.
    
    Manages subprocess lifecycle, handles JSON-RPC communication, and provides
    methods for resource discovery, resource reading, and tool invocation.
    """
    
    def __init__(self, server_name: str, command: str, args: List[str], env: Optional[Dict[str, str]] = None, cwd: Optional[str] = None):
        """
        Initialize MCP client.
        
        Args:
            server_name: Name identifier for this server
            command: Command to start MCP server (e.g., "python")
            args: Command-line arguments for MCP server
            env: Environment variables for the server process
            cwd: Working directory for the server process (optional)
        """
        self.server_name = server_name
        self.command = command
        self.args = args
        self.env = env or {}
        self.cwd = cwd
        
        self.process: Optional[subprocess.Popen] = None
        self.initialized = False
        self.capabilities: Dict[str, Any] = {}
        self.last_error: Optional[tuple[float, str]] = None
        self.retry_count = 0
        self._request_id = 0
        self._lock = threading.Lock()
        
        # Resource cache
        self._resource_cache: Dict[str, Dict[str, Any]] = {}
        self._resource_list_cache: Optional[Dict[str, Any]] = None
        
    def _get_next_id(self) -> int:
        """Get next JSON-RPC request ID."""
        with self._lock:
            self._request_id += 1
            return self._request_id
    
    def _start_process(self) -> bool:
        """
        Start MCP server process.
        
        Returns:
            True if process started successfully, False otherwise
        """
        try:
            # Merge with current environment
            env = os.environ.copy()
            env.update(self.env)
            
            logger.debug(f"Starting MCP server '{self.server_name}' with command: {self.command} {' '.join(self.args)}")
            if self.cwd:
                logger.debug(f"Working directory: {self.cwd}")
            
            self.process = subprocess.Popen(
                [self.command] + self.args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                cwd=self.cwd,
                text=True,
                bufsize=1
            )
            
            # Give the process a moment to start and check if it's still alive
            time.sleep(0.1)
            
            if self.process.poll() is not None:
                # Process exited immediately - read stderr to see why
                stderr_output = ""
                try:
                    if self.process.stderr:
                        # Read all available stderr
                        import select
                        if hasattr(select, 'select'):
                            # Non-blocking read
                            ready, _, _ = select.select([self.process.stderr], [], [], 0.1)
                            if ready:
                                stderr_output = self.process.stderr.read(4096)  # Read up to 4KB
                        else:
                            # Fallback: blocking read with timeout
                            stderr_output = self.process.stderr.read(4096)
                except Exception as e:
                    logger.debug(f"Could not read stderr: {e}")
                
                error_msg = f"MCP server '{self.server_name}' exited immediately (exit code: {self.process.returncode})"
                if stderr_output:
                    error_msg += f"\nStderr: {stderr_output.strip()}"
                logger.error(error_msg)
                self.last_error = (time.time(), error_msg)
                self.process = None
                self.retry_count += 1
                return False
            
            logger.info(f"MCP server '{self.server_name}' process started (PID: {self.process.pid})")
            return True
            
        except FileNotFoundError as e:
            error_msg = f"Command not found: {self.command}. Is it installed and in PATH?"
            logger.error(error_msg)
            self.last_error = (time.time(), error_msg)
            self.retry_count += 1
            return False
        except Exception as e:
            error_msg = f"Failed to start MCP server '{self.server_name}': {e}"
            logger.error(error_msg, exc_info=True)
            self.last_error = (time.time(), error_msg)
            self.retry_count += 1
            return False
    
    def _stop_process(self):
        """Stop MCP server process gracefully."""
        if self.process:
            try:
                # Try graceful shutdown
                if self.process.stdin:
                    self.process.stdin.close()
                if self.process.stdout:
                    self.process.stdout.close()
                if self.process.stderr:
                    self.process.stderr.close()
                
                # Wait for process to terminate
                try:
                    self.process.wait(timeout=2.0)
                except subprocess.TimeoutExpired:
                    # Force kill if doesn't terminate
                    self.process.kill()
                    self.process.wait()
                
                logger.info(f"MCP server '{self.server_name}' process stopped")
            except Exception as e:
                logger.warning(f"Error stopping MCP server '{self.server_name}': {e}")
            finally:
                self.process = None
                self.initialized = False
    
    def _is_process_alive(self) -> bool:
        """Check if MCP server process is still running."""
        if not self.process:
            return False
        return self.process.poll() is None
    
    def _restart_process(self) -> bool:
        """
        Restart MCP server process with exponential backoff.
        
        Returns:
            True if restart successful, False otherwise
        """
        self._stop_process()
        
        # Exponential backoff: wait 2^retry_count seconds (max 60s)
        if self.retry_count > 0:
            wait_time = min(2 ** self.retry_count, 60)
            logger.info(f"Waiting {wait_time}s before restarting MCP server '{self.server_name}'")
            time.sleep(wait_time)
        
        return self._start_process()
    
    def _send_request(self, method: str, params: Optional[Dict[str, Any]] = None, timeout: float = 5.0) -> Optional[Dict[str, Any]]:
        """
        Send JSON-RPC request to MCP server.
        
        Args:
            method: JSON-RPC method name
            params: Method parameters
            timeout: Request timeout in seconds
            
        Returns:
            Response dict or None if error/timeout
        """
        if not self._is_process_alive():
            if not self._restart_process():
                return None
        
        request_id = self._get_next_id()
        request = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method
        }
        if params:
            request["params"] = params
        
        try:
            # Send request
            request_json = json.dumps(request) + "\n"
            if not self.process or not self.process.stdin:
                return None
            
            self.process.stdin.write(request_json)
            self.process.stdin.flush()
            
            # Read response with timeout
            if not self.process.stdout:
                return None
            
            # Read response line (with timeout handling via threading)
            response_line = None
            response_error = None
            stderr_output = None
            
            def read_response():
                nonlocal response_line, response_error, stderr_output
                try:
                    # Check if process is still alive first
                    if not self._is_process_alive():
                        # Process died - try to read stderr
                        if self.process and self.process.stderr:
                            try:
                                stderr_output = self.process.stderr.read()
                            except Exception:
                                pass
                        response_error = Exception("Process died during request")
                        return
                    
                    response_line = self.process.stdout.readline()
                    
                    # Also check stderr for any errors (non-blocking)
                    if self.process.stderr:
                        try:
                            # Try to read stderr if available (non-blocking)
                            import select
                            if hasattr(select, 'select'):
                                ready, _, _ = select.select([self.process.stderr], [], [], 0)
                                if ready:
                                    stderr_output = self.process.stderr.read()
                        except (ImportError, OSError):
                            # select not available or not supported (e.g., Windows)
                            pass
                except Exception as e:
                    response_error = e
            
            reader_thread = threading.Thread(target=read_response, daemon=True)
            reader_thread.start()
            reader_thread.join(timeout=timeout)
            
            if reader_thread.is_alive():
                logger.warning(f"Timeout waiting for response from MCP server '{self.server_name}'")
                # Check if process is still alive
                if not self._is_process_alive():
                    logger.error(f"MCP server '{self.server_name}' process died during request")
                return None
            
            if response_error:
                if stderr_output:
                    logger.error(f"MCP server '{self.server_name}' stderr: {stderr_output}")
                raise response_error
            
            if not response_line:
                if stderr_output:
                    logger.error(f"MCP server '{self.server_name}' stderr: {stderr_output}")
                return None
            
            response = json.loads(response_line.strip())
            
            # Check for errors
            if "error" in response:
                error = response["error"]
                error_msg = f"MCP server error: {error.get('message', 'Unknown error')}"
                logger.error(f"{error_msg} (code: {error.get('code', 'unknown')})")
                self.last_error = (time.time(), error_msg)
                return None
            
            # Verify response ID matches
            if response.get("id") != request_id:
                logger.warning(f"Response ID mismatch: expected {request_id}, got {response.get('id')}")
            
            return response.get("result")
            
        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse JSON response from MCP server '{self.server_name}': {e}"
            logger.error(error_msg)
            # Try to read stderr for more context
            if self.process and self.process.stderr:
                try:
                    stderr_content = self.process.stderr.read()
                    if stderr_content:
                        logger.error(f"Stderr output: {stderr_content}")
                except Exception:
                    pass
            self.last_error = (time.time(), error_msg)
            return None
        except Exception as e:
            error_msg = f"Error communicating with MCP server '{self.server_name}': {e}"
            logger.error(error_msg, exc_info=True)
            # Try to read stderr for more context
            if self.process and self.process.stderr:
                try:
                    stderr_content = self.process.stderr.read()
                    if stderr_content:
                        logger.error(f"Stderr output: {stderr_content}")
                except Exception:
                    pass
            self.last_error = (time.time(), error_msg)
            self.retry_count += 1
            return None
    
    def initialize(self) -> bool:
        """
        Initialize MCP protocol with server.
        
        Returns:
            True if initialization successful, False otherwise
        """
        if self.initialized:
            return True
        
        if not self._is_process_alive():
            if not self._start_process():
                return False
        
        params = {
            "protocolVersion": MCP_PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": {
                "name": "project_chat",
                "version": "1.0"
            }
        }
        
        result = self._send_request("initialize", params, timeout=INITIALIZE_TIMEOUT)
        
        if result:
            self.capabilities = result.get("capabilities", {})
            self.initialized = True
            self.retry_count = 0  # Reset retry count on successful init
            logger.info(f"MCP server '{self.server_name}' initialized successfully")
            return True
        else:
            logger.error(f"Failed to initialize MCP server '{self.server_name}'")
            return False
    
    def shutdown(self):
        """Shutdown MCP client and stop server process."""
        self._stop_process()
        logger.info(f"MCP client '{self.server_name}' shut down")
    
    def __enter__(self):
        """Context manager entry."""
        if not self.initialized:
            self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown()
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """
        List all available resources from MCP server.
        
        Returns:
            List of resource dictionaries with uri, name, description, mimeType
        """
        if not self.initialized:
            if not self.initialize():
                return []
        
        # Check cache first
        if self._resource_list_cache:
            cached_at = self._resource_list_cache.get("cached_at", 0)
            ttl = self._resource_list_cache.get("ttl", 60)
            if time.time() - cached_at < ttl:
                return self._resource_list_cache.get("resources", [])
        
        result = self._send_request("resources/list", timeout=RESOURCE_TIMEOUT)
        
        if result and "resources" in result:
            resources = result["resources"]
            # Cache the result
            self._resource_list_cache = {
                "resources": resources,
                "cached_at": time.time(),
                "ttl": 60  # 1 minute TTL
            }
            return resources
        
        return []
    
    def read_resource(self, uri: str) -> Optional[str]:
        """
        Read a specific resource from MCP server.
        
        Args:
            uri: Resource URI (e.g., "meditation://note/morning-meditation-2024-12-01")
            
        Returns:
            Resource content as string, or None if not found/error
        """
        if not self.initialized:
            if not self.initialize():
                return None
        
        # Check cache first
        if uri in self._resource_cache:
            cached = self._resource_cache[uri]
            cached_at = cached.get("cached_at", 0)
            ttl = cached.get("ttl", 300)
            if time.time() - cached_at < ttl:
                return cached.get("content")
        
        result = self._send_request("resources/read", {"uri": uri}, timeout=RESOURCE_TIMEOUT)
        
        if result and "contents" in result and len(result["contents"]) > 0:
            content = result["contents"][0].get("text", "")
            mime_type = result["contents"][0].get("mimeType", "text/plain")
            
            # Cache the result
            self._resource_cache[uri] = {
                "content": content,
                "mimeType": mime_type,
                "cached_at": time.time(),
                "ttl": 300  # 5 minute TTL
            }
            
            return content
        
        return None
    
    def invalidate_cache(self, uri: Optional[str] = None):
        """
        Invalidate resource cache.
        
        Args:
            uri: Specific resource URI to invalidate, or None to invalidate all
        """
        if uri:
            self._resource_cache.pop(uri, None)
        else:
            self._resource_cache.clear()
            self._resource_list_cache = None
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """
        List all available tools from MCP server.
        
        Returns:
            List of tool dictionaries with name, description, inputSchema
        """
        if not self.initialized:
            if not self.initialize():
                return []
        
        result = self._send_request("tools/list", timeout=TOOL_TIMEOUT)
        
        if result and "tools" in result:
            return result["tools"]
        
        return []
    
    def call_tool(self, tool_name: str, arguments: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Call a tool on the MCP server.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments dictionary
            
        Returns:
            Tool result dict with content, or None if error
        """
        if not self.initialized:
            if not self.initialize():
                return None
        
        params = {
            "name": tool_name
        }
        if arguments:
            params["arguments"] = arguments
        
        result = self._send_request("tools/call", params, timeout=TOOL_TIMEOUT)
        
        return result

