#!/usr/bin/env python3
"""MEOK AI Labs — sleep-tracker-ai-mcp MCP Server. Track sleep duration, quality, and patterns."""

import asyncio
import json
from datetime import datetime
from typing import Any

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent)
import mcp.types as types
import sys, os
sys.path.insert(0, os.path.expanduser("~/clawd/meok-labs-engine/shared"))
from auth_middleware import check_access
import json

# In-memory store (replace with DB in production)
_store = {}

server = Server("sleep-tracker-ai-mcp")

@server.list_resources()
async def handle_list_resources() -> list[Resource]:
    return []

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    return [
        Tool(name="log_sleep", description="Log sleep", inputSchema={"type":"object","properties":{"hours":{"type":"number"},"quality":{"type":"number"}},"required":["hours"]}),
        Tool(name="get_sleep_trend", description="Get sleep trend", inputSchema={"type":"object","properties":{}}),
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Any | None) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    args = arguments or {}
    if name == "log_sleep":
        _store.setdefault("logs", []).append({"hours": args["hours"], "quality": args.get("quality", 5)})
        return [TextContent(type="text", text=json.dumps({"status": "logged"}, indent=2))]
    if name == "get_sleep_trend":
        logs = _store.get("logs", [])
        avg = sum(l["hours"] for l in logs) / len(logs) if logs else 0
        return [TextContent(type="text", text=json.dumps({"average_hours": round(avg, 1), "entries": len(logs)}, indent=2))]
    return [TextContent(type="text", text=json.dumps({"error": "Unknown tool"}, indent=2))]

async def main():
    async with stdio_server(server._read_stream, server._write_stream) as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="sleep-tracker-ai-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={})))

if __name__ == "__main__":
    asyncio.run(main())