
from pydantic_settings import BaseSettings
from pydantic import field_validator 
from typing import List, Optional, Union
from dotenv import load_dotenv
import json
import os

load_dotenv()


class Settings(BaseSettings):
    """Application configuration with environment variable support"""
    ### OpenAI Settings
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")

settings = Settings()
