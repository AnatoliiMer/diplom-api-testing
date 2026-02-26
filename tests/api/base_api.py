import requests
import allure
import json
import logging
from typing import Optional, Dict, Any
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config import config

logger = logging.getLogger(__name__)

class BaseAPI:
    """Базовый класс для всех API клиентов."""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or config.api.base_url
        self.session = self._create_session()
        self.timeout = config.api.timeout
        
    def _create_session(self) -> requests.Session:
        """Создание сессии с retry механизмом."""
        session = requests.Session()
        
        # Настройка retry стратегии
        retry_strategy = Retry(
            total=config.api.max_retries,
            backoff_factor=config.api.retry_backoff,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Установка заголовков по умолчанию
        session.headers.update(config.default_headers)
        
        return session
    
    def _log_request(self, method: str, url: str, **kwargs):
        """Логирование запроса."""
        logger.info(f"🌐 {method} {url}")
        
        with allure.step(f"📤 Request: {method} {url}"):
            # Логирование headers
            headers = kwargs.get('headers', {})
            if headers:
                allure.attach(
                    json.dumps(dict(headers), indent=2),
                    name="Request Headers",
                    attachment_type=allure.attachment_type.JSON
                )
            
            # Логирование body
            if kwargs.get('json'):
                allure.attach(
                    json.dumps(kwargs.get('json'), indent=2, ensure_ascii=False),
                    name="Request Body",
                    attachment_type=allure.attachment_type.JSON
                )
    
    def _log_response(self, response: requests.Response):
        """Логирование ответа."""
        logger.info(f"📥 Response: {response.status_code} ({response.elapsed.total_seconds():.3f}s)")
        
        with allure.step(f"📥 Response: {response.status_code}"):
            # Логирование body
            try:
                response_json = response.json()
                allure.attach(
                    json.dumps(response_json, indent=2, ensure_ascii=False),
                    name="Response Body",
                    attachment_type=allure.attachment_type.JSON
                )
            except:
                allure.attach(
                    response.text,
                    name="Response Body",
                    attachment_type=allure.attachment_type.TEXT
                )
            
            # Логирование времени выполнения
            allure.attach(
                f"Time: {response.elapsed.total_seconds():.3f}s",
                name="Performance",
                attachment_type=allure.attachment_type.TEXT
            )
    
    def _request(
        self,
        method: str,
        endpoint: str,
        expected_status: int = None,
        **kwargs
    ) -> requests.Response:
        """Базовый метод для выполнения запросов."""
        url = f"{self.base_url}{endpoint}"
        
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        
        self._log_request(method, url, **kwargs)
        
        try:
            response = self.session.request(method, url, **kwargs)
            self._log_response(response)
            
            if expected_status:
                assert response.status_code == expected_status, \
                    f"Expected status {expected_status}, got {response.status_code}"
            
            return response
            
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout: {method} {url}")
            raise
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error: {method} {url}")
            raise
    
    def get(self, endpoint: str, **kwargs) -> requests.Response:
        return self._request("GET", endpoint, **kwargs)
    
    def post(self, endpoint: str, **kwargs) -> requests.Response:
        return self._request("POST", endpoint, **kwargs)
    
    def put(self, endpoint: str, **kwargs) -> requests.Response:
        return self._request("PUT", endpoint, **kwargs)
    
    def patch(self, endpoint: str, **kwargs) -> requests.Response:
        return self._request("PATCH", endpoint, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        return self._request("DELETE", endpoint, **kwargs)
    
    def close(self):
        self.session.close()