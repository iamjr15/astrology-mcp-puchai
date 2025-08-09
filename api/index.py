"""Vercel serverless function entry point for Astrologer MCP Server."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import importlib.util
module_path = os.path.join(os.path.dirname(__file__), '..', 'mcp-bearer-token', 'puch_astro_mcp.py')
spec = importlib.util.spec_from_file_location("puch_astro_mcp", module_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

app = module.app
