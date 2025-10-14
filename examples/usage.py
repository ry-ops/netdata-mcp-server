"""Example usage of the Netdata MCP client."""

import asyncio
from netdata_mcp import NetdataClient


async def main():
    """Demonstrate Netdata client usage."""
    # Initialize client (uses environment variables or defaults to localhost)
    client = NetdataClient()

    try:
        # Get basic info
        print("=== Netdata Agent Info ===")
        info = await client.get_info()
        print(f"Version: {info.get('version')}")
        print(f"Hostname: {info.get('hostname')}")
        print(f"OS: {info.get('os_name')}")
        print()

        # List available contexts
        print("=== Available Contexts (first 5) ===")
        contexts = await client.get_contexts(api_version="v2")
        context_list = list(contexts.get("contexts", {}).keys())[:5]
        for ctx in context_list:
            print(f"  - {ctx}")
        print()

        # Get CPU data
        print("=== CPU Data (last 10 minutes) ===")
        cpu_data = await client.get_data(
            context="system.cpu",
            after=-600,
            format="json",
            options=["jsonwrap"],
        )
        if "result" in cpu_data:
            print(f"Points returned: {cpu_data.get('points')}")
            print(f"Time range: {cpu_data.get('after')} to {cpu_data.get('before')}")
            print(f"Dimensions: {', '.join(cpu_data.get('dimension_names', []))}")
        print()

        # Check active alerts
        print("=== Active Alerts ===")
        alerts = await client.get_alerts(active=True)
        if "alarms" in alerts:
            alarm_count = len(alerts["alarms"])
            print(f"Total active alarms: {alarm_count}")
            if alarm_count > 0:
                for alarm_name, alarm_data in list(alerts["alarms"].items())[:3]:
                    print(f"  - {alarm_name}: {alarm_data.get('status')}")
        else:
            print("No active alerts")
        print()

        # Search for disk-related contexts
        print("=== Searching for 'disk' contexts ===")
        search_results = await client.search_contexts(query="disk", api_version="v2")
        if "contexts" in search_results:
            for ctx in list(search_results["contexts"].keys())[:5]:
                print(f"  - {ctx}")
        print()

        # List available functions
        print("=== Available Functions ===")
        functions = await client.get_functions()
        if isinstance(functions, dict):
            for func_name in list(functions.keys())[:5]:
                print(f"  - {func_name}")
        print()

    except Exception as e:
        print(f"Error: {e}")

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
