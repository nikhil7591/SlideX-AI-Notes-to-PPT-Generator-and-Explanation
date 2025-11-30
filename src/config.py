"""
Configuration settings for AI Notes-to-PPT Generator
"""

import os
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables
load_dotenv()

class Config:
    """Application configuration class"""
    
    # API Configuration - Gemini Only
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = "gemini-2.0-flash"  # Updated to use available model
    GEMINI_TEMPERATURE = 0.3  # Lower temperature for crisp, focused output
    GEMINI_MAX_TOKENS = 2048
    
    # Default AI Model (Gemini)
    DEFAULT_AI_MODEL = "gemini"
    
    # Application Configuration
    APP_NAME = os.getenv("APP_NAME", "AI Notes-to-PPT Generator")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    # File Upload Configuration
    MAX_FILE_SIZE = os.getenv("MAX_FILE_SIZE", "50MB")
    ALLOWED_EXTENSIONS = os.getenv("ALLOWED_EXTENSIONS", "pdf,txt,docx").split(",")
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
    
    # Presentation Generation Configuration
    DEFAULT_TEMPLATE = os.getenv("DEFAULT_TEMPLATE", "professional")
    MAX_SLIDES = int(os.getenv("MAX_SLIDES", "50"))
    MIN_FONT_SIZE = int(os.getenv("MIN_FONT_SIZE", "12"))
    MAX_FONT_SIZE = int(os.getenv("MAX_FONT_SIZE", "44"))
    
    # Processing Configuration
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "4000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
    SUMMARY_RATIO = float(os.getenv("SUMMARY_RATIO", "0.3"))
    
    # Security Configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key_here_for_sessions")
    SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT", "3600"))
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")
    
    # Database Configuration - MongoDB
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "ai_notes_to_ppt")
    COLLECTIONS = {
        "presentations": "presentations",
        "users": "users",
        "processing_logs": "processing_logs"
    }
    
    @classmethod
    def validate_api_keys(cls) -> Dict[str, bool]:
        """Validate that required API keys are configured"""
        return {
            "gemini": bool(cls.GEMINI_API_KEY and cls.GEMINI_API_KEY != "your_gemini_api_key_here")
        }
    
    @classmethod
    def get_model_config(cls, model_name: str) -> Dict[str, Any]:
        """Get configuration for a specific model"""
        if model_name.lower() in ["gemini", "google", "default"]:
            return {
                "api_key": cls.GEMINI_API_KEY,
                "model": cls.GEMINI_MODEL,
                "temperature": cls.GEMINI_TEMPERATURE
            }
        else:
            # Default to Gemini for any unknown model
            return cls.get_model_config("gemini")

# Template configurations
PRESENTATION_TEMPLATES = {
    "professional": {
        "theme_color": "#2C3E50",
        "title_font": "Arial",
        "body_font": "Calibri",
        "title_size": 44,
        "body_size": 24,
        "layout": "title_and_content"
    },
    "modern": {
        "theme_color": "#3498DB",
        "title_font": "Helvetica",
        "body_font": "Arial",
        "title_size": 40,
        "body_size": 22,
        "layout": "title_and_content"
    },
    "academic": {
        "theme_color": "#34495E",
        "title_font": "Times New Roman",
        "body_font": "Times New Roman",
        "title_size": 42,
        "body_size": 26,
        "layout": "title_and_content"
    },
    "creative": {
        "theme_color": "#E74C3C",
        "title_font": "Verdana",
        "body_font": "Arial",
        "title_size": 38,
        "body_size": 20,
        "layout": "title_and_content"
    }
}

# Processing prompts
SYSTEM_PROMPTS = {
    "summarization": """You are an expert content analyst tasked with summarizing educational or professional content. 
    Extract only the most important KEY CONCEPTS and FACTS. Be crisp and concise.""",
    
    "structuring": """You are a presentation design expert. Organize content into focused slide topics 
    with SHORT, CRISP titles (5-8 words max). No examples, no questions.""",
    
    "content_generation": """You are a skilled content creator. Create SHORT, POINT-TO-POINT bullet points 
    that are 1-2 lines each. Focus on KEY FACTS only. NO examples, NO definitions, NO questions.""",
    
    "presenter_notes": """You are an experienced presenter. Create SHORT speaker notes (1-2 sentences max) 
    that provide key talking points only.""",
    
    "explanation": """You are an expert educator. Provide clear, focused explanations of key concepts 
    in SHORT, CRISP language. Focus on main ideas, not examples or extended explanations."""
}
