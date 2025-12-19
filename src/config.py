"""
Configuration settings for AI Notes-to-PPT Generator
✅ UPDATED with correct Gemini model and stylish color schemes
"""

import os
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables
load_dotenv()

class Config:
    """Application configuration class"""
    
    # API Configuration - Gemini Only
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
    # ✅ FIXED: Updated to use gemini-1.5-flash (gemini-pro is deprecated)
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    GEMINI_TEMPERATURE = float(os.getenv("GEMINI_TEMPERATURE", "0.7"))
    GEMINI_MAX_TOKENS = int(os.getenv("GEMINI_MAX_TOKENS", "2048"))
    
    # Validate API key on import
    if not GEMINI_API_KEY or len(GEMINI_API_KEY) < 20:
        print("=" * 60)
        print("WARNING: GEMINI_API_KEY is not configured!")
        print("=" * 60)
        print("Please set GEMINI_API_KEY in your .env file:")
        print("1. Create a .env file in the project root")
        print("2. Add: GEMINI_API_KEY=your_api_key_here")
        print("3. Get your API key from: https://makersuite.google.com/app/apikey")
        print("=" * 60)
    
    # Default AI Model (Gemini)
    DEFAULT_AI_MODEL = "gemini"
    
    # Application Configuration
    APP_NAME = os.getenv("APP_NAME", "SlideX - AI Presentation Generator")
    APP_VERSION = os.getenv("APP_VERSION", "2.0.0")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    # File Upload Configuration
    MAX_FILE_SIZE = os.getenv("MAX_FILE_SIZE", "50MB")
    ALLOWED_EXTENSIONS = os.getenv("ALLOWED_EXTENSIONS", "pdf,txt,docx,png,jpg,jpeg,wav,mp3,m4a").split(",")
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
    DATABASE_NAME = os.getenv("DATABASE_NAME", "slidex_db")
    COLLECTIONS = {
        "presentations": "presentations",
        "users": "users",
        "processing_logs": "processing_logs"
    }
    
    @classmethod
    def validate_api_keys(cls) -> Dict[str, bool]:
        """Validate that required API keys are configured"""
        is_valid = bool(cls.GEMINI_API_KEY and 
                       cls.GEMINI_API_KEY.strip() != "" and 
                       cls.GEMINI_API_KEY != "your_gemini_api_key_here" and
                       len(cls.GEMINI_API_KEY) > 20)
        
        if not is_valid:
            print("WARNING: GEMINI_API_KEY is not properly configured!")
            print(f"Current value: {cls.GEMINI_API_KEY[:10] + '...' if cls.GEMINI_API_KEY else 'None'}")
            print("Please set GEMINI_API_KEY in your .env file")
        
        return {
            "gemini": is_valid
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
            return cls.get_model_config("gemini")

# ✅ UPDATED: Stylish Template Configurations with more themes
PRESENTATION_TEMPLATES = {
    "professional": {
        "theme_color": "#1E3A8A",  # Deep Blue
        "accent_color": "#3B82F6",  # Bright Blue
        "background_color": "#FFFFFF",
        "title_font": "Segoe UI",
        "body_font": "Segoe UI",
        "title_size": 44,
        "body_size": 20,
        "title_color": "#1E3A8A",
        "body_color": "#374151",
        "layout": "title_and_content",
        "style": "corporate",
        "description": "Corporate & Business presentations"
    },
    "modern": {
        "theme_color": "#7C3AED",  # Purple
        "accent_color": "#EC4899",  # Pink
        "background_color": "#FFFFFF",
        "title_font": "Segoe UI",
        "body_font": "Segoe UI",
        "title_size": 42,
        "body_size": 18,
        "title_color": "#7C3AED",
        "body_color": "#1F2937",
        "layout": "title_and_content",
        "style": "contemporary",
        "description": "Creative & Tech presentations"
    },
    "academic": {
        "theme_color": "#065F46",  # Dark Green
        "accent_color": "#10B981",  # Emerald
        "background_color": "#FFFFFF",
        "title_font": "Calibri",
        "body_font": "Calibri",
        "title_size": 40,
        "body_size": 20,
        "title_color": "#065F46",
        "body_color": "#374151",
        "layout": "title_and_content",
        "style": "formal",
        "description": "Research & Education"
    },
    "creative": {
        "theme_color": "#DC2626",  # Red
        "accent_color": "#F59E0B",  # Amber
        "background_color": "#FFFFFF",
        "title_font": "Segoe UI",
        "body_font": "Segoe UI",
        "title_size": 44,
        "body_size": 18,
        "title_color": "#DC2626",
        "body_color": "#1F2937",
        "layout": "title_and_content",
        "style": "creative",
        "description": "Marketing & Events"
    },
    "minimal": {
        "theme_color": "#000000",  # Black
        "accent_color": "#6B7280",  # Gray
        "background_color": "#FFFFFF",
        "title_font": "Segoe UI",
        "body_font": "Segoe UI",
        "title_size": 40,
        "body_size": 18,
        "title_color": "#000000",
        "body_color": "#374151",
        "layout": "title_and_content",
        "style": "minimal",
        "description": "Clean & Simple"
    },
    "ocean": {
        "theme_color": "#0E7490",  # Teal
        "accent_color": "#06B6D4",  # Cyan
        "background_color": "#FFFFFF",
        "title_font": "Segoe UI",
        "body_font": "Segoe UI",
        "title_size": 42,
        "body_size": 18,
        "title_color": "#0E7490",
        "body_color": "#1F2937",
        "layout": "title_and_content",
        "style": "calm",
        "description": "Ocean & Nature themes"
    },
    "sunset": {
        "theme_color": "#EA580C",  # Orange
        "accent_color": "#F97316",  # Bright Orange
        "background_color": "#FFFFFF",
        "title_font": "Segoe UI",
        "body_font": "Segoe UI",
        "title_size": 42,
        "body_size": 18,
        "title_color": "#EA580C",
        "body_color": "#1F2937",
        "layout": "title_and_content",
        "style": "warm",
        "description": "Warm & Energetic"
    },
    "forest": {
        "theme_color": "#15803D",  # Forest Green
        "accent_color": "#22C55E",  # Lime
        "background_color": "#FFFFFF",
        "title_font": "Segoe UI",
        "body_font": "Segoe UI",
        "title_size": 42,
        "body_size": 18,
        "title_color": "#15803D",
        "body_color": "#1F2937",
        "layout": "title_and_content",
        "style": "natural",
        "description": "Nature & Environment"
    }
}

# Processing prompts
SYSTEM_PROMPTS = {
    "summarization": """You are an expert content analyst tasked with summarizing educational or professional content. 
    Your goal is to extract the most important information while maintaining clarity and coherence.""",
    
    "structuring": """You are a presentation design expert. Your task is to organize content into a logical slide structure 
    that flows well and maintains audience engagement.""",
    
    "content_generation": """You are a skilled content creator specializing in educational presentations. 
    Create clear, concise bullet points that effectively communicate key concepts. NEVER repeat content across slides.""",
    
    "presenter_notes": """You are an experienced presenter. Create detailed speaker notes that provide context, 
    examples, and additional information to help the presenter deliver the content effectively.""",
    
    "explanation": """You are an expert educator and explainer. Your task is to provide clear, comprehensive explanations 
    of complex concepts with examples, analogies, and additional learning resources. Make difficult topics accessible 
    and engaging for learners at various levels."""
}