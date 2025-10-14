#!/usr/bin/env python3
"""Helper script to generate Claude Desktop configuration."""

import json
import os
import platform
from pathlib import Path


def get_config_path():
    """Get the Claude Desktop config path for the current OS."""
    system = platform.system()

    if system == "Darwin":  # macOS
        return Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
    elif system == "Windows":
        appdata = os.getenv("APPDATA")
        if appdata:
            return Path(appdata) / "Claude/claude_desktop_config.json"
    elif system == "Linux":
        # Linux doesn't have official Claude Desktop, but just in case
        return Path.home() / ".config/Claude/claude_desktop_config.json"

    return None


def main():
    """Generate configuration for Claude Desktop."""
    print("🔧 Netdata MCP Server - Configuration Helper\n")

    # Get current directory
    current_dir = Path(__file__).parent.absolute()
    print(f"📁 Server directory: {current_dir}\n")

    # Get Netdata URL
    netdata_url = input("Enter Netdata URL [http://localhost:19999]: ").strip()
    if not netdata_url:
        netdata_url = "http://localhost:19999"

    # Get API key (optional)
    api_key = input("Enter Netdata API key (optional, press Enter to skip): ").strip()

    # Generate configuration
    config = {
        "mcpServers": {
            "netdata": {
                "command": "uv",
                "args": [
                    "--directory",
                    str(current_dir),
                    "run",
                    "python",
                    "-m",
                    "netdata_mcp.server",
                ],
                "env": {"NETDATA_URL": netdata_url},
            }
        }
    }

    if api_key:
        config["mcpServers"]["netdata"]["env"]["NETDATA_API_KEY"] = api_key

    # Display configuration
    print("\n" + "=" * 70)
    print("Generated Configuration:")
    print("=" * 70)
    print(json.dumps(config, indent=2))
    print("=" * 70)

    # Get Claude Desktop config path
    config_path = get_config_path()

    if config_path:
        print(f"\n📍 Claude Desktop config location:")
        print(f"   {config_path}")

        if config_path.exists():
            print("\n⚠️  Config file already exists!")
            merge = input("Do you want to see merge instructions? (y/n): ").strip().lower()

            if merge == "y":
                print("\n📝 To merge this configuration:")
                print("1. Open your existing config file")
                print("2. Add the 'netdata' entry to the 'mcpServers' object")
                print("3. Save the file and restart Claude Desktop")
        else:
            print("\n💡 Config file doesn't exist yet.")
            create = input("Create the config file with this configuration? (y/n): ").strip().lower()

            if create == "y":
                config_path.parent.mkdir(parents=True, exist_ok=True)
                with open(config_path, "w") as f:
                    json.dump(config, f, indent=2)
                print(f"\n✅ Configuration saved to: {config_path}")
    else:
        print("\n⚠️  Could not determine Claude Desktop config path for your OS")
        print("Please manually add the configuration to your Claude Desktop config file")

    # Save to local file
    local_config = current_dir / "my_claude_config.json"
    with open(local_config, "w") as f:
        json.dump(config, f, indent=2)

    print(f"\n💾 Configuration also saved to: {local_config}")

    print("\n" + "=" * 70)
    print("Next Steps:")
    print("=" * 70)
    print("1. Verify the configuration above is correct")
    print("2. Restart Claude Desktop completely (quit, don't just close)")
    print("3. Test by asking Claude: 'What's my current CPU usage?'")
    print("\n✨ Setup complete!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Configuration cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
