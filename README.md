# AI Enrichment System (`ai-enrichment-system`)

The **AI Enrichment System** is the intelligence pipeline for the CareerScope platform. It is a highly decoupled, horizontally scalable, event-driven microservice responsible for extracting structured intelligence from chaotic, unstructured job market data.

Unlike legacy linear processing pipelines, this system operates on an **Event Choreography** pattern via GCP Pub/Sub. Each AI extraction task is treated as an independent "Capability" that can scale, fail, and retry in complete isolation.

---

## 🏗️ Architecture & Philosophy

1. **Absolute Decoupling:** 
   This system is entirely decoupled from the core Django monolith (`backend`) and the ingestion engine (`data-ingestion-system`). It exists solely to perform heavy LLM inferences (via `pydantic-ai` and `langchain`) without bloating the core API servers.
2. **Capability-Driven Design:** 
   Instead of a monolithic pipeline (`scrape -> parse -> embed`), intelligence is broken down into atomic **Capabilities** (e.g., `skill_extraction`, `classification`, `embedding_generation`).
3. **Stateless Idempotency:** 
   Workers hold no state. If a worker dies mid-extraction, Pub/Sub simply redelivers the message to another worker.
4. **Immutable Enrichment Logs:** 
   The system never overwrites original job data. All AI inferences are written as append-only records to the `JobEnrichments` table with exact `confidence_score`, `model_name`, and `prompt_version` metadata.

---

## 🧠 The Capability Registry

All AI logic resides in the `capabilities/` directory. Every worker implements the abstract `Capability` contract defined in `capabilities/base.py`.

### Current Capabilities:
- **`skill_extraction`**: Reads raw job descriptions and extracts a clean array of required hard and soft skills.
- **`classification`**: Infers structured metadata such as Seniority Level (Junior, Mid, Senior), Employment Type (Full-Time, Contract), and Salary Ranges.
- **`normalization`**: (Dependency) Cleans raw HTML and sanitizes text before other capabilities execute.
- **`embedding_generation`**: Converts the enriched text into dense vector embeddings for downstream use by the Personalization Engine.

### Dynamic Dependency Resolution
Capabilities explicitly define their dependencies. For example, `skill_extraction` declares `normalization` as a dependency. The Event Router will automatically reject and defer execution if downstream dependencies are not yet marked `COMPLETED` in the database.

---

## 🔄 Event Choreography Flow

The system does not use a master orchestrator to route jobs through stages. It uses **Event Choreography**:

1. **Ingestion Trigger:** `data-ingestion-system` publishes a `job_created` event to the `raw-jobs` Pub/Sub topic.
2. **Execution Request:** The generic `/workers/execute` endpoint receives the push event.
3. **Registry Lookup:** The endpoint dynamically loads the requested capability (e.g., `normalization`) from the Registry.
4. **Inference & Persistence:** The capability executes using an LLM and saves the versioned output to the database.
5. **Choreography Ping:** The router checks the Registry for any downstream capabilities that depend on `normalization` (e.g., `skill_extraction`) and publishes *new* events to the bus to trigger them.

This creates a highly resilient chain reaction where every capability scales independently based on its specific compute requirements.

---

## 🚀 Deployment (GCP Cloud Run)

This service is optimized for deployment on Google Cloud Run. 

Because capabilities are dynamically loaded, you can deploy the exact same Docker container to multiple Cloud Run services, simply binding different Pub/Sub push subscriptions to them to create dedicated worker pools:
- `Service A (Skill Extractors)` ← Listens to `extract-skills` topic.
- `Service B (Embedders)` ← Listens to `generate-embeddings` topic.

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the FastAPI worker
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```
