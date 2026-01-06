import os
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import json
from app.core.config import MODEL_API_KEY, MODEL_URL, MODEL_NAME, MODEL_TEMPERATURE
from app.core.schemas import ExtractedItems

from app.utils.item_parser import fix_item_format

class ItemExtractor:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=MODEL_API_KEY,
            base_url=MODEL_URL,
            model=MODEL_NAME,
            temperature=MODEL_TEMPERATURE
        )
        self.prompt_path = Path(__file__).parent.parent / "prompts" / "extract_item.txt"
        
    def _load_prompt(self) -> str:
        if not self.prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found at {self.prompt_path}")
        return self.prompt_path.read_text().strip()

    def extract(self, user_input: str) -> ExtractedItems:
        system_prompt = self._load_prompt()

        prompt = ChatPromptTemplate.from_messages([
            ("system", "{system_prompt}"),
            ("user", "Extract items from this: {user_input}")
        ])

        structured_llm = self.llm.with_structured_output(ExtractedItems)
        chain = prompt | structured_llm

        result = chain.invoke({
            "system_prompt": system_prompt,
            "user_input": user_input
        })
        
        # Normalize item format
        # result.items = [fix_item_format(item) for item in result.items]
        return result

if __name__ == "__main__":
    extractor = ItemExtractor()
    # sample_text = "I need to order 5 สารเคมีอื่น ๆ and ค่าที่ปรึกษา Pm."
    sample_text = "demand กระติกน้ำร้อน และ ตู้เตรียม เดือนตุลาคมเกิน 3% ไหม"
    http_result = extractor.extract(sample_text)
    print(f"Input: {sample_text}")
    print(f"Extracted: {http_result.items}")
