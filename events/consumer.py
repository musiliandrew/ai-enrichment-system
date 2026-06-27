"""
events/consumer.py — Generic Event Router for AI Capabilities

Handles incoming Pub/Sub Push events. Extracts the requested capability,
loads it from the registry, executes it statelessly, and triggers downstream events.
"""
import logging
import base64
import json
import uuid
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Request, Response
from core.registry import registry
from capabilities.base import EnrichmentResult

router = APIRouter(prefix="/workers", tags=["Workers"])
logger = logging.getLogger(__name__)

# --- Mock DB Helpers for Architecture Demo ---
def _check_dependencies_met(job_id: str, dependencies: list) -> bool:
    """Mock query to JobProcessingState to see if deps are COMPLETED."""
    # In reality: SELECT capability_statuses FROM job_processing_state WHERE job_id = ?
    return True

def _save_enrichment(job_id: str, capability_name: str, result: EnrichmentResult):
    """Mock query to insert into JobEnrichments."""
    # In reality: INSERT INTO job_enrichments ...
    pass

def _update_processing_state(job_id: str, capability_name: str, status: str):
    """Mock query to update capability_statuses in JobProcessingState."""
    # In reality: UPDATE job_processing_state SET capability_statuses = jsonb_set(...)
    pass

def _publish_event(topic: str, event_type: str, payload: Dict[str, Any]):
    """Mock publish to Pub/Sub EventBus."""
    # In reality: Use the same EventBus wrapper as data-ingestion-system
    pass
# ---------------------------------------------


@router.post("/execute")
async def execute_capability(request: Request):
    """
    Generic endpoint. The Pub/Sub subscription should pass the capability 
    name in the payload or as a query param. For this example, we assume 
    the payload dictates what to run.
    """
    try:
        envelope = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    message = envelope.get("message", {})
    if "data" not in message:
        return Response(status_code=204)

    try:
        decoded_data = base64.b64decode(message["data"]).decode("utf-8")
        event_payload = json.loads(decoded_data)
    except Exception as e:
        logger.error(f"Failed to decode payload: {e}")
        return Response(status_code=204)

    job_id = event_payload.get("job_id")
    target_capability = event_payload.get("capability")
    
    if not job_id or not target_capability:
        logger.error("Payload missing job_id or target capability.")
        return Response(status_code=204)

    try:
        capability = registry.get(target_capability)
    except KeyError:
        logger.error(f"Requested capability '{target_capability}' not registered.")
        return Response(status_code=204)

    # 1. Dependency Check
    if not _check_dependencies_met(job_id, capability.dependencies):
        logger.warning(f"Dependencies not met for {target_capability} on job {job_id}. Dropping event.")
        # We ack the message. A future event will re-trigger this when deps are met.
        return Response(status_code=200)

    # 2. Update Operational State to IN_PROGRESS
    _update_processing_state(job_id, target_capability, "IN_PROGRESS")

    try:
        # 3. Execute Stateless AI Logic
        logger.info(f"Executing '{target_capability}' for job {job_id}...")
        enrichment_result = await capability.execute(event_payload)
        
        # 4. Save Versioned AI Result (JobEnrichments table)
        _save_enrichment(job_id, target_capability, enrichment_result)
        
        # 5. Mark COMPLETED
        _update_processing_state(job_id, target_capability, "COMPLETED")
        
        # 6. Event Choreography: Trigger Downstream Capabilities
        downstream = registry.get_downstream_capabilities(target_capability)
        for downstream_cap in downstream:
            logger.info(f"Triggering downstream capability: {downstream_cap.name}")
            _publish_event(
                topic="ai-enrichment-tasks",
                event_type="execute_capability",
                payload={"job_id": job_id, "capability": downstream_cap.name}
            )
            
    except Exception as e:
        logger.error(f"Capability {target_capability} failed: {e}")
        _update_processing_state(job_id, target_capability, "FAILED")
        # Returning 500 triggers Pub/Sub Exponential Backoff & Retry!
        raise HTTPException(status_code=500, detail="Execution failed")

    return Response(status_code=200)
