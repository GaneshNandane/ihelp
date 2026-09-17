from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


class Settings(BaseSettings):
    app_name: str = "iHelp Backend"
    api_prefix: str = "/api"
    cors_origins: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://localhost:5174",
            "http://localhost:5175",
            "http://localhost:5176",
            "http://localhost:5177",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:5174",
            "http://127.0.0.1:5175",
            "http://127.0.0.1:5176",
            "http://127.0.0.1:5177",
        ]
    )

    firecrawl_api_key: Optional[str] = None
    firecrawl_base_url: str = "https://api.firecrawl.dev"
    firecrawl_timeout_seconds: int = 30
    default_job_query: str = "software engineer developer jobs India hiring TCS Infosys Cognizant Wipro"
    default_job_location: str = "India"
    default_job_country: str = "IN"
    default_job_limit: int = 6
    
    # Google Sheet Sync URL & Webhook
    google_sheet_url: str = (
        "https://docs.google.com/spreadsheets/d/e/2PACX-1vQKgD-ari2EKlNf2ZS1dQUq2x9lS9F_gAwtdri-yG5qPkJij85T3TzeTdkxMZuooV-klF8XlCj9R-pz/pubhtml?gid=0&single=true"
    )
    google_sheet_webhook_url: Optional[str] = None

    # SMTP Mail Server Configuration (Optional - for direct email sending)
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_pass: Optional[str] = None
    sender_email: Optional[str] = None
    
    reputed_companies: List[str] = Field(
        default_factory=lambda: [
            "TCS",
            "Cognizant",
            "Infosys",
            "Wipro",
            "HCLTech",
            "Tech Mahindra",
            "LTIMindtree",
            "Accenture India",
            "Capgemini India",
            "Zoho",
            "Jio Platforms",
            "Swiggy",
            "Zomato",
            "Microsoft India",
            "Google India",
            "Amazon India",
        ]
    )

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
