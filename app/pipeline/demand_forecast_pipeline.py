import asyncio
from typing import Dict, Any, Optional
from app.services.item_extractor import ItemExtractor
from app.services.ragflow_service import RagFlowService
from app.services.db_service import get_demand_forecast
from app.services.response_synthesizer import ResponseSynthesizer

class DemandForecastPipeline:
    def __init__(self):
        self.extractor = ItemExtractor()
        self.rag_service = RagFlowService()
        self.synthesizer = ResponseSynthesizer()

    async def run(self, user_query: str) -> Dict[str, Any]:
        """
        Executes the full pipeline:
        1. Extract item from user query
        2. Retrieve candidates from RagFlow
        3. Select best match
        4. Query DB for demand forecast
        """
        print(f"--- Starting Demand Forecast Pipeline: {user_query} ---")
        
        # 1. Extract Item
        extraction_result = self.extractor.extract(user_query)
        if not extraction_result.items:
            print("No items extracted.")
            return {"error": "No items extracted from query"}
        
        target_items = extraction_result.items
        print(f"Extracted Items: {target_items}")

        # Process each extracted item
        results = []
        for target_item in target_items:

            # 2 & 3. Process with RagFlow (Retrieve + Select Best Match)
            # RagFlowService.process_item does retrieve + selection
            selected_item = await self.rag_service.process_item(target_item)
            
            if not selected_item or selected_item == "None":
                print(f"No valid item selected from RagFlow for {target_item}.")
                results.append({
                    "extracted_item": target_item,
                    "selected_item": None,
                    "demand_forecast": None,
                    "message": "Could not find a matching item in the RagFlow candidates."
                })
                continue

            # 4. Get Demand Forecast from DB
            print(f"Querying DB for selected item: {selected_item}")
            forecast = get_demand_forecast(selected_item)

            # 5. Synthesize Answer
            print("Synthesizing answer...")
            answer = self.synthesizer.synthesize(
                user_query=user_query,
                extracted_item=target_item,
                selected_item=selected_item,
                forecast_data=forecast
            )
            
            result = {
                # "extracted_item": target_item,
                # "selected_item": selected_item,
                # "demand_forecast": forecast,
                "answer": answer
            }
            results.append(result)
        
        print("--- Pipeline Finished ---")
        return {"results": results}

if __name__ == "__main__":
    async def main():
        pipeline = DemandForecastPipeline()
        # Test query
        test_query = "demand กระติกน้ำร้อน และ ตู้เตรียม เดือนตุลาคมเกิน 3% ไหม"
        result = await pipeline.run(test_query)
        print("\nFinal Result Output:")
        print(result)

    asyncio.run(main())
