import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Базовый класс конфигурации."""
    
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
    JSON_AS_ASCII = False  # Для поддержки кириллицы
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max request size

class DevelopmentConfig(Config):
    """Конфигурация для разработки."""
    
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DEV_DATABASE_URL',
        'sqlite:///dev.db'
    )

class TestingConfig(Config):
    """Конфигурация для тестирования."""
    
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'TEST_DATABASE_URL',
        'sqlite:///test.db'
    )
    # Отключаем CSRF для тестов
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """Конфигурация для продакшена."""
    
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://user:pass@localhost:5432/db'
    )

# Словарь для выбора конфигурации
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}