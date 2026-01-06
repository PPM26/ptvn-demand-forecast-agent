import os
from pathlib import Path
from typing import Dict, Any, Optional
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

    def synthesize(self, user_query: str, extracted_item: str, selected_item: Optional[str], forecast_data: Optional[Dict[str, Any]]) -> str:
        system_prompt = self._load_prompt()
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "{system_prompt}"),
            ("user", "Query: {user_query}\nExtracted Item: {extracted_item}\nSelected Item: {selected_item}\nData: {forecast_data}")
        ])

        chain = prompt | self.llm | StrOutputParser()

        # Handle None for data to avoid string conversion errors or awkward "None" strings if possible, 
        # though the prompt handles "None" explicitly.
        forecast_str = str(forecast_data) if forecast_data else "No data found"
        selected_str = str(selected_item) if selected_item else "None"

        return chain.invoke({
            "system_prompt": system_prompt,
            "user_query": user_query,
            "extracted_item": extracted_item,
            "selected_item": selected_str,
            "forecast_data": forecast_str
        })

if __name__ == "__main__":
    # Test block
    synthesizer = ResponseSynthesizer()
    print("Testing ResponseSynthesizer...")
    response = synthesizer.synthesize(
        user_query="what is the forecast of flapbox",
        extracted_item="flapbox",
        selected_item="Flap_Box_Type_1",
        forecast_data={"date": "2023-10-01", "qty": 500, "meta": "high demand"}
    )
    print("\n--- Response ---")
    print(response)
