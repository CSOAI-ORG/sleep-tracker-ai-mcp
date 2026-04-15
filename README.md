# Sleep Tracker Ai

> By [MEOK AI Labs](https://meok.ai) — Track sleep duration and quality, analyse patterns, and get personalised sleep recommendations. By MEOK AI Labs.

Sleep Tracker AI — log sleep, analyse patterns, and get personalised recommendations. MEOK AI Labs.

## Installation

```bash
pip install sleep-tracker-ai-mcp
```

## Usage

```bash
# Run standalone
python server.py

# Or via MCP
mcp install sleep-tracker-ai-mcp
```

## Tools

### `log_sleep`
Log a sleep entry. Hours slept, quality 1-10 (10=best), optional bedtime/wake_time (HH:MM), and notes.

**Parameters:**
- `hours` (float)
- `quality` (int)
- `bedtime` (str)
- `wake_time` (str)
- `notes` (str)

### `get_sleep_stats`
Get sleep statistics over the last N days. Includes averages, trends, and consistency scores.

**Parameters:**
- `days` (int)

### `analyze_patterns`
Analyse sleep patterns to find correlations between bedtime, duration, quality, and notes.

### `get_recommendations`
Get personalised sleep improvement recommendations based on your logged data.


## Authentication

Free tier: 15 calls/day. Upgrade at [meok.ai/pricing](https://meok.ai/pricing) for unlimited access.

## Links

- **Website**: [meok.ai](https://meok.ai)
- **GitHub**: [CSOAI-ORG/sleep-tracker-ai-mcp](https://github.com/CSOAI-ORG/sleep-tracker-ai-mcp)
- **PyPI**: [pypi.org/project/sleep-tracker-ai-mcp](https://pypi.org/project/sleep-tracker-ai-mcp/)

## License

MIT — MEOK AI Labs
