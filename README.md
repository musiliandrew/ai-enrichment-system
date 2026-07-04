# AI Enrichment System

A **stateless FastAPI microservice** dedicated to natural language processing and semantic data enrichment. It abstracts all interactions with Large Language Models (LLMs) into clean, distinct "Capabilities" designed to run entirely detached from generic application APIs.

Built with **FastAPI**, **`pydantic-ai`**, and seamlessly integrated with the **Google Gemini API**.

## Architecture Overview
This microservice operates purely as an enrichment pipeline with zero database coupling. It receives raw unstructured data, processes it through isolated capability modules, and returns strictly typed JSON structures.

1. **Capability Registry Pattern:** Uses a scalable registry (`core/registry.py`) to easily drop in new AI skills (e.g., parsing documents, extracting entity trends, sentiment analysis) without modifying the core server.
2. **Provider Agnostic (Default: Gemini):** Configured for high-throughput, low-cost operations via Gemini 1.5 Flash, with the ability to route to reasoning models (Gemini 1.5 Pro) for complex analytical tasks.
3. **Stateless Execution:** Handles HTTP POST requests containing data payloads, processes them synchronously, and immediately returns the enriched schema.

## Running Locally

1. Create a virtual environment: `python -m venv env`
2. Activate it: `source env/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Set environment variables (requires `GEMINI_API_KEY`):
   ```bash
   cp .env.example .env
   ```
5. Run the server:
   ```bash
   uvicorn main:app --reload --port 8002
   ```

## Key API Endpoints

- **`POST /sync-execute`**: The primary interaction endpoint. Provide a JSON payload specifying a registered `capability` name and the raw `payload` data to execute an AI task synchronously.
  
### Example Request
```json
{
  "capability": "tech_trends",
  "payload": {
    "technologies": ["Python", "React", "GCP"],
    "news_titles": ["Google Cloud releases new AI tools", "Python 3.14 announced"]
  }
}
```

### Example Response
```json
{
  "status": "success",
  "result": {
    "trending_skills": ["GCP Cloud AI"],
    "obsolete_skills": [],
    "market_summary": "High demand for integrated cloud AI tools."
  }
}
```
