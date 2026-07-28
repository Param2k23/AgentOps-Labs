import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Paths
BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR / "datasets"
DATASET_DIR.mkdir(exist_ok=True)

# API Config
API_BASE_URL = os.getenv("BENCHMARK_API_URL", "http://localhost:8000/api/v1")

# Document Generation
DOCUMENT_CATEGORIES = [
    "employee handbook",
    "IT incident report",
    "HR policy",
    "security policy",
]
DOCUMENT_SIZES = ["Small", "Medium"]
DOCUMENTS_PER_CATEGORY = 1

# Task Generation
TASKS_PER_DOCUMENT = 2

# Evaluation & Models
if os.getenv("LLM_PROVIDER", "gemini").lower() == "openrouter":
    DEFAULT_MODELS = ["google/gemma-4-31b-it:free"]
else:
    DEFAULT_MODELS = ["gemini-2.5-flash"]
    
CONCURRENCY = int(os.getenv("BENCHMARK_CONCURRENCY", "1"))

# API keys for Gemini (dataset generation)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
