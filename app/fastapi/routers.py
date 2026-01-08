from fastapi import APIRouter, HTTPException, Depends
from app.fastapi.schemas import PipelineInput, PipelineResponse
from app.pipeline.demand_forecast_pipeline import DemandForecastPipeline

router = APIRouter()

def get_pipeline():
    return DemandForecastPipeline()

@router.get("/health")
async def health_check():
    return {"status": "ok"}

@router.post("/pipeline/run", response_model=PipelineResponse)
async def run_pipeline(data: PipelineInput, pipeline: DemandForecastPipeline = Depends(get_pipeline)):
    """
    Run the full Demand Forecast Pipeline.
    """
    try:
        result = await pipeline.run(data.input_data)
        return PipelineResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
