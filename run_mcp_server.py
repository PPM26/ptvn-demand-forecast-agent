#!/usr/bin/env python
"""
Entry point script to run the MCP server for the Demand Forecast Agent.

Usage:
    python run_mcp_server.py
"""

if __name__ == "__main__":
    from app.mcp_server import mcp
    
    print("Starting Demand Forecast MCP Server...")
    print("Available tools:")
    print("  - get_demand_forecast: Get forecast for item(s) as comma-separated string")
    print("  - get_multiple_forecasts: Get forecasts for items as a list")
    print("\nServer is running...")
    
    mcp.run()
