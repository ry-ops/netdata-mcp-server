"""Netdata MCP Server - Integrates Netdata API with Claude via MCP protocol."""

import asyncio
import json
from typing import Any, Optional
from urllib.parse import urljoin, urlencode

import httpx
from mcp.server import Server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)
from pydantic import BaseModel, Field


class NetdataClient:
    """Client for interacting with Netdata API."""

    def __init__(self, base_url: str = "http://localhost:19999", api_key: Optional[str] = None):
        """
        Initialize Netdata client.

        Args:
            base_url: Base URL of Netdata instance (default: http://localhost:19999)
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)

    async def _request(
        self, endpoint: str, params: Optional[dict] = None, api_version: str = "v1"
    ) -> dict[str, Any]:
        """Make a request to Netdata API."""
        url = urljoin(self.base_url, f"/api/{api_version}/{endpoint}")

        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            response = await self.client.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            return {"error": str(e), "status_code": getattr(e.response, "status_code", None)}

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    # Info & Nodes
    async def get_info(self) -> dict[str, Any]:
        """Get basic information about the Netdata agent."""
        return await self._request("info")

    async def get_nodes(self, api_version: str = "v2") -> dict[str, Any]:
        """Get list of all nodes hosted by this Netdata Agent."""
        return await self._request("nodes", api_version=api_version)

    # Contexts
    async def get_contexts(
        self, api_version: str = "v2", scope_nodes: str = "*", scope_contexts: str = "*"
    ) -> dict[str, Any]:
        """Get list of all contexts across all nodes."""
        params = {"scope_nodes": scope_nodes, "scope_contexts": scope_contexts}
        return await self._request("contexts", params=params, api_version=api_version)

    async def search_contexts(
        self, query: str, api_version: str = "v2", scope_nodes: str = "*"
    ) -> dict[str, Any]:
        """Search for contexts matching a query."""
        params = {"q": query, "scope_nodes": scope_nodes}
        return await self._request("q", params=params, api_version=api_version)

    # Data Queries
    async def get_data(
        self,
        chart: Optional[str] = None,
        context: Optional[str] = None,
        after: int = -600,
        before: int = 0,
        points: int = 0,
        format: str = "json",
        group: str = "average",
        options: Optional[list[str]] = None,
        api_version: str = "v1",
    ) -> dict[str, Any]:
        """
        Query metric data.

        Args:
            chart: Chart ID to query (v1 only)
            context: Context to query (v1 only, or use v2 with scope_contexts)
            after: Start time (negative for seconds ago, positive for unix timestamp)
            before: End time (negative for seconds ago, positive for unix timestamp, 0 for now)
            points: Number of points to return (0 for all available)
            format: Response format (json, jsonp, csv, etc.)
            group: Time aggregation function (average, min, max, sum, etc.)
            options: Additional options (jsonwrap, raw, minify, etc.)
            api_version: API version to use (v1, v2, or v3)
        """
        params = {
            "after": after,
            "before": before,
            "points": points,
            "format": format,
            "group": group,
        }

        if api_version == "v1":
            if chart:
                params["chart"] = chart
            elif context:
                params["context"] = context
        else:
            # v2/v3 use scope_contexts parameter
            if context:
                params["scope_contexts"] = context

        if options:
            params["options"] = ",".join(options)

        return await self._request("data", params=params, api_version=api_version)

    async def get_all_metrics(
        self,
        format: str = "json",
        filter: Optional[str] = None,
        names: str = "yes",
        timestamps: str = "yes",
    ) -> dict[str, Any]:
        """
        Get latest values for all metrics.

        Args:
            format: Response format (shell, prometheus, json)
            filter: Filter to apply to charts
            names: Include dimension names (yes/no)
            timestamps: Include timestamps in prometheus output (yes/no)
        """
        params = {"format": format, "names": names, "timestamps": timestamps}
        if filter:
            params["filter"] = filter

        return await self._request("allmetrics", params=params)

    # Alerts
    async def get_alerts(self, all: bool = False, active: bool = False) -> dict[str, Any]:
        """
        Get list of active or raised alarms.

        Args:
            all: Return all enabled alarms
            active: Return raised alarms in WARNING or CRITICAL state
        """
        params = {}
        if all:
            params["all"] = "true"
        if active:
            params["active"] = "true"

        return await self._request("alarms", params=params)

    async def get_alert_log(self, after: Optional[int] = None) -> dict[str, Any]:
        """
        Get alarm log entries.

        Args:
            after: Return events after this UNIQUEID
        """
        params = {}
        if after is not None:
            params["after"] = after

        return await self._request("alarm_log", params=params)

    async def get_alert_variables(self, chart: str) -> dict[str, Any]:
        """
        Get variables available for configuring alarms for a chart.

        Args:
            chart: Chart ID
        """
        return await self._request("alarm_variables", params={"chart": chart})

    # Functions
    async def get_functions(self) -> dict[str, Any]:
        """Get list of all registered collector functions."""
        return await self._request("functions")

    async def execute_function(self, function: str, timeout: int = 10) -> dict[str, Any]:
        """
        Execute a collector function.

        Args:
            function: Name of the function to execute
            timeout: Timeout in seconds
        """
        params = {"function": function, "timeout": timeout}
        return await self._request("function", params=params)

    # Badges
    async def get_badge(
        self,
        chart: str,
        dimension: Optional[str] = None,
        after: int = -600,
        before: int = 0,
        label: Optional[str] = None,
        units: Optional[str] = None,
        label_color: Optional[str] = None,
        value_color: Optional[str] = None,
    ) -> bytes:
        """
        Generate an SVG badge for a chart or dimension.

        Returns raw SVG bytes.
        """
        params = {
            "chart": chart,
            "after": after,
            "before": before,
        }
        if dimension:
            params["dimension"] = dimension
        if label:
            params["label"] = label
        if units:
            params["units"] = units
        if label_color:
            params["label_color"] = label_color
        if value_color:
            params["value_color"] = value_color

        url = urljoin(self.base_url, "/api/v1/badge.svg")
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            response = await self.client.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.content
        except httpx.HTTPError as e:
            return str(e).encode()

    # Management
    async def manage_health(
        self,
        cmd: Optional[str] = None,
        alarm: Optional[str] = None,
        chart: Optional[str] = None,
        context: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Manage health checks and notifications.

        Args:
            cmd: Command (DISABLE ALL, SILENCE ALL, DISABLE, SILENCE, RESET, LIST)
            alarm: Alarm name pattern
            chart: Chart ID pattern
            context: Context pattern
        """
        params = {}
        if cmd:
            params["cmd"] = cmd
        if alarm:
            params["alarm"] = alarm
        if chart:
            params["chart"] = chart
        if context:
            params["context"] = context

        return await self._request("manage/health", params=params)

    # Charts (v1 - legacy)
    async def get_charts(self) -> dict[str, Any]:
        """Get summary of all charts (v1 API - legacy)."""
        return await self._request("charts")

    async def get_chart(self, chart: str) -> dict[str, Any]:
        """
        Get detailed information about a chart (v1 API - legacy).

        Args:
            chart: Chart ID
        """
        return await self._request("chart", params={"chart": chart})


# Initialize MCP server
app = Server("netdata-mcp-server")
netdata_client: Optional[NetdataClient] = None


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available Netdata tools."""
    return [
        Tool(
            name="netdata_get_info",
            description="Get basic information about the Netdata agent including version, OS, collectors, and alarm counts",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="netdata_get_nodes",
            description="Get list of all nodes hosted by this Netdata Agent with their status and information",
            inputSchema={
                "type": "object",
                "properties": {
                    "api_version": {
                        "type": "string",
                        "description": "API version to use (v2 or v3)",
                        "enum": ["v2", "v3"],
                        "default": "v2",
                    }
                },
            },
        ),
        Tool(
            name="netdata_get_contexts",
            description="Get list of all metric contexts across all nodes with their metadata",
            inputSchema={
                "type": "object",
                "properties": {
                    "api_version": {
                        "type": "string",
                        "description": "API version to use (v2 or v3)",
                        "enum": ["v2", "v3"],
                        "default": "v2",
                    },
                    "scope_nodes": {
                        "type": "string",
                        "description": "Simple pattern to filter nodes",
                        "default": "*",
                    },
                    "scope_contexts": {
                        "type": "string",
                        "description": "Simple pattern to filter contexts",
                        "default": "*",
                    },
                },
            },
        ),
        Tool(
            name="netdata_search_contexts",
            description="Search for contexts matching a query string across all nodes",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query string",
                    },
                    "api_version": {
                        "type": "string",
                        "description": "API version to use (v2 or v3)",
                        "enum": ["v2", "v3"],
                        "default": "v2",
                    },
                    "scope_nodes": {
                        "type": "string",
                        "description": "Simple pattern to filter nodes",
                        "default": "*",
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="netdata_get_data",
            description="Query metric data for a chart or context with time-series data for all dimensions",
            inputSchema={
                "type": "object",
                "properties": {
                    "chart": {
                        "type": "string",
                        "description": "Chart ID to query (v1 API only)",
                    },
                    "context": {
                        "type": "string",
                        "description": "Context to query (e.g., 'system.cpu', 'disk.io')",
                    },
                    "after": {
                        "type": "integer",
                        "description": "Start time in seconds (negative for relative to now, positive for unix timestamp)",
                        "default": -600,
                    },
                    "before": {
                        "type": "integer",
                        "description": "End time in seconds (0 for now, negative for relative, positive for unix timestamp)",
                        "default": 0,
                    },
                    "points": {
                        "type": "integer",
                        "description": "Number of points to return (0 for all available)",
                        "default": 0,
                    },
                    "format": {
                        "type": "string",
                        "description": "Response format",
                        "enum": ["json", "json2", "csv", "datatable", "jsonp"],
                        "default": "json",
                    },
                    "group": {
                        "type": "string",
                        "description": "Time aggregation function",
                        "enum": [
                            "min",
                            "max",
                            "avg",
                            "average",
                            "median",
                            "sum",
                            "stddev",
                        ],
                        "default": "average",
                    },
                    "options": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Additional options (jsonwrap, raw, minify, etc.)",
                    },
                    "api_version": {
                        "type": "string",
                        "description": "API version to use (v1, v2, or v3)",
                        "enum": ["v1", "v2", "v3"],
                        "default": "v1",
                    },
                },
            },
        ),
        Tool(
            name="netdata_get_all_metrics",
            description="Get latest values for all metrics across all charts",
            inputSchema={
                "type": "object",
                "properties": {
                    "format": {
                        "type": "string",
                        "description": "Response format",
                        "enum": ["shell", "prometheus", "json"],
                        "default": "json",
                    },
                    "filter": {
                        "type": "string",
                        "description": "Filter pattern to apply to charts",
                    },
                },
            },
        ),
        Tool(
            name="netdata_get_alerts",
            description="Get list of active or raised alarms with their current state",
            inputSchema={
                "type": "object",
                "properties": {
                    "all": {
                        "type": "boolean",
                        "description": "Return all enabled alarms",
                        "default": False,
                    },
                    "active": {
                        "type": "boolean",
                        "description": "Return raised alarms in WARNING or CRITICAL state",
                        "default": False,
                    },
                },
            },
        ),
        Tool(
            name="netdata_get_alert_log",
            description="Get alarm log entries with historical information on raised and cleared alarms",
            inputSchema={
                "type": "object",
                "properties": {
                    "after": {
                        "type": "integer",
                        "description": "Return events after this UNIQUEID",
                    }
                },
            },
        ),
        Tool(
            name="netdata_get_alert_variables",
            description="Get variables available for configuring alarms for a specific chart",
            inputSchema={
                "type": "object",
                "properties": {
                    "chart": {
                        "type": "string",
                        "description": "Chart ID",
                    }
                },
                "required": ["chart"],
            },
        ),
        Tool(
            name="netdata_get_functions",
            description="Get list of all registered collector functions that can be executed on demand",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="netdata_execute_function",
            description="Execute a collector function on demand",
            inputSchema={
                "type": "object",
                "properties": {
                    "function": {
                        "type": "string",
                        "description": "Name of the function to execute",
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds",
                        "default": 10,
                    },
                },
                "required": ["function"],
            },
        ),
        Tool(
            name="netdata_manage_health",
            description="Manage health checks and notifications at runtime (disable, silence, reset)",
            inputSchema={
                "type": "object",
                "properties": {
                    "cmd": {
                        "type": "string",
                        "description": "Command to execute",
                        "enum": [
                            "DISABLE ALL",
                            "SILENCE ALL",
                            "DISABLE",
                            "SILENCE",
                            "RESET",
                            "LIST",
                        ],
                    },
                    "alarm": {
                        "type": "string",
                        "description": "Alarm name pattern",
                    },
                    "chart": {
                        "type": "string",
                        "description": "Chart ID pattern",
                    },
                    "context": {
                        "type": "string",
                        "description": "Context pattern",
                    },
                },
            },
        ),
        Tool(
            name="netdata_get_charts",
            description="Get summary of all charts (legacy v1 API)",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="netdata_get_chart",
            description="Get detailed information about a specific chart (legacy v1 API)",
            inputSchema={
                "type": "object",
                "properties": {
                    "chart": {
                        "type": "string",
                        "description": "Chart ID",
                    }
                },
                "required": ["chart"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls for Netdata operations."""
    global netdata_client

    if netdata_client is None:
        # Initialize with default localhost URL
        # Users can set NETDATA_URL and NETDATA_API_KEY environment variables
        import os

        base_url = os.getenv("NETDATA_URL", "http://localhost:19999")
        api_key = os.getenv("NETDATA_API_KEY")
        netdata_client = NetdataClient(base_url=base_url, api_key=api_key)

    try:
        result = None

        if name == "netdata_get_info":
            result = await netdata_client.get_info()

        elif name == "netdata_get_nodes":
            api_version = arguments.get("api_version", "v2")
            result = await netdata_client.get_nodes(api_version=api_version)

        elif name == "netdata_get_contexts":
            api_version = arguments.get("api_version", "v2")
            scope_nodes = arguments.get("scope_nodes", "*")
            scope_contexts = arguments.get("scope_contexts", "*")
            result = await netdata_client.get_contexts(
                api_version=api_version,
                scope_nodes=scope_nodes,
                scope_contexts=scope_contexts,
            )

        elif name == "netdata_search_contexts":
            query = arguments["query"]
            api_version = arguments.get("api_version", "v2")
            scope_nodes = arguments.get("scope_nodes", "*")
            result = await netdata_client.search_contexts(
                query=query, api_version=api_version, scope_nodes=scope_nodes
            )

        elif name == "netdata_get_data":
            result = await netdata_client.get_data(
                chart=arguments.get("chart"),
                context=arguments.get("context"),
                after=arguments.get("after", -600),
                before=arguments.get("before", 0),
                points=arguments.get("points", 0),
                format=arguments.get("format", "json"),
                group=arguments.get("group", "average"),
                options=arguments.get("options"),
                api_version=arguments.get("api_version", "v1"),
            )

        elif name == "netdata_get_all_metrics":
            result = await netdata_client.get_all_metrics(
                format=arguments.get("format", "json"),
                filter=arguments.get("filter"),
            )

        elif name == "netdata_get_alerts":
            result = await netdata_client.get_alerts(
                all=arguments.get("all", False),
                active=arguments.get("active", False),
            )

        elif name == "netdata_get_alert_log":
            result = await netdata_client.get_alert_log(after=arguments.get("after"))

        elif name == "netdata_get_alert_variables":
            result = await netdata_client.get_alert_variables(chart=arguments["chart"])

        elif name == "netdata_get_functions":
            result = await netdata_client.get_functions()

        elif name == "netdata_execute_function":
            result = await netdata_client.execute_function(
                function=arguments["function"],
                timeout=arguments.get("timeout", 10),
            )

        elif name == "netdata_manage_health":
            result = await netdata_client.manage_health(
                cmd=arguments.get("cmd"),
                alarm=arguments.get("alarm"),
                chart=arguments.get("chart"),
                context=arguments.get("context"),
            )

        elif name == "netdata_get_charts":
            result = await netdata_client.get_charts()

        elif name == "netdata_get_chart":
            result = await netdata_client.get_chart(chart=arguments["chart"])

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

        # Format the result as JSON
        result_text = json.dumps(result, indent=2)
        return [TextContent(type="text", text=result_text)]

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Run the MCP server."""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
