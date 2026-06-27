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
