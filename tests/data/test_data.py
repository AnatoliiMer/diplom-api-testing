import pytest
from faker import Faker
from config import config

fake = Faker()
fake.seed_instance(config.test.faker_seed)

# Граничные значения для тестирования
BOUNDARY_VALUES = {
    'name_length': {
        'min': 1,
        'max': 100,
        'exceed': 101
    },
    'price': {
        'min': 0,
        'max': 999999.99
    }
}

# Тестовые данные для создания товаров
# Каждый элемент: (item_data, expected_status, test_id, marks)
create_item_test_data = [
    # Валидные данные
    (
        {'name': 'Ноутбук ASUS', 'price': 999.99, 'description': 'Игровой ноутбук', 'in_stock': True},
        201,
        'valid_complete_item',
        [pytest.mark.smoke, pytest.mark.positive]
    ),
    (
        {'name': 'Мышь Logitech', 'price': 25.50},
        201,
        'valid_minimal_item',
        [pytest.mark.positive]
    ),
    (
        {'name': 'Коврик для мыши', 'price': 0.0, 'in_stock': True},
        201,
        'zero_price_item',
        [pytest.mark.boundary]
    ),
    
    # Граничные значения
    (
        {'name': 'A' * BOUNDARY_VALUES['name_length']['max'], 'price': 100.0},
        201,
        'max_name_length',
        [pytest.mark.boundary]
    ),
    (
        {'name': 'Товар', 'price': BOUNDARY_VALUES['price']['max']},
        201,
        'max_price',
        [pytest.mark.boundary]
    ),
    
    # Негативные тесты
    (
        {'name': '', 'price': 100.0},
        400,
        'empty_name',
        [pytest.mark.negative, pytest.mark.validation]
    ),
    (
        {'name': 'A' * (BOUNDARY_VALUES['name_length']['exceed']), 'price': 100.0},
        400,
        'name_too_long',
        [pytest.mark.negative, pytest.mark.validation]
    ),
    (
        {'name': 'Товар', 'price': -10.0},
        400,
        'negative_price',
        [pytest.mark.negative, pytest.mark.validation]
    ),
    (
        {'name': None, 'price': 100.0},
        400,
        'null_name',
        [pytest.mark.negative, pytest.mark.validation]
    ),
    (
        {'price': 100.0},  # отсутствует поле name
        400,
        'missing_name',
        [pytest.mark.negative, pytest.mark.validation]
    )
]

# Тестовые данные для обновления
update_item_test_data = [
    ({'name': 'Обновленное название'}, 200, 'update_name_only', [pytest.mark.positive]),
    ({'price': 999.99}, 200, 'update_price_only', [pytest.mark.positive]),
    ({'in_stock': False}, 200, 'update_stock_only', [pytest.mark.positive]),
    ({'name': 'Новое название', 'price': 500.00}, 200, 'update_multiple_fields', [pytest.mark.positive]),
    ({'name': '', 'price': 100}, 400, 'invalid_update', [pytest.mark.negative])
]

def generate_random_item():
    """Генерация случайного товара."""
    return {
        'name': fake.catch_phrase()[:50],
        'price': round(fake.random_number(digits=4) / 100, 2),
        'description': fake.text(max_nb_chars=200),
        'in_stock': fake.boolean()
    }

# Массовые данные для нагрузочного тестирования
BULK_TEST_DATA = [generate_random_item() for _ in range(10)]