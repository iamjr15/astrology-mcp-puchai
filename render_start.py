#!/usr/bin/env python3
"""Render.com startup script for Astrologer MCP Server.

This script starts the FastAPI application for deployment on Render.com
as a persistent web service rather than a serverless function.
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the FastAPI app from the main MCP server
# Handle the hyphenated directory name
import importlib.util
mcp_module_path = project_root / "mcp-bearer-token" / "puch_astro_mcp.py"
spec = importlib.util.spec_from_file_location("puch_astro_mcp", mcp_module_path)
mcp_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mcp_module)
app = mcp_module.app

if __name__ == "__main__":
    # Get port from environment variable (Render sets this automatically)
    port = int(os.environ.get("PORT", 8086))
    
    # Run the FastAPI app with uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    )
