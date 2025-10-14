"""Tests for Netdata MCP Server."""

import pytest
from unittest.mock import AsyncMock, patch
from netdata_mcp import NetdataClient


@pytest.fixture
def mock_httpx_client():
    """Mock httpx AsyncClient."""
    with patch("netdata_mcp.server.httpx.AsyncClient") as mock:
        client_instance = AsyncMock()
        mock.return_value = client_instance
        yield client_instance


@pytest.mark.asyncio
async def test_netdata_client_init():
    """Test NetdataClient initialization."""
    client = NetdataClient(base_url="http://test:19999", api_key="test-key")
    assert client.base_url == "http://test:19999"
    assert client.api_key == "test-key"
    await client.close()


@pytest.mark.asyncio
async def test_get_info(mock_httpx_client):
    """Test get_info method."""
    mock_response = AsyncMock()
    mock_response.json.return_value = {
        "version": "1.0.0",
        "hostname": "test-host",
    }
    mock_httpx_client.get.return_value = mock_response

    client = NetdataClient()
    result = await client.get_info()

    assert result["version"] == "1.0.0"
    assert result["hostname"] == "test-host"
    await client.close()


@pytest.mark.asyncio
async def test_get_data_with_context(mock_httpx_client):
    """Test get_data with context parameter."""
    mock_response = AsyncMock()
    mock_response.json.return_value = {
        "labels": ["time", "cpu"],
        "data": [[1234567890, 50.5]],
    }
    mock_httpx_client.get.return_value = mock_response

    client = NetdataClient()
    result = await client.get_data(
        context="system.cpu", after=-600, before=0, format="json"
    )

    assert "data" in result
    await client.close()


@pytest.mark.asyncio
async def test_get_alerts(mock_httpx_client):
    """Test get_alerts method."""
    mock_response = AsyncMock()
    mock_response.json.return_value = {
        "hostname": "test-host",
        "alarms": {
            "test_alarm": {"status": "WARNING", "value": 75.0}
        },
    }
    mock_httpx_client.get.return_value = mock_response

    client = NetdataClient()
    result = await client.get_alerts(active=True)

    assert "alarms" in result
    assert "test_alarm" in result["alarms"]
    await client.close()


@pytest.mark.asyncio
async def test_search_contexts(mock_httpx_client):
    """Test search_contexts method."""
    mock_response = AsyncMock()
    mock_response.json.return_value = {
        "contexts": {
            "disk.io": {"family": "disk", "priority": 1000},
            "disk.ops": {"family": "disk", "priority": 1010},
        }
    }
    mock_httpx_client.get.return_value = mock_response

    client = NetdataClient()
    result = await client.search_contexts(query="disk", api_version="v2")

    assert "contexts" in result
    assert "disk.io" in result["contexts"]
    await client.close()


@pytest.mark.asyncio
async def test_error_handling(mock_httpx_client):
    """Test error handling in client."""
    import httpx

    mock_httpx_client.get.side_effect = httpx.HTTPError("Connection failed")

    client = NetdataClient()
    result = await client.get_info()

    assert "error" in result
    await client.close()


def test_tool_listing():
    """Test that all expected tools are listed."""
    from netdata_mcp.server import list_tools
    import asyncio

    tools = asyncio.run(list_tools())
    tool_names = [tool.name for tool in tools]

    expected_tools = [
        "netdata_get_info",
        "netdata_get_nodes",
        "netdata_get_contexts",
        "netdata_search_contexts",
        "netdata_get_data",
        "netdata_get_all_metrics",
        "netdata_get_alerts",
        "netdata_get_alert_log",
        "netdata_manage_health",
    ]

    for expected in expected_tools:
        assert expected in tool_names
