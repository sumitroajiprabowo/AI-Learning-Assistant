"""
Configuration file for the AI Learning Assistant
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class"""
    
    # API Keys
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    
    # AI Model Configuration
    DEFAULT_MODEL = 'gemini-3.1-flash-lite'
    GEMINI_MODEL = 'gemini-3.1-flash-lite'
    MAX_TOKENS = 1000
    TEMPERATURE = 0.7
    
    # Document Processing
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx'}
    
    # Vector Database
    VECTOR_DB_PATH = 'vector_db'
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    # Study Plan Configuration
    DEFAULT_STUDY_DURATION = 30  # days
    DEFAULT_DAILY_HOURS = 2
    
    # Quiz Configuration
    DEFAULT_QUIZ_LENGTH = 10
    DIFFICULTY_LEVELS = ['easy', 'medium', 'hard']
    
    @classmethod
    def validate_api_keys(cls):
        """Validate that required API keys are present"""
        missing_keys = []
        
        if not cls.GEMINI_API_KEY:
            missing_keys.append('GEMINI_API_KEY')
            
        return missing_keys

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}