import subprocess
import time

services = [
    "python -m uvicorn data_ingestion.api_agent:app --host 0.0.0.0 --port 8001",
    "python -m uvicorn data_ingestion.scraper_agent:app --host 0.0.0.0 --port 8002",
    "python -m uvicorn agents.retriever_agent:app --host 0.0.0.0 --port 8003",
    "python -m uvicorn agents.analytics_agent:app --host 0.0.0.0 --port 8004",
    "python -m uvicorn agents.language_agent:app --host 0.0.0.0 --port 8005",
    "python -m uvicorn agents.voice_agent:app --host 0.0.0.0 --port 8006",
    "python -m uvicorn orchestrator.orchestrator:app --host 0.0.0.0 --port 8000"
]

processes = []
for service in services:
    process = subprocess.Popen(service.split())
    processes.append(process)
    time.sleep(1)  # Stagger startup to avoid port conflicts

try:
    for process in processes:
        process.wait()
except KeyboardInterrupt:
    for process in processes:
        process.terminate()