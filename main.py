"""
main.py — FastAPI Entrypoint for AI Enrichment System

Designed specifically to run on GCP Cloud Run.
Exposes generic endpoints that accept Pub/Sub push messages
and routes them to the requested capability engine.
"""
import logging
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from events.consumer import router as consumer_router
from core.registry import init_registry

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Enrichment System")

@app.on_event("startup")
async def startup_event():
    logger.info("Initializing AI Enrichment System...")
    init_registry()

# Register the consumer router which handles Pub/Sub pushes
app.include_router(consumer_router)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "ai-enrichment-system"}

from pydantic import BaseModel
from typing import Dict, Any
from core.registry import registry

class SyncExecuteRequest(BaseModel):
    capability: str
    payload: Dict[str, Any]

@app.post("/sync-execute")
async def sync_execute_capability(req: SyncExecuteRequest):
    """
    Synchronous endpoint for backend CRUD operations to invoke an AI capability
    and immediately get the result back.
    """
    try:
        capability = registry.get(req.capability)
    except KeyError:
        return JSONResponse(status_code=404, content={"error": f"Capability '{req.capability}' not found."})

    try:
        enrichment_result = await capability.execute(req.payload)
        return enrichment_result.dict()
    except Exception as e:
        logger.error(f"Capability {req.capability} failed: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})
