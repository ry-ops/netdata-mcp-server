# Netdata MCP Server - Project Structure

## Overview

This is a complete MCP (Model Context Protocol) server that enables Claude to interact with the Netdata monitoring API. Built with Python and managed with `uv` for fast, reliable dependency management.

## Project Structure

```
netdata-mcp-server/
├── src/
│   └── netdata_mcp/
│       ├── __init__.py          # Package initialization
│       └── server.py            # Main MCP server implementation
├── tests/
│   ├── __init__.py              # Test package initialization
│   └── test_server.py           # Test suite
├── examples/
│   └── usage.py                 # Example usage script
├── pyproject.toml               # Project metadata and dependencies
├── README.md                    # Comprehensive documentation
├── QUICKSTART.md                # Quick start guide
├── LICENSE                      # MIT License
├── .gitignore                   # Git ignore rules
├── configure.py                 # Configuration helper script
└── claude_desktop_config.example.json  # Example Claude config
```

## Key Files

### `src/netdata_mcp/server.py`

The main implementation with:
- **NetdataClient**: Async HTTP client for Netdata API
- **MCP Server**: Tool definitions and handlers
- **15+ Tools**: For querying metrics, alerts, nodes, etc.

Key features:
- Support for Netdata API v1, v2, and v3
- Comprehensive error handling
- Full OpenAPI spec coverage
- Async/await throughout

### `pyproject.toml`

Modern Python project configuration:
- Python 3.10+ requirement
- Dependencies: mcp, httpx, pydantic
- Dev dependencies: pytest, black, ruff
- uv-specific configuration

### `README.md`

Complete documentation including:
- Feature overview
- Installation instructions
- Configuration guide
- Tool reference
- Usage examples
- Troubleshooting

### `QUICKSTART.md`

Step-by-step guide to get running in 5 minutes:
- Prerequisites
- Installation
- Configuration
- Verification
- Common issues

### `configure.py`

Interactive configuration helper:
- Detects OS and config location
- Generates Claude Desktop config
- Handles existing configs
- Saves local backup

### `examples/usage.py`

Demonstrates all major features:
- Getting system info
- Querying metrics
- Checking alerts
- Searching contexts
- Listing functions

### `tests/test_server.py`

Pytest test suite covering:
- Client initialization
- API methods
- Error handling
- Tool listing
- Mock responses

## Available Tools

The MCP server exposes 15 tools to Claude:

### Information & Discovery
1. `netdata_get_info` - Agent information
2. `netdata_get_nodes` - List nodes
3. `netdata_get_contexts` - List contexts
4. `netdata_search_contexts` - Search contexts
5. `netdata_get_charts` - List charts (v1)
6. `netdata_get_chart` - Chart details (v1)

### Data Queries
7. `netdata_get_data` - Query time-series data
8. `netdata_get_all_metrics` - Latest metric values

### Alert Management
9. `netdata_get_alerts` - Active alarms
10. `netdata_get_alert_log` - Alarm history
11. `netdata_get_alert_variables` - Alarm variables
12. `netdata_manage_health` - Manage health checks

### Functions
13. `netdata_get_functions` - List functions
14. `netdata_execute_function` - Execute function

### Legacy
15. Additional v1 API endpoints

## API Coverage

The server implements endpoints from the Netdata OpenAPI specification:

- ✅ /api/v1/info
- ✅ /api/v1/data
- ✅ /api/v1/allmetrics
- ✅ /api/v1/alarms
- ✅ /api/v1/alarm_log
- ✅ /api/v1/alarm_variables
- ✅ /api/v1/functions
- ✅ /api/v1/function
- ✅ /api/v1/manage/health
- ✅ /api/v1/charts
- ✅ /api/v1/chart
- ✅ /api/v1/contexts
- ✅ /api/v1/context
- ✅ /api/v1/badge.svg
- ✅ /api/v2/nodes
- ✅ /api/v2/contexts
- ✅ /api/v2/q (search)
- ✅ /api/v2/data
- ✅ /api/v2/weights
- ✅ /api/v3/nodes
- ✅ /api/v3/contexts
- ✅ /api/v3/q
- ✅ /api/v3/data
- ✅ /api/v3/weights

## Technology Stack

- **Python 3.10+**: Modern Python with type hints
- **uv**: Fast Python package manager
- **MCP**: Model Context Protocol for Claude integration
- **httpx**: Async HTTP client
- **pydantic**: Data validation
- **pytest**: Testing framework

## Development

### Setup Development Environment

```bash
# Install with dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/

# Lint code
ruff check src/
```

### Running Locally

```bash
# Test the client directly
uv run python examples/usage.py

# Run the MCP server
uv run python -m netdata_mcp.server
```

### Adding New Tools

1. Add method to `NetdataClient` class
2. Add tool definition in `list_tools()`
3. Add handler in `call_tool()`
4. Add tests in `test_server.py`
5. Update documentation

## Configuration

### Environment Variables

- `NETDATA_URL`: Netdata instance URL (default: http://localhost:19999)
- `NETDATA_API_KEY`: Optional API key for authentication

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "netdata": {
      "command": "uv",
      "args": ["--directory", "/path/to/netdata-mcp-server", "run", "python", "-m", "netdata_mcp.server"],
      "env": {
        "NETDATA_URL": "http://localhost:19999"
      }
    }
  }
}
```

## Use Cases

### System Monitoring
- Real-time CPU, memory, disk metrics
- Network traffic analysis
- Process monitoring

### Alert Management
- Check active alerts
- Review alert history
- Configure alarm thresholds

### Performance Analysis
- Time-series data queries
- Metric correlation
- Anomaly detection

### Infrastructure Management
- Multi-node monitoring
- Context discovery
- Collector functions

## Future Enhancements

Potential improvements:
- [ ] Badge generation support
- [ ] Streaming API support
- [ ] Cloud API integration
- [ ] Custom metric creation
- [ ] Alert rule management
- [ ] Dashboard generation
- [ ] Report generation
- [ ] Metric export

## Contributing

Contributions welcome! Areas for improvement:
- Additional API endpoints
- Better error messages
- Performance optimizations
- More examples
- Better documentation
- Integration tests

## License

MIT License - see LICENSE file for details.

## Support & Resources

- [Netdata Documentation](https://learn.netdata.cloud/)
- [Netdata API Docs](https://learn.netdata.cloud/api)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [uv Documentation](https://github.com/astral-sh/uv)

## Version History

- **0.1.0** (2025-01-14): Initial release
  - Full Netdata API v1/v2/v3 support
  - 15 MCP tools
  - Comprehensive documentation
  - Test suite
  - Configuration helper

---

Built with ❤️ for the Netdata and Claude communities.
