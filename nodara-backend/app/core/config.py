import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SAP_ENV: str = os.getenv("SAP_ENV", "dev.local")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://nodara_user:NodaraPass2026!@postgres-service:5432/nodara_db")
    SAP_IS_BASE_URL: str = os.getenv("SAP_IS_BASE_URL", "http://s4-sim-service:8000")
    LANGFUSE_HOST: str = os.getenv("LANGFUSE_HOST", "http://langfuse-service:3000")
    LANGFUSE_PUBLIC_KEY: str = os.getenv("LANGFUSE_PUBLIC_KEY", "")
    LANGFUSE_SECRET_KEY: str = os.getenv("LANGFUSE_SECRET_KEY", "")
    SAP_AICORE_CLIENT_ID: str = os.getenv("SAP_AICORE_CLIENT_ID", "")
    SAP_AICORE_CLIENT_SECRET: str = os.getenv("SAP_AICORE_CLIENT_SECRET", "")
    SAP_AICORE_AUTH_URL: str = os.getenv("SAP_AICORE_AUTH_URL", "")
    SAP_AICORE_BASE_URL: str = os.getenv("SAP_AICORE_BASE_URL", "")
    SAP_AICORE_RESOURCE_GROUP: str = os.getenv("SAP_AICORE_RESOURCE_GROUP", "default")
    SAP_OPENAI_DEPLOYMENT_ID: str = os.getenv("SAP_OPENAI_DEPLOYMENT_ID", "gpt-4o")

settings = Settings()
