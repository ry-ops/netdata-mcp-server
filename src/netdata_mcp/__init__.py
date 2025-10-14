"""Netdata MCP Server - Integration between Netdata API and Claude via MCP."""

__version__ = "0.1.0"

from .server import NetdataClient, app

__all__ = ["NetdataClient", "app"]
