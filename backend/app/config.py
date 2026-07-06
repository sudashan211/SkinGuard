"""
Configuration management for SkinGuard backend
"""
import os
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings"""
    
    # Demo Mode
    demo_mode: bool = os.getenv("DEMO_MODE", "false").lower() == "true"
    
    # Use Real AI (can be true even in demo mode for hybrid operation)
    use_real_ai: bool = os.getenv("USE_REAL_AI", "false").lower() == "true"
    
    # Supabase Configuration
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_anon_key: str = os.getenv("SUPABASE_ANON_KEY", "")
    supabase_service_role_key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    
    # JWT Configuration
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_access_token_expire_minutes: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    jwt_refresh_token_expire_days: int = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    # API Configuration
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    api_reload: bool = os.getenv("API_RELOAD", "true").lower() == "true"
    
    # CORS Configuration - use string and parse manually to avoid pydantic JSON parsing
    cors_origins_str: str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173")
    
    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        if self.cors_origins_str:
            return [origin.strip() for origin in self.cors_origins_str.split(",")]
        return []
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from environment


settings = Settings()
