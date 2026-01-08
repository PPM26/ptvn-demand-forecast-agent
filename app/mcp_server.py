import asyncio
from typing import Any
from fastmcp import FastMCP
from app.pipeline.demand_forecast_pipeline import DemandForecastPipeline
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("Demand Forecast Agent")

pipeline = None

def get_pipeline() -> DemandForecastPipeline:
    """Get or create the pipeline instance."""
    global pipeline
    if pipeline is None:
        pipeline = DemandForecastPipeline()
    return pipeline


@mcp.tool()
async def get_demand_forecast(item_names: str) -> str:
    """
    Get demand forecast for one or more items.
    
    This tool retrieves demand forecasts by:
    1. Matching item names against a knowledge base (RagFlow)
    2. Querying the database for forecast data
    3. Returning formatted forecast results
    
    Args:
        item_names: Single item name or comma-separated list of items.
                   Examples: "กระติกน้ำ" or "กระติกน้ำ, flap box, ตู้"
    
    Returns:
        Formatted demand forecast results including:
        - Item name (matched from knowledge base)
        - Demand forecast data
        
    Examples:
        >>> await get_demand_forecast("กระติกน้ำ")
        >>> await get_demand_forecast("กระติกน้ำ, flap box")
    """
    try:
        forecast_pipeline = get_pipeline()
        
        result = await forecast_pipeline.run(item_names)
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        return result.get("demand_forecast", "No forecast data available")
        
    except Exception as e:
        return f"Error processing demand forecast: {str(e)}"


@mcp.tool()
async def get_multiple_forecasts(items: list[str]) -> str:
    """
    Get demand forecasts for multiple items (as a list).
    
    Args:
        items: List of item names, e.g., ["กระติกน้ำ", "flap box", "ตู้"]
    
    Returns:
        Formatted demand forecast results for all items
    """
    try:
        forecast_pipeline = get_pipeline()
        
        result = await forecast_pipeline.run(items)
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        return result.get("demand_forecast", "No forecast data available")
        
    except Exception as e:
        return f"Error processing demand forecasts: {str(e)}"


if __name__ == "__main__":
    mcp.run()
