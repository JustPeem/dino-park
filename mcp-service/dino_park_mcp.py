"""Compatibility runner for MCP service with robust path resolution."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is importable when running this file directly,
# e.g. `python mcp-service/dino_park_mcp.py` inside Docker.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mcp_service.dino_park_mcp import mcp

if __name__ == "__main__":
    mcp.run(transport="stdio")