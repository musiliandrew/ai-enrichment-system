# CareerScoper AI Enrichment System

The AI Enrichment System is a **stateless FastAPI microservice** dedicated to natural language processing and semantic enrichment. It abstracts all interactions with Large Language Models (LLMs) away from the main CareerScoper API.

It is built with **FastAPI**, **`pydantic-ai`**, and deeply integrates with the **Google Gemini API**.

## Architecture Overview
This microservice operates purely as an enrichment pipeline. It does not touch a database directly. It receives unstructured or raw data, processes it through specific AI "Capabilities," and returns structured JSON.

1. **Capability Registry:** Uses a clean, scalable registry pattern (`core/registry.py`) to easily add new AI skills (e.g., parsing resumes, extracting Tech Trends, analyzing market insights).
2. **Standardized Provider:** Standardized on `gemini-1.5-flash` for high-throughput, low-cost operations, and `gemini-1.5-pro` for complex deep-reasoning tasks.
3. **Stateless Execution:** Handles HTTP POST requests containing data payloads, processes them synchronously, and returns the enriched data back to the caller (usually the Django monolith or Data Ingestion System).

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

- **`POST /sync-execute`**: The primary endpoint. Provide a JSON payload with a `capability` name and the raw `payload` data to execute an AI enrichment task synchronously.
  
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
