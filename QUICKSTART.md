# Quick Start Guide

Get up and running with Netdata MCP Server in 5 minutes!

## Prerequisites

1. **Install uv** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Install Netdata** (if not already running):
   ```bash
   # On Linux/macOS
   bash <(curl -Ss https://get.netdata.cloud/kickstart.sh)
   
   # Or use Docker
   docker run -d --name=netdata \
     -p 19999:19999 \
     -v netdataconfig:/etc/netdata \
     -v netdatalib:/var/lib/netdata \
     -v netdatacache:/var/cache/netdata \
     -v /etc/passwd:/host/etc/passwd:ro \
     -v /etc/group:/host/etc/group:ro \
     -v /proc:/host/proc:ro \
     -v /sys:/host/sys:ro \
     --cap-add SYS_PTRACE \
     --security-opt apparmor=unconfined \
     netdata/netdata
   ```

3. Verify Netdata is running:
   ```bash
   curl http://localhost:19999/api/v1/info
   ```

## Installation Steps

### 1. Clone or Download This Repository

```bash
git clone <repository-url>
cd netdata-mcp-server
```

### 2. Install Dependencies

```bash
uv pip install -e .
```

### 3. Test the Connection

Run the example script to verify everything works:

```bash
uv run python examples/usage.py
```

You should see output showing your Netdata agent info, available contexts, CPU data, and more.

### 4. Configure Claude Desktop

Edit your Claude Desktop configuration:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

Add this configuration:

```json
{
  "mcpServers": {
    "netdata": {
      "command": "uv",
      "args": [
        "--directory",
        "/FULL/PATH/TO/netdata-mcp-server",
        "run",
        "python",
        "-m",
        "netdata_mcp.server"
      ],
      "env": {
        "NETDATA_URL": "http://localhost:19999"
      }
    }
  }
}
```

**Important**: Replace `/FULL/PATH/TO/netdata-mcp-server` with the actual full path to this directory.

### 5. Restart Claude Desktop

Completely quit and restart Claude Desktop for the changes to take effect.

### 6. Verify Integration

In Claude, you should now be able to ask questions like:

- "What's my current CPU usage?"
- "Show me all available Netdata contexts"
- "Are there any active alerts?"
- "What's the memory utilization for the last hour?"

## Common Issues

### Issue: Claude can't connect to Netdata

**Solution**: Verify the `NETDATA_URL` in your configuration:
```bash
curl http://localhost:19999/api/v1/info
```

If this fails, check that Netdata is running:
```bash
# Check if Netdata is running
ps aux | grep netdata

# Or check with systemctl (Linux)
systemctl status netdata
```

### Issue: MCP server won't start

**Solution**: Test the server directly:
```bash
cd /path/to/netdata-mcp-server
uv run python -m netdata_mcp.server
```

Check for any error messages. Common issues:
- Python version < 3.10
- Missing dependencies (run `uv pip install -e .` again)
- Invalid path in Claude configuration

### Issue: "No tools available" in Claude

**Solutions**:
1. Restart Claude Desktop completely (quit, don't just close the window)
2. Check the Claude Desktop logs for errors
3. Verify the `command` and `args` in your configuration are correct

### Issue: Remote Netdata instance

If your Netdata is on a different machine:

1. Update the configuration:
   ```json
   "env": {
     "NETDATA_URL": "http://your-server-ip:19999"
   }
   ```

2. If authentication is required:
   ```json
   "env": {
     "NETDATA_URL": "http://your-server-ip:19999",
     "NETDATA_API_KEY": "your-api-key"
   }
   ```

## Next Steps

Now that you're set up, try these example queries:

### System Monitoring
```
Show me CPU and memory usage over the last hour
Which processes are using the most resources?
What's the current network I/O?
```

### Alert Management
```
List all active alerts
Show me the alert history from yesterday
What alerts are configured for high CPU usage?
```

### Advanced Queries
```
Compare disk performance across all nodes
Search for all disk-related metrics
Execute the top-processes function
```

### Custom Dashboards
```
Create a summary of system health
Show me the most important metrics to watch
What's the anomaly rate for my services?
```

## Learn More

- [Full Documentation](README.md)
- [Netdata Documentation](https://learn.netdata.cloud/)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [Example Queries](examples/)

## Getting Help

If you run into issues:

1. Check the [Troubleshooting section](README.md#troubleshooting) in the main README
2. Verify Netdata is working: `curl http://localhost:19999/api/v1/info`
3. Test the MCP server directly: `uv run python examples/usage.py`
4. Check Claude Desktop logs for error messages

## Success!

Once everything is working, you'll be able to have natural conversations with Claude about your system metrics, alerts, and monitoring data. Claude can help you:

- Understand what's happening on your systems
- Diagnose performance issues
- Monitor trends over time
- Set up and manage alerts
- Explore your infrastructure

Happy monitoring! 🚀
