# MCP Server Usage Guide

This guide explains how to use the Model Context Protocol (MCP) server for the Demand Forecast Agent.

## Overview

The MCP server exposes the demand forecast pipeline as tools that can be used by:
- MCP Inspector
- Other MCP-compliant clients

It supports two transport modes:
1. **SSE (Server-Sent Events)**: Mounted on the FastAPI application. Recommended for development, debugging with Inspector, and when running as a web service.
2. **Stdio**: Direct standard input/output. Recommended for local integration with Claude Desktop.

## Available Tools

### `get_demand_forecast`

Get demand forecast for one or more items. Accepts both string and list inputs. It identifies the item via RagFlow and retrieves the latest forecast from the database.

**Parameters:**
- `item_names` (string | list): Single item name, comma-separated items, or list of items.

**Examples:**
- `"กระติกน้ำ"` (Single string)
- `"กระติกน้ำ, flap box"` (Comma-separated string)
- `["กระติกน้ำ", "flap box"]` (List of strings)

## Running the Server

### Option 1: FastAPI with SSE (Recommended for Inspector)

Run the main FastAPI application. This serves both the API and the MCP SSE endpoint.

```bash
uvicorn app.main:app --reload
```

- **API Root**: `http://localhost:8000`
- **MCP SSE Endpoint**: `http://localhost:8000/sse/sse` (Use this URL in your MCP client)

### Option 2: Stdio Mode (For Local Clients)

Run the standalone MCP script for communication over stdin/stdout:

```bash
python run_mcp_server.py
```

## Debugging with MCP Inspector

You can use the MCP Inspector to test tools interactively without setting up a full client.

1. Start the FastAPI server (Option 1 above).
2. In a new terminal, run the inspector pointing to the SSE endpoint:

```bash
npx @modelcontextprotocol/inspector http://localhost:8000/sse/sse
```

This will open a web interface in your browser where you can:
- View available tools
- Execute `get_demand_forecast` with different inputs
- View the tool output and JSON logs

### Recommended: Stdio Configuration

This method allows Claude Desktop to manage the server process automatically.

```json
{
  "mcpServers": {
    "demand-forecast": {
      "command": "/absolute/path/to/python",
      "args": ["/absolute/path/to/Pantavanij/demand_forecast_agent/run_mcp_server.py"],
      "env": {
        "PYTHONPATH": "/absolute/path/to/Pantavanij/demand_forecast_agent"
      }
    }
  }
}
```
**Note**: Replace `/absolute/path/to/...` with the actual full paths on your machine. You should use the python executable from your virtual environment (e.g., `.venv/bin/python`).

### Alternative: SSE Configuration

If you prefer to keep `uvicorn` running separately:

```json
{
  "mcpServers": {
    "demand-forecast-sse": {
      "url": "http://localhost:8000/sse/sse"
    }
  }
}
```

## Testing Logic Programmatically

To test the core forecasting logic without the MCP layer (avoiding FastMCP wrapper issues), import and use the pipeline directly:

```python
import asyncio
from app.pipeline.demand_forecast_pipeline import DemandForecastPipeline

async def test():
    # Initialize pipeline
    pipeline = DemandForecastPipeline()
    
    # Test with a single item
    print("Testing single item...")
    result = await pipeline.run("กระติกน้ำ")
    print(result)

if __name__ == "__main__":
    asyncio.run(test())
```

## Prerequisites & Troubleshooting

### Setup
1. **Install Dependencies**: 
   ```bash
   pip install -r requirements.txt
   ```
2. **Environment Variables**: Ensure `.env` contains:
   - `OPENAI_API_KEY`
   - `RAGFLOW_API_KEY` & `RAGFLOW_BASE_URL`
   - `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`

### Common Issues
- **Tool Call Fails**: Check the terminal running `uvicorn` for traceback errors.
- **Connection Refused**: Ensure the server is running on port 8000.
- **Import Errors**: Set `PYTHONPATH` to your project root if running scripts from outside the directory.
