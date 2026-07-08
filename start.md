# Start AI Enrichment System Locally

Open a terminal and navigate to the `ai-enrichment-system` directory:
```bash
cd ~/Desktop/Projects/CareerScoper/ai-enrichment-system
```

Create and activate a virtual environment (only needed once):
```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Start the FastAPI server:
```bash
uvicorn main:app --host 0.0.0.0 --port 8002 --reload
```
This service will run on **Port 8002**.
