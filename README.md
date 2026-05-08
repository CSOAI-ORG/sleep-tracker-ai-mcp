<div align="center">

# Sleep Tracker Ai MCP

**MCP server for sleep tracker ai mcp operations**

[![PyPI](https://img.shields.io/pypi/v/meok-sleep-tracker-ai-mcp)](https://pypi.org/project/meok-sleep-tracker-ai-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-MCP_Server-purple)](https://meok.ai)

</div>

## Overview

Sleep Tracker Ai MCP provides AI-powered tools via the Model Context Protocol (MCP).

## Tools

| Tool | Description |
|------|-------------|
| `log_sleep` | Log a sleep entry. Hours slept, quality 1-10 (10=best), optional bedtime/wake_ti |
| `get_sleep_stats` | Get sleep statistics over the last N days. Includes averages, trends, and consis |
| `analyze_patterns` | Analyse sleep patterns to find correlations between bedtime, duration, quality,  |
| `get_recommendations` | Get personalised sleep improvement recommendations based on your logged data. |

## Installation

```bash
pip install meok-sleep-tracker-ai-mcp
```

## Usage with Claude Desktop

Add to your Claude Desktop MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "sleep-tracker-ai": {
      "command": "python",
      "args": ["-m", "meok_sleep_tracker_ai_mcp.server"]
    }
  }
}
```

## Usage with FastMCP

```python
from mcp.server.fastmcp import FastMCP

# This server exposes 4 tool(s) via MCP
# See server.py for full implementation
```

## License

MIT © [MEOK AI Labs](https://meok.ai)
