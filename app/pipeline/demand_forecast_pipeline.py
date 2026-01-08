import asyncio
from typing import Dict, Any, List, Union
from app.services.ragflow_service import RagFlowService
from app.services.db_service import get_demand_forecast

class DemandForecastPipeline:
    def __init__(self):
        self.rag_service = RagFlowService()

    async def run(self, input_data: Union[str, List[str]]) -> Dict[str, Any]:
        """
        Executes the pipeline:
        1. Accept (list of) items
        2. Retrieve best match item from RagFlow
        3. Query DB for demand forecast
        4. Return formatted results
        """
        print(f"--- Starting Demand Forecast Pipeline with input: {input_data} ---")
        
        # 1. Normalize Input
        target_items = []
        if isinstance(input_data, str):
            if "," in input_data:
                target_items = [item.strip() for item in input_data.split(",") if item.strip()]
            else:
                target_items = [input_data]
        elif isinstance(input_data, list):
            target_items = input_data
        else:
            return {"error": "Invalid input format. Expected string or list."}

        # 2. Process Items
        processed_results = []
        for target_item in target_items:
            # Retrieve + Select Best Match
            selected_item = await self.rag_service.process_item(target_item)
            
            if not selected_item or selected_item == "None":
                print(f"No valid item selected from RagFlow for {target_item}.")
                processed_results.append({
                    "input_item": target_item,
                    "selected_item": None,
                    "demand_forecast": None,
                    "message": "Could not find a matching item in the RagFlow candidates."
                })
                continue

            # Query DB
            print(f"Querying DB for selected item: {selected_item}")
            forecast = get_demand_forecast(selected_item)
            
            processed_results.append({
                "input_item": target_item,
                "selected_item": selected_item,
                "demand_forecast": forecast
            })

        # 3. Format Answer
        answer = self._format_response(processed_results)
        
        final_output = {
            "results": processed_results,
            "demand_forecast": answer
        }
        
        print("--- Pipeline Finished ---")
        return final_output
    
    def _format_response(self, results: List[Dict[str, Any]]) -> str:
        if not results:
            return "No results processed."
        
        # Helper to format a single forecast dict
        def format_forecast_data(data: Dict[str, Any]) -> str:
            if not data:
                return "No forecast data found."

            val = data.get('demand_forecast', 'N/A')
            return f"Forecast: {val}"

        # If single item
        if len(results) == 1:
            res = results[0]
            matched_name = res['selected_item']
            forecast = res['demand_forecast']
            header = f"### Item: {matched_name}"
            
            if forecast:
                content = format_forecast_data(forecast)
            else:
                content = f"No demand forecast found for item '{res['input_item']}' (RagFlow Matched: {res['selected_item']})."
            
            return f"{header}\n{content}"

        # If multiple items
        lines = []
        for res in results:
            matched_name = res['selected_item']
            forecast = res['demand_forecast']
            
            header = f"### Item: {matched_name}"
            
            content = format_forecast_data(forecast)
            
            lines.append(f"{header}\n{content}")
        
        return "\n\n".join(lines)

if __name__ == "__main__":
    async def main():
        pipeline = DemandForecastPipeline()
        
        # Test 1: String Item(s)
        # print("Testing string Item(s)...")
        # res1 = await pipeline.run("กระติกน้ำ, flap box, ตู้")
        # print("Result:\n", res1['demand_forecast'])
        
        # print("-" * 20)
        
        # Test 2: List Item(s)
        print("Testing list Item(s)...")
        res2 = await pipeline.run(["กระติกน้ำ", "flap box", "ตู้"])
        print("Result:\n", res2['demand_forecast'])

    asyncio.run(main())