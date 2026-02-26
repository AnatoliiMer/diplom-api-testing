import allure
from typing import Any, List, Optional
from .helpers import validate_json_schema, compare_json_objects

class APIAssertions:
    """Класс с кастомными assertions для API тестирования."""
    
    @staticmethod
    def assert_status_code(response, expected_code: int):
        """Проверка статус кода."""
        with allure.step(f"Проверка статус кода: ожидаем {expected_code}"):
            assert response.status_code == expected_code, \
                f"Expected status {expected_code}, got {response.status_code}"
    
    @staticmethod
    def assert_json_schema(response, schema: dict):
        """Проверка JSON схемы."""
        with allure.step("Проверка JSON схемы"):
            validate_json_schema(response.json(), schema)
    
    @staticmethod
    def assert_field_equal(response, field: str, expected_value: Any):
        """Проверка значения поля."""
        with allure.step(f"Проверка поля '{field}': ожидаем {expected_value}"):
            data = response.json()
            assert data.get(field) == expected_value, \
                f"Field '{field}': expected {expected_value}, got {data.get(field)}"
    
    @staticmethod
    def assert_fields_present(response, fields: List[str]):
        """Проверка наличия полей."""
        with allure.step(f"Проверка наличия полей: {fields}"):
            data = response.json()
            missing_fields = [f for f in fields if f not in data]
            assert not missing_fields, \
                f"Missing fields: {missing_fields}"
    
    @staticmethod
    def assert_response_time(response, max_time_ms: int):
        """Проверка времени ответа."""
        with allure.step(f"Проверка времени ответа: < {max_time_ms}ms"):
            response_time = response.elapsed.total_seconds() * 1000
            assert response_time < max_time_ms, \
                f"Response time {response_time:.2f}ms exceeds {max_time_ms}ms"
    
    @staticmethod
    def assert_json_contains(expected: dict, actual: dict, exclude: List[str] = None):
        """Проверка, что JSON содержит ожидаемые поля."""
        with allure.step("Проверка содержимого JSON"):
            diff = compare_json_objects(expected, actual, exclude)
            assert not diff, f"JSON mismatch: {diff}"