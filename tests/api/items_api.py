import allure
from typing import Optional, Dict, Any
from .base_api import BaseAPI

class ItemsAPI(BaseAPI):
    """Клиент для работы с эндпоинтами товаров."""
    
    def __init__(self, base_url: str = None):
        super().__init__(base_url)
        self.endpoint = "/items"
    
    @allure.step("📋 Получение списка всех товаров")
    def get_all_items(
        self,
        page: int = 1,
        per_page: int = 20,
        in_stock: Optional[bool] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        expected_status: int = 200
    ):
        """
        Получение списка товаров с фильтрацией.
        """
        params = {
            'page': page,
            'per_page': per_page
        }
        
        if in_stock is not None:
            params['in_stock'] = str(in_stock).lower()
        if min_price is not None:
            params['min_price'] = min_price
        if max_price is not None:
            params['max_price'] = max_price
        
        return self.get(
            self.endpoint,
            params=params,
            expected_status=expected_status
        )
    
    @allure.step("🔍 Получение товара по ID: {item_id}")
    def get_item(
        self,
        item_id: int,
        expected_status: int = 200
    ):
        return self.get(
            f"{self.endpoint}/{item_id}",
            expected_status=expected_status
        )
    
    @allure.step("➕ Создание нового товара")
    def create_item(
        self,
        name: str,
        price: float,
        description: Optional[str] = None,
        in_stock: bool = True,
        expected_status: int = 201
    ):
        data = {
            "name": name,
            "price": price,
            "in_stock": in_stock
        }
        
        if description is not None:
            data["description"] = description
        
        return self.post(
            self.endpoint,
            json=data,
            expected_status=expected_status
        )
    
    @allure.step("📝 Полное обновление товара ID: {item_id}")
    def update_item(
        self,
        item_id: int,
        name: str,
        price: float,
        description: Optional[str] = None,
        in_stock: bool = True,
        expected_status: int = 200
    ):
        data = {
            "name": name,
            "price": price,
            "in_stock": in_stock
        }
        
        if description is not None:
            data["description"] = description
        
        return self.put(
            f"{self.endpoint}/{item_id}",
            json=data,
            expected_status=expected_status
        )
    
    @allure.step("✏️ Частичное обновление товара ID: {item_id}")
    def patch_item(
        self,
        item_id: int,
        name: Optional[str] = None,
        price: Optional[float] = None,
        description: Optional[str] = None,
        in_stock: Optional[bool] = None,
        expected_status: int = 200
    ):
        data = {}
        if name is not None:
            data["name"] = name
        if price is not None:
            data["price"] = price
        if description is not None:
            data["description"] = description
        if in_stock is not None:
            data["in_stock"] = in_stock
        
        return self.patch(
            f"{self.endpoint}/{item_id}",
            json=data,
            expected_status=expected_status
        )
    
    @allure.step("🗑️ Удаление товара ID: {item_id}")
    def delete_item(
        self,
        item_id: int,
        expected_status: int = 200
    ):
        return self.delete(
            f"{self.endpoint}/{item_id}",
            expected_status=expected_status
        )