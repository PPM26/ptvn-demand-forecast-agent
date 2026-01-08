from fastapi import FastAPI
from app.fastapi.routers import router as pipeline_router
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Demand Forecast Agent API",
    description="API for the Demand Forecast Agent Pipeline",
    version="1.0.0"
)

app.include_router(pipeline_router, tags=["Pipeline"])

@app.get("/")
async def root():
    return {"message": "Demand Forecast Agent API"}
    