from pydantic import BaseModel, Field
from typing import List

class ExtractedItems(BaseModel):
    items: List[str] = Field(..., description="List of item names extracted from the input text.")
