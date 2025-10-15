<img src="https://github.com/ry-ops/netdata-mcp-server/blob/main/netdata_mcp_server.png" width="100%">

# Netdata MCP Server

A Model Context Protocol (MCP) server that integrates [Netdata](https://www.netdata.cloud/) monitoring capabilities with Claude. This allows Claude to query metrics, monitor system health, analyze alerts, and interact with Netdata's real-time monitoring data.

## Features

- **Real-time Metrics**: Query time-series data for CPU, memory, disk, network, and custom metrics
- **Node Management**: List and monitor multiple Netdata nodes
- **Context Discovery**: Search and explore available metric contexts
- **Alert Monitoring**: Check active alarms, view alarm history, and manage health checks
- **Collector Functions**: Execute on-demand collector functions
- **Multi-version API Support**: Compatible with Netdata API v1, v2, and v3
- **Badge Generation**: Create SVG badges for metrics

## Installation

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- A running Netdata instance (default: `http://localhost:19999`)

### Install uv

```bash
# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Install the MCP Server

```bash
# Clone or download this repository
cd netdata-mcp-server

# Install dependencies with uv
uv pip install -e .
```

## Configuration

### Environment Variables

Set these environment variables to configure the Netdata connection:

```bash
# Netdata instance URL (default: http://localhost:19999)
export NETDATA_URL="http://your-netdata-host:19999"

# Optional: API key for authentication
export NETDATA_API_KEY="your-api-key-here"
```

### Claude Desktop Configuration

Add the server to your Claude Desktop configuration file:

**On macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**On Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "netdata": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/netdata-mcp-server",
        "run",
        "python",
        "-m",
        "netdata_mcp.server"
      ],
      "env": {
        "NETDATA_URL": "http://localhost:19999",
        "NETDATA_API_KEY": "optional-api-key"
      }
    }
  }
}
```

## Available Tools

The MCP server provides the following tools for Claude to interact with Netdata:

### Information & Discovery

- **netdata_get_info**: Get basic information about the Netdata agent
- **netdata_get_nodes**: List all nodes hosted by this Netdata Agent
- **netdata_get_contexts**: Get all metric contexts across nodes
- **netdata_search_contexts**: Search for specific contexts
- **netdata_get_charts**: Get summary of all charts (legacy v1)
- **netdata_get_chart**: Get detailed chart information (legacy v1)

### Data Queries

- **netdata_get_data**: Query time-series metric data
- **netdata_get_all_metrics**: Get latest values for all metrics

### Alert Management

- **netdata_get_alerts**: List active or raised alarms
- **netdata_get_alert_log**: View alarm history
- **netdata_get_alert_variables**: Get variables for alarm configuration
- **netdata_manage_health**: Disable, silence, or reset health checks

### Functions

- **netdata_get_functions**: List available collector functions
- **netdata_execute_function**: Execute a collector function on demand

## Usage Examples

Here are some example queries you can ask Claude:

### Basic Monitoring

```
What's the current CPU usage?
Show me memory utilization over the last hour
What alerts are currently active?
```

### Detailed Analysis

```
Compare disk I/O across all nodes
What were the top 5 metrics by anomaly rate in the last 24 hours?
Show me the alert history for the last week
```

### System Investigation

```
Which processes are consuming the most CPU?
Is there any unusual network activity?
What collector functions are available?
```

### Configuration

```
List all available metric contexts
What variables can I use for the system.cpu alarm?
Show me all nodes and their status
```

## API Reference

### NetdataClient Class

The `NetdataClient` class provides direct access to the Netdata API:

```python
from netdata_mcp import NetdataClient

# Initialize client
client = NetdataClient(
    base_url="http://localhost:19999",
    api_key="optional-key"
)

# Get system info
info = await client.get_info()

# Query CPU data
cpu_data = await client.get_data(
    context="system.cpu",
    after=-600,  # Last 10 minutes
    format="json"
)

# Get active alerts
alerts = await client.get_alerts(active=True)

# Close the client
await client.close()
```

### Common Parameters

- **after/before**: Time range for queries (negative for relative, positive for unix timestamp)
- **points**: Number of data points to return (0 for all available)
- **format**: Response format (json, json2, csv, prometheus, etc.)
- **group**: Aggregation function (average, min, max, sum, median, etc.)
- **api_version**: API version to use (v1, v2, or v3)

## Development

### Running Tests

```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest
```

### Code Formatting

```bash
# Format code with black
black src/

# Lint with ruff
ruff check src/
```

## Netdata API Documentation

For complete API documentation, see:
- [Netdata API Documentation](https://learn.netdata.cloud/api)
- [OpenAPI Specification](https://raw.githubusercontent.com/netdata/netdata/master/src/web/api/netdata-swagger.yaml)

## Troubleshooting

### Connection Issues

If Claude can't connect to Netdata:

1. Verify Netdata is running: `curl http://localhost:19999/api/v1/info`
2. Check the `NETDATA_URL` environment variable
3. Ensure no firewall is blocking the connection
4. For remote Netdata instances, verify the URL and port

### Authentication Errors

If you get authentication errors:

1. Check if your Netdata instance requires authentication
2. Verify the `NETDATA_API_KEY` is correctly set
3. Ensure the API key has the necessary permissions

### No Data Returned

If queries return no data:

1. Verify the chart/context exists: use `netdata_get_contexts`
2. Check the time range (after/before parameters)
3. Ensure the metric is being collected (check with `netdata_get_all_metrics`)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues related to:
- **This MCP server**: Open an issue on this repository
- **Netdata itself**: Visit [Netdata GitHub](https://github.com/netdata/netdata)
- **MCP protocol**: See [MCP Documentation](https://modelcontextprotocol.io/)

## Acknowledgments

- [Netdata](https://www.netdata.cloud/) for the excellent monitoring platform
- [Anthropic](https://www.anthropic.com/) for Claude and the MCP protocol
- [Astral](https://astral.sh/) for the uv package manager
