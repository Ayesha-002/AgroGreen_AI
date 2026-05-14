# config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")

# App settings
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", 8000))
GRADIO_PORT = int(os.getenv("GRADIO_PORT", 7860))
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
KNOWLEDGE_BASE_DIR = os.path.join(DATA_DIR, "knowledge_base")
DATASETS_DIR = os.path.join(DATA_DIR, "datasets")

# AI Settings
OPENAI_MODEL = "gpt-3.5-turbo"
EMBEDDING_MODEL = "text-embedding-ada-002"
MAX_TOKENS = 1000
TEMPERATURE = 0.7
