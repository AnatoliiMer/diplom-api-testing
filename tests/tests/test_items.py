import allure
import pytest
from data.test_data import create_item_test_data, update_item_test_data
from utils.assertions import APIAssertions as Assert
from config import config

@allure.epic("REST API Тестирование")
@allure.feature("Управление товарами")
class TestItemsAPI:
    
    @allure.story("Получение товаров")
    @allure.title("Тест получения списка всех товаров")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("smoke", "positive")
    def test_get_all_items(self, api_client):
        """Тест получения списка всех товаров."""
        
        response = api_client.get_all_items()
        
        Assert.assert_status_code(response, 200)
        Assert.assert_json_schema(response, config.response_schemas["items_list"])
        
        data = response.json()
        assert isinstance(data['items'], list)
        assert data['total'] >= 0
        assert data['page'] >= 1
        assert data['per_page'] >= 1
        
        allure.attach(
            f"Total items: {data['total']}",
            name="Statistics",
            attachment_type=allure.attachment_type.TEXT
        )
    
    @allure.story("Создание товаров")
    @allure.title("Параметризованный тест создания товара")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.parametrize(
        "item_data,expected_status,test_id,marks",
        create_item_test_data,
        ids=[item[2] for item in create_item_test_data]
    )
    def test_create_item_parametrized(
        self,
        api_client,
        item_data,
        expected_status,
        test_id,
        marks
    ):
        """Параметризованный тест создания товаров."""
        
        with allure.step(f"Создание товара с данными: {item_data}"):
            # Проверяем наличие ключа 'name' в данных
            if 'name' in item_data:
                response = api_client.create_item(
                    name=item_data['name'],
                    price=item_data['price'],
                    description=item_data.get('description'),
                    in_stock=item_data.get('in_stock', True),
                    expected_status=expected_status
                )
            else:
                # Для теста missing_name отправляем запрос без name
                response = api_client.post(
                    "/items",
                    json=item_data,
                    expected_status=expected_status
                )
        
        if expected_status == 201:
            created_item = response.json()
            
            with allure.step("Проверка созданного товара"):
                Assert.assert_json_schema(response, config.response_schemas["item"])
                assert created_item['name'] == item_data['name']
                assert created_item['price'] == item_data['price']
                
                if 'description' in item_data:
                    assert created_item.get('description') == item_data['description']
                
                if 'in_stock' in item_data:
                    assert created_item['in_stock'] == item_data['in_stock']
    
    @allure.story("Создание товаров")
    @allure.title("Тест создания товара со случайными данными")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("positive", "faker")
    def test_create_random_item(self, api_client, random_item_data):
        """Тест создания товара со случайными данными."""
        
        response = api_client.create_item(
            name=random_item_data['name'],
            price=random_item_data['price'],
            description=random_item_data.get('description'),
            in_stock=random_item_data.get('in_stock', True)
        )
        
        Assert.assert_status_code(response, 201)
        Assert.assert_json_schema(response, config.response_schemas["item"])
        
        created_item = response.json()
        assert created_item['name'] == random_item_data['name']
        assert created_item['price'] == random_item_data['price']
    
    @allure.story("Получение товаров")
    @allure.title("Тест получения товара по ID")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("smoke", "positive")
    def test_get_item_by_id(self, api_client, created_item):
        """Тест получения товара по ID."""
        
        response = api_client.get_item(created_item['id'])
        
        Assert.assert_status_code(response, 200)
        Assert.assert_json_schema(response, config.response_schemas["item"])
        
        item = response.json()
        assert item['id'] == created_item['id']
        assert item['name'] == created_item['name']
        assert item['price'] == created_item['price']
    
    @allure.story("Получение товаров")
    @allure.title("Тест получения несуществующего товара")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("negative", "not_found")
    def test_get_nonexistent_item(self, api_client):
        """Тест получения несуществующего товара."""
        
        response = api_client.get_item(999999, expected_status=404)
        Assert.assert_status_code(response, 404)
        
        data = response.json()
        assert 'error' in data
    
    @allure.story("Обновление товаров")
    @allure.title("Тест полного обновления товара")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("positive", "update")
    def test_update_item(self, api_client, created_item):
        """Тест полного обновления товара (PUT)."""
        
        new_data = {
            'name': 'Обновленный товар',
            'price': 199.99,
            'description': 'Новое описание',
            'in_stock': False
        }
        
        response = api_client.update_item(
            created_item['id'],
            name=new_data['name'],
            price=new_data['price'],
            description=new_data['description'],
            in_stock=new_data['in_stock']
        )
        
        Assert.assert_status_code(response, 200)
        
        updated_item = response.json()
        assert updated_item['name'] == new_data['name']
        assert updated_item['price'] == new_data['price']
        assert updated_item['description'] == new_data['description']
        assert updated_item['in_stock'] == new_data['in_stock']
    
    @allure.story("Обновление товаров")
    @allure.title("Параметризованный тест частичного обновления товара")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize(
        "patch_data,expected_status,test_id,marks",
        update_item_test_data,
        ids=[item[2] for item in update_item_test_data]
    )
    def test_patch_item(
        self,
        api_client,
        created_item,
        patch_data,
        expected_status,
        test_id,
        marks
    ):
        """Параметризованный тест частичного обновления товара."""
        
        response = api_client.patch_item(
            created_item['id'],
            **patch_data,
            expected_status=expected_status
        )
        
        if expected_status == 200:
            updated_item = response.json()
            
            # Проверка обновленных полей
            for field, value in patch_data.items():
                assert updated_item[field] == value, \
                    f"Field {field} was not updated correctly"
            
            # Проверка, что остальные поля не изменились
            assert updated_item['id'] == created_item['id']
    
    @allure.story("Удаление товаров")
    @allure.title("Тест удаления товара")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("smoke", "delete")
    def test_delete_item(self, api_client, created_item):
        """Тест удаления товара."""
        
        response = api_client.delete_item(created_item['id'])
        Assert.assert_status_code(response, 200)
        
        # Проверка, что товар действительно удален
        get_response = api_client.get_item(created_item['id'], expected_status=404)
        Assert.assert_status_code(get_response, 404)
    
    @allure.story("Фильтрация")
    @allure.title("Тест фильтрации товаров по цене")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("positive", "filter")
    def test_filter_items_by_price(self, api_client):
        """Тест фильтрации товаров по диапазону цен."""
        
        # Создаем товары с разными ценами
        items_prices = [10, 50, 100, 200]
        created_ids = []
        
        try:
            for price in items_prices:
                response = api_client.create_item(
                    name=f"Price Test Item {price}",
                    price=price
                )
                assert response.status_code == 201
                created_ids.append(response.json()['id'])
            
            # Тест фильтрации по минимальной цене
            response = api_client.get_all_items(min_price=50)
            data = response.json()
            
            for item in data['items']:
                assert item['price'] >= 50
            
            # Тест фильтрации по максимальной цене
            response = api_client.get_all_items(max_price=100)
            data = response.json()
            
            for item in data['items']:
                assert item['price'] <= 100
            
            # Тест фильтрации по диапазону
            response = api_client.get_all_items(min_price=50, max_price=150)
            data = response.json()
            
            for item in data['items']:
                assert 50 <= item['price'] <= 150
        
        finally:
            # Очистка
            for item_id in created_ids:
                api_client.delete_item(item_id, expected_status=200)
    
    @allure.story("Производительность")
    @allure.title("Тест времени ответа API")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("performance")
    def test_api_response_time(self, api_client):
        """Тест времени ответа API."""
        
        response = api_client.get_all_items()
        Assert.assert_response_time(response, 500)  # < 500ms
    
    @allure.story("Пагинация")
    @allure.title("Тест пагинации списка товаров")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("positive", "pagination")
    def test_items_pagination(self, api_client):
        """Тест пагинации списка товаров."""
        
        # Создаем несколько товаров для теста пагинации
        created_ids = []
        try:
            for i in range(15):
                response = api_client.create_item(
                    name=f"Pagination Item {i}",
                    price=100 + i
                )
                assert response.status_code == 201
                created_ids.append(response.json()['id'])
            
            # Первая страница
            response = api_client.get_all_items(page=1, per_page=5)
            data = response.json()
            
            assert data['page'] == 1
            assert data['per_page'] == 5
            assert len(data['items']) <= 5
            assert data['total'] >= 15
            
            # Вторая страница
            response2 = api_client.get_all_items(page=2, per_page=5)
            data2 = response2.json()
            
            assert data2['page'] == 2
            assert len(data2['items']) <= 5
            
            # Проверяем, что товары на разных страницах разные
            if len(data['items']) > 0 and len(data2['items']) > 0:
                assert data['items'][0]['id'] != data2['items'][0]['id']
        
        finally:
            # Очистка
            for item_id in created_ids:
                api_client.delete_item(item_id, expected_status=200)
    
    @allure.story("Комплексные тесты")
    @allure.title("Тест полного жизненного цикла товара")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("smoke", "e2e")
    def test_complete_item_lifecycle(self, api_client, random_item_data):
        """Тест полного жизненного цикла товара."""
        
        # 1. Создание
        with allure.step("1. Создание товара"):
            create_response = api_client.create_item(
                name=random_item_data['name'],
                price=random_item_data['price']
            )
            Assert.assert_status_code(create_response, 201)
            item = create_response.json()
            item_id = item['id']
        
        # 2. Проверка создания
        with allure.step("2. Проверка создания"):
            get_response = api_client.get_item(item_id)
            Assert.assert_status_code(get_response, 200)
            assert get_response.json()['name'] == random_item_data['name']
        
        # 3. Обновление
        with allure.step("3. Обновление товара"):
            new_name = f"Updated {random_item_data['name']}"
            update_response = api_client.patch_item(
                item_id,
                name=new_name,
                price=199.99
            )
            Assert.assert_status_code(update_response, 200)
            assert update_response.json()['name'] == new_name
        
        # 4. Удаление
        with allure.step("4. Удаление товара"):
            delete_response = api_client.delete_item(item_id)
            Assert.assert_status_code(delete_response, 200)
        
        # 5. Проверка удаления
        with allure.step("5. Проверка удаления"):
            get_deleted_response = api_client.get_item(item_id, expected_status=404)
            Assert.assert_status_code(get_deleted_response, 404)