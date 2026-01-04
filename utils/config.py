import os

class Config:
    """Base Configuration"""
    ENV: str = "base"
    API_BASE_URL: str
    FRONTEND_BASE_URL: str
    TIMEOUT: int = 30000
    HEADLESS: bool = True
    
    @classmethod
    def get_mongo_uri(cls):
        return os.getenv("MONGODB_URI")
        
    @classmethod
    def get_mongo_db_name(cls):
        return os.getenv("MONGODB_DB_NAME", "test")

class LocalConfig(Config):
    """Local Development Environment"""
    ENV = "local"
    API_BASE_URL = "http://localhost:8000/api/v1"
    FRONTEND_BASE_URL = "http://localhost:3000"

class ProductionConfig(Config):
    """Production Environment (Default)"""
    ENV = "production"
    API_BASE_URL = "https://testing-box.onrender.com/api/v1" 
    FRONTEND_BASE_URL = "https://testing-box.vercel.app"

# Mapping for CLI
ENV_MAP = {
    "local": LocalConfig,
    "production": ProductionConfig
}

def get_config(env_name: str) -> type[Config]:
    # Default to Production as per user request
    return ENV_MAP.get(env_name, ProductionConfig)
