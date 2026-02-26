import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

# Загружаем .env файл из корня проекта
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

@dataclass
class APIConfig:
    """Конфигурация API."""
    base_url: str = os.getenv("API_BASE_URL", "http://127.0.0.1:5000/api")
    timeout: int = int(os.getenv("API_TIMEOUT", "30"))
    max_retries: int = int(os.getenv("API_MAX_RETRIES", "3"))
    retry_backoff: float = float(os.getenv("RETRY_BACKOFF", "1.0"))

@dataclass
class TestConfig:
    """Конфигурация тестов."""
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    parallel_workers: int = int(os.getenv("PARALLEL_WORKERS", "4"))
    faker_seed: int = int(os.getenv("FAKER_SEED", "42"))

class Config:
    """Главный класс конфигурации."""
    api = APIConfig()
    test = TestConfig()
    
    # Заголовки по умолчанию
    default_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "API-Test-Framework/2.0",
        "Connection": "close"
    }
    
    # Схемы ответов для валидации
    response_schemas = {
        "item": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "price": {"type": "number"},
                "description": {"type": ["string", "null"]},
                "in_stock": {"type": "boolean"},
                "created_at": {"type": "string", "format": "date-time"},
                "updated_at": {"type": ["string", "null"], "format": "date-time"}
            },
            "required": ["id", "name", "price", "in_stock"]
        },
        "items_list": {
            "definitions": {
                "item": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"},
                        "price": {"type": "number"},
                        "description": {"type": ["string", "null"]},
                        "in_stock": {"type": "boolean"},
                        "created_at": {"type": "string", "format": "date-time"},
                        "updated_at": {"type": ["string", "null"], "format": "date-time"}
                    },
                    "required": ["id", "name", "price", "in_stock"]
                }
            },
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/item"}
                },
                "total": {"type": "integer"},
                "page": {"type": "integer"},
                "per_page": {"type": "integer"},
                "pages": {"type": "integer"}
            },
            "required": ["items", "total", "page", "per_page", "pages"]
        }
    }

config = Config()