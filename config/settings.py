"""Configuration settings for RSP Harmonization Engine."""

from pathlib import Path
from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # API Configuration
    anthropic_api_key: Optional[str] = Field(
        default=None,
        description="Anthropic API key for Claude access"
    )
    
    # Model Configuration
    llm_model: str = Field(
        default="claude-sonnet-4-20250514",
        description="Default LLM model to use for extraction"
    )
    
    # Rate Limiting
    rate_limit_rpm: int = Field(
        default=50,
        description="Maximum requests per minute"
    )
    
    # Paths
    data_dir: Path = Field(
        default=Path("data"),
        description="Directory containing RSP documents"
    )
    output_dir: Path = Field(
        default=Path("outputs"),
        description="Directory for generated outputs"
    )
    
    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )
    
    # Dashboard
    dashboard_port: int = Field(
        default=8501,
        description="Streamlit dashboard port"
    )
    dashboard_host: str = Field(
        default="localhost",
        description="Streamlit dashboard host"
    )
    
    @property
    def project_root(self) -> Path:
        """Get the project root directory."""
        return Path(__file__).parent.parent
    
    @property
    def raw_data_dir(self) -> Path:
        """Directory for raw RSP documents."""
        return self.project_root / self.data_dir / "raw"
    
    @property
    def processed_data_dir(self) -> Path:
        """Directory for processed/extracted data."""
        return self.project_root / self.data_dir / "processed"
    
    @property
    def schemas_dir(self) -> Path:
        """Directory for JSON schemas."""
        return self.project_root / self.data_dir / "schemas"
    
    @property
    def reports_dir(self) -> Path:
        """Directory for generated reports."""
        return self.project_root / self.output_dir / "reports"
    
    @property
    def harmonized_dir(self) -> Path:
        """Directory for harmonization outputs."""
        return self.project_root / self.output_dir / "harmonized_language"
    
    @property
    def visualizations_dir(self) -> Path:
        """Directory for visualization exports."""
        return self.project_root / self.output_dir / "visualizations"
    
    def ensure_directories(self) -> None:
        """Create all required directories if they don't exist."""
        directories = [
            self.raw_data_dir,
            self.processed_data_dir,
            self.schemas_dir,
            self.reports_dir,
            self.harmonized_dir,
            self.visualizations_dir,
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def has_api_key(self) -> bool:
        """Check if an API key is configured."""
        return bool(self.anthropic_api_key and self.anthropic_api_key != "your_api_key_here")


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Convenience access
settings = get_settings()
