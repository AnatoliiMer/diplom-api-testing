import pytest
import allure
import logging
import json
from datetime import datetime
from typing import Dict, Any, Generator
from api.items_api import ItemsAPI
from data.test_data import generate_random_item
from config import config

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, config.test.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@pytest.fixture(scope="session")
def api_client() -> Generator[ItemsAPI, None, None]:
    """Фикстура, предоставляющая клиент API для всех тестов."""
    logger.info("🚀 Инициализация API клиента")
    
    with allure.step("🛠️ Инициализация API клиента"):
        client = ItemsAPI()
        allure.attach(
            client.base_url,
            name="API Base URL",
            attachment_type=allure.attachment_type.TEXT
        )
        
    yield client
    
    logger.info("🧹 Закрытие API клиента")
    client.close()

@pytest.fixture
def random_item_data() -> Dict[str, Any]:
    """Фикстура с случайными данными товара."""
    return generate_random_item()

@pytest.fixture(params=[
    {"name": "Стандартный товар", "price": 100.0, "in_stock": True},
    {"name": "Дорогой товар", "price": 9999.99, "in_stock": True},
    {"name": "Дешевый товар", "price": 0.99, "in_stock": True},
    {"name": "Товар не в наличии", "price": 500.0, "in_stock": False}
], ids=["standard", "expensive", "cheap", "out_of_stock"])
def parametrized_item_data(request) -> Dict[str, Any]:
    """Параметризованная фикстура с разными типами товаров."""
    return request.param

@pytest.fixture
def created_item(api_client, request) -> Generator[Dict[str, Any], None, None]:
    """
    Фикстура для создания товара и его автоматического удаления.
    """
    # Получение данных для создания
    if hasattr(request, 'param') and request.param:
        item_data = request.param
    else:
        item_data = generate_random_item()
    
    with allure.step(f"📦 Setup: Создание тестового товара"):
        logger.info(f"Creating test item: {item_data['name']}")
        
        response = api_client.create_item(
            name=item_data['name'],
            price=item_data['price'],
            description=item_data.get('description'),
            in_stock=item_data.get('in_stock', True)
        )
        
        assert response.status_code == 201, f"Failed to create item: {response.text}"
        item = response.json()
        
        allure.attach(
            json.dumps(item, indent=2, ensure_ascii=False),
            name="Created Item",
            attachment_type=allure.attachment_type.JSON
        )
        
        logger.info(f"✅ Item created with ID: {item['id']}")
    
    yield item
    
    with allure.step("🧹 Teardown: Удаление тестового товара"):
        logger.info(f"Deleting test item ID: {item['id']}")
        try:
            # Не ожидаем конкретный статус, принимаем 200 или 404
            delete_response = api_client.delete_item(item['id'], expected_status=None)
            if delete_response.status_code not in [200, 404]:
                logger.warning(f"Unexpected delete status: {delete_response.status_code}")
            else:
                logger.info(f"Cleanup successful: {delete_response.status_code}")
        except Exception as e:
            logger.warning(f"Cleanup failed: {e}")
        finally:
            allure.attach(
                f"Cleanup attempted with status: {delete_response.status_code if 'delete_response' in locals() else 'unknown'}",
                name="Cleanup result",
                attachment_type=allure.attachment_type.TEXT
            )

@pytest.fixture(autouse=True)
def setup_test_logging(request):
    """Автоматическая фикстура для логирования начала и конца теста."""
    test_name = request.node.name
    logger.info(f"▶️ Запуск теста: {test_name}")
    
    start_time = datetime.now()
    
    yield
    
    duration = (datetime.now() - start_time).total_seconds()
    logger.info(f"⏹️ Тест завершен: {test_name} (длительность: {duration:.2f}s)")

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Хук для обработки результатов теста."""
    outcome = yield
    rep = outcome.get_result()
    
    if rep.when == "call":
        setattr(item, "rep_call", rep)
        
        # Добавление информации в Allure при падении теста
        if rep.failed:
            with allure.step("❌ Тест упал"):
                allure.attach(
                    str(call.excinfo),
                    name="Error Info",
                    attachment_type=allure.attachment_type.TEXT
                )