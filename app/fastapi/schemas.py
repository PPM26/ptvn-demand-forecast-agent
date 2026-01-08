from pydantic import BaseModel
from typing import List, Union

class PipelineInput(BaseModel):
    input_data: Union[str, List[str]]

class PipelineResponse(BaseModel):
    demand_forecast: str
