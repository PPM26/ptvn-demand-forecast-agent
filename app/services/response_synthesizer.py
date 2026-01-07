import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.core.config import MODEL_API_KEY, MODEL_URL, MODEL_NAME, MODEL_TEMPERATURE

class ResponseSynthesizer:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=MODEL_API_KEY,
            base_url=MODEL_URL,
            model=MODEL_NAME,
            temperature=MODEL_TEMPERATURE
        )
        self.prompt_path = Path(__file__).parent.parent / "prompts" / "synthesize_response.txt"

    def _load_prompt(self) -> str:
        if not self.prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found at {self.prompt_path}")
        return self.prompt_path.read_text().strip()

    def synthesize(self, user_query: str, results: List[Dict[str, Any]]) -> str:
        system_prompt = self._load_prompt()
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "{system_prompt}"),
            ("user", "Query: {user_query}\nContext Data:\n{context_data}")
        ])

        chain = prompt | self.llm | StrOutputParser()

        # Format results into a readable context string
        context_parts = []
        for i, res in enumerate(results, 1):
            item_name = res.get("extracted_item", "Unknown Item")
            selected = res.get("selected_item", "None")
            forecast = res.get("demand_forecast", "No data found")
            
            part = (
                f"Item {i}: {item_name}\n"
                f"  - Selected Candidate: {selected}\n"
                f"  - Forecast Data: {forecast}\n"
            )
            context_parts.append(part)
        
        context_data = "\n".join(context_parts)

        return chain.invoke({
            "system_prompt": system_prompt,
            "user_query": user_query,
            "context_data": context_data
        })

if __name__ == "__main__":
    # Test block
    synthesizer = ResponseSynthesizer()
    print("Testing ResponseSynthesizer...")
    response = synthesizer.synthesize(
        user_query="what is the forecast of flapbox",
        results=[{
             "extracted_item": "flapbox",
             "selected_item": "Flap_Box_Type_1",
             "demand_forecast": {"date": "2023-10-01", "qty": 500, "meta": "high demand"}
        }]
    )
    print("\n--- Response ---")
    print(response)
