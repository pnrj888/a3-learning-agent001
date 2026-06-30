import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

os.makedirs(PROJECT_ROOT / "data" / "chroma", exist_ok=True)
os.makedirs(PROJECT_ROOT / "data" / "database", exist_ok=True)
os.makedirs(PROJECT_ROOT / "data" / "pdfs", exist_ok=True)
os.makedirs(PROJECT_ROOT / "logs", exist_ok=True)


class SparkConfig:
    APP_ID = os.environ.get("SPARK_APP_ID", "")
    API_KEY = os.environ.get("SPARK_API_KEY", "")
    API_SECRET = os.environ.get("SPARK_API_SECRET", "")
    API_URL = os.environ.get("SPARK_API_URL", "wss://spark-api.xf-yun.com/v3.5/chat")


class MultiModalConfig:
    APP_ID = os.environ.get("MULTIMODAL_APP_ID", "")
    API_KEY = os.environ.get("MULTIMODAL_API_KEY", "")
    API_SECRET = os.environ.get("MULTIMODAL_API_SECRET", "")
    IMAGE_API_URL = os.environ.get("IMAGE_API_URL", "https://api.xf-yun.com/v1/private/sd")
    VIDEO_API_URL = os.environ.get("VIDEO_API_URL", "https://api.xf-yun.com/v1/private/sv")


class ChromaConfig:
    PERSIST_DIRECTORY = os.environ.get("CHROMA_PERSIST_DIR", str(PROJECT_ROOT / "data" / "chroma"))


class DatabaseConfig:
    SQLITE_PATH = os.environ.get("SQLITE_PATH", str(PROJECT_ROOT / "data" / "database" / "app.db"))


class KnowledgeBaseConfig:
    PDF_DIR = os.environ.get("PDF_DIR", str(PROJECT_ROOT / "data" / "pdfs"))


class CrewAIConfig:
    LOGGING_ENABLED = os.environ.get("CREWAI_LOGGING", "false").lower() == "true"
