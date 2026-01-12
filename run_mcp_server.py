if __name__ == "__main__":
    from app.mcp_server import mcp
    
    print("Starting Demand Forecast MCP Server...")
    print("Available tools:")
    print("  - get_demand_forecast: Get forecast for item(s) as string or list")
    print("\nServer is running...")
    
    mcp.run()
