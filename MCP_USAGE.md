# MCP Server Usage Guide

This guide explains how to use the Model Context Protocol (MCP) server for the Demand Forecast Agent.

## What is the MCP Server?

The MCP server exposes your demand forecast pipeline as tools that AI assistants (like Claude Desktop, IDEs, or other MCP clients) can use to query demand forecasts for items.

## Available Tools

### 1. `get_demand_forecast`
Get demand forecast for one or more items using a comma-separated string.

**Parameters:**
- `item_names` (string): Single item name or comma-separated list

**Examples:**
```
get_demand_forecast("กระติกน้ำ")
get_demand_forecast("กระติกน้ำ, flap box, ตู้")
```

### 2. `get_multiple_forecasts`
Get demand forecasts for multiple items using a list.

**Parameters:**
- `items` (list): List of item names

**Example:**
```
get_multiple_forecasts(["กระติกน้ำ", "flap box", "ตู้"])
```

## Starting the MCP Server

### Basic Usage

```bash
cd /Users/ppm/Pantavanij/demand_forecast_agent
python run_mcp_server.py
```

### Prerequisites

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   Ensure your `.env` file contains required credentials for:
   - OpenAI API (for item selection)
   - RagFlow API (for knowledge base matching)
   - PostgreSQL database (for forecast data)

## Connecting AI Assistants

### Claude Desktop

1. **Locate the Claude Desktop config file:**
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. **Add the MCP server configuration:**
   ```json
   {
     "mcpServers": {
       "demand-forecast": {
         "command": "python",
         "args": [
           "/Users/ppm/Pantavanij/demand_forecast_agent/run_mcp_server.py"
         ],
         "env": {}
       }
     }
   }
   ```

3. **Restart Claude Desktop**

4. **Use the tools:**
   You can now ask Claude to get demand forecasts:
   - "Get the demand forecast for กระติกน้ำ"
   - "What's the forecast for flap box and ตู้?"

### Other MCP Clients

The server uses the standard MCP protocol and can be integrated with:
- IDEs with MCP support (VSCode, etc.)
- Custom MCP clients
- Other AI assistants supporting MCP

Refer to your client's documentation for specific integration steps.

## How It Works

When an AI assistant calls a tool:

1. **Item Matching:** The system matches input item names against a knowledge base (RagFlow) to find the exact product names
2. **Database Query:** Queries the PostgreSQL database for the latest demand forecast data
3. **Response Formatting:** Returns formatted results with item names and forecast data

## Troubleshooting

### Server Won't Start

- **Check dependencies:** Run `pip install -r requirements.txt`
- **Verify environment variables:** Ensure `.env` file has all required values
- **Check Python version:** Requires Python 3.10+

### Tool Calls Fail

- **Database connection:** Verify PostgreSQL connection details in `.env`
- **RagFlow API:** Ensure RagFlow API key and endpoint are correct
- **OpenAI API:** Check OpenAI API key is valid

### No Results Returned

- **Item not found:** The item may not exist in the RagFlow knowledge base
- **No forecast data:** The item may not have forecast data in the database
- **Check logs:** Run the server directly to see detailed error messages

## Development

### Testing the Server

You can test the server programmatically:

```python
import asyncio
from app.mcp_server import get_demand_forecast

async def test():
    result = await get_demand_forecast("กระติกน้ำ")
    print(result)

asyncio.run(test())
```

### Adding New Tools

To add new tools to the MCP server, edit `app/mcp_server.py` and use the `@mcp.tool()` decorator:

```python
@mcp.tool()
async def your_new_tool(param: str) -> str:
    """Tool description."""
    # Implementation
    return result
```

## Additional Resources

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Model Context Protocol Specification](https://spec.modelcontextprotocol.io/)
- [Claude Desktop MCP Setup](https://docs.anthropic.com/claude/docs/model-context-protocol)
