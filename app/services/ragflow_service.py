import csv
import json
import asyncio
from pathlib import Path
from typing import List, Any, Optional, Dict

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from ragflow_sdk import RAGFlow

from app.core.config import (
    RAGFLOW_URL,
    RAGFLOW_API_KEY,
    RAGFLOW_PO_DATASET_IDS,
    TOP_K,
    MODEL_API_KEY,
    MODEL_URL,
    MODEL_NAME,
    MODEL_TEMPERATURE,
)


class RagFlowService:
    def __init__(self):
        try:
            self.rag_client = RAGFlow(
                api_key=RAGFLOW_API_KEY,
                base_url=RAGFLOW_URL,
            )
            print("[RAGFLOW] Client initialized successfully.")
        except Exception as e:
            print(f"[RAGFLOW] Could not initialize RAGFlow client: {e}. Falling back to empty results.")
            self.rag_client = None

        self.llm = ChatOpenAI(
            api_key=MODEL_API_KEY,
            base_url=MODEL_URL,
            model=MODEL_NAME,
            temperature=MODEL_TEMPERATURE
        )
        self.prompt_path = Path(__file__).parent.parent / "prompts" / "select_item.txt"

    def _load_prompt(self) -> str:
        if not self.prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found at {self.prompt_path}")
        return self.prompt_path.read_text().strip()

    async def _retrieve(self, question: str, top_k: int = None) -> List[Any]:
        if not self.rag_client:
            return []

        if top_k is None:
            top_k = TOP_K

        loop = asyncio.get_running_loop()

        def _call():
            # sync call into SDK
            return self.rag_client.retrieve(
                dataset_ids=RAGFLOW_PO_DATASET_IDS,
                question=question,
                top_k=top_k,
            )

        try:
            # hard timeout so no single RAG call can hang the whole pipeline
            result = await asyncio.wait_for(
                loop.run_in_executor(None, _call),
                timeout=45,  # seconds
            )
            return list(result or [])
        except asyncio.TimeoutError:
            print(f"[RAGFLOW TIMEOUT] question='{question}' (top_k={top_k})")
            return []
        except Exception as e:
            print(f"[RAGFLOW] Error during retrieve (question='{question}'): {e}")
            return []

    @staticmethod
    def _parse_chunk_text(text: str) -> Dict[str, Any]:
        """
        Parse RagFlow chunk text of the form:
        header1,header2,...,headerN:value1,value2,...,valueN

        Handles quoted headers/values and commas properly using csv.reader.
        Returns dict mapping header -> value (both as strings).
        """
        if not text or ":" not in text:
            return {}

        header_part, value_part = text.split(":", 1)

        # Use csv.reader to correctly parse quotes and commas
        header_reader = csv.reader([header_part])
        value_reader = csv.reader([value_part])

        try:
            headers = next(header_reader)
            values = next(value_reader)
        except StopIteration:
            return {}

        # strip whitespace around headers/values
        headers = [h.strip() for h in headers]
        values = [v.strip() for v in values]

        # zip into dict
        row = {}
        for h, v in zip(headers, values):
            row[h] = v

        return row

    @staticmethod
    def _get_from_mapping(mapping, candidate_keys):
        """Try multiple key variants against a dict-like mapping."""
        if not mapping:
            return None
        for k in candidate_keys:
            if k in mapping:
                return mapping[k]
        # normalized (lowercase, no spaces/quotes/underscores)
        norm_map = {
            "".join(ch for ch in key.lower() if ch.isalnum()): v
            for key, v in mapping.items()
        }
        for k in candidate_keys:
            norm_k = "".join(ch for ch in k.lower() if ch.isalnum())
            if norm_k in norm_map:
                return norm_map[norm_k]
        return None

    @classmethod
    def _get_field(cls, rec: Any, candidate_keys: List[str]):
        """
        Try to get a field from:
        - top-level dict
        - rec.metadata (if object-like)
        """
        if isinstance(rec, dict):
            val = cls._get_from_mapping(rec, candidate_keys)
            if val is not None:
                return val
            meta = rec.get("metadata") or {}
            return cls._get_from_mapping(meta, candidate_keys)

        # object-like result
        meta = getattr(rec, "metadata", {}) or {}
        # direct attributes first
        for k in candidate_keys:
            if hasattr(rec, k):
                return getattr(rec, k)
        # metadata attributes / keys 
        val = cls._get_from_mapping(meta, candidate_keys)
        if val is not None:
            return val

        return None

    async def select_best_match(self, extracted_items: str, candidates: List[Any]) -> str:
        if not candidates:
            return "None"
        
        candidate_texts = []
        for c in candidates:
            # TRY to get structured content first
            content_str = self._get_field(c, ["content_with_weight", "content", "text_content"])
            
            # If we found content strings, try to parse them if they look like header:value
            if content_str and isinstance(content_str, str):
                parsed = self._parse_chunk_text(content_str)
                if parsed:
                    # Successfully parsed structured data -> convert to JSON line or readable text
                    candidate_texts.append(json.dumps(parsed, ensure_ascii=False))
                else:
                    # unstructured text
                    candidate_texts.append(content_str)
            else:
                # Fallback: stringify the whole object if content not found
                candidate_texts.append(str(c))
        
        candidate_list_str = "\n".join([f"- {c}" for c in candidate_texts])

        system_prompt = self._load_prompt()
        prompt = ChatPromptTemplate.from_messages([
            ("system", "{system_prompt}"),
            ("user", "User Input Item: {extracted_items}\n\nCandidate Items:\n{candidates}")
        ])
        
        chain = prompt | self.llm
        
        try:
            result = await chain.ainvoke({
                "system_prompt": system_prompt,
                "extracted_items": extracted_items,
                "candidates": candidate_list_str
            })
            return result.content.strip()
        except Exception as e:
            print(f"[RAGFLOW] Error during selection: {e}")
            return "None"

    async def process_item(self, item_name: str) -> str:
        """
        Retrieves candidates from RagFlow and selects the best match.
        """
        print(f"[RAGFLOW] Processing item: {item_name}")
        candidates = await self._retrieve(item_name)
        print(f"[RAGFLOW] Retrieved {len(candidates)} candidates.")
        
        selected_item = await self.select_best_match(item_name, candidates)
        print(f"[RAGFLOW] Selected item: {selected_item}")
        return selected_item

if __name__ == "__main__":
    # Test block
    import asyncio
    
    async def main():
        service = RagFlowService()
        result = await service.process_item("flap box")
        print(f"Final Result: {result}")

    asyncio.run(main())
