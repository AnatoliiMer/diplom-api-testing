from flask import request
from flask_restful import Resource
from marshmallow import ValidationError
from database.db import db
from models.item import Item
from schemas.item_schema import ItemSchema, ItemQuerySchema
import logging

logger = logging.getLogger(__name__)

class ItemListResource(Resource):
    """Ресурс для работы со списком товаров."""
    
    def get(self):
        """Получение списка товаров с фильтрацией и пагинацией."""
        try:
            # Валидация query параметров
            query_schema = ItemQuerySchema()
            params = query_schema.load(request.args)
            
            # Базовый запрос
            query = Item.query
            
            # Применение фильтров
            if params.get('in_stock') is not None:
                query = query.filter_by(in_stock=params['in_stock'])
            
            if params.get('min_price') is not None:
                query = query.filter(Item.price >= params['min_price'])
            
            if params.get('max_price') is not None:
                query = query.filter(Item.price <= params['max_price'])
            
            # Пагинация
            page = params['page']
            per_page = params['per_page']
            paginated = query.paginate(page=page, per_page=per_page, error_out=False)
            
            # Сериализация
            item_schema = ItemSchema(many=True)
            items = item_schema.dump(paginated.items)
            
            return {
                'items': items,
                'total': paginated.total,
                'page': page,
                'per_page': per_page,
                'pages': paginated.pages
            }, 200
            
        except ValidationError as e:
            logger.warning(f"Validation error: {e.messages}")
            return {'errors': e.messages}, 400
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return {'error': 'Internal server error'}, 500
    
    def post(self):
        """Создание нового товара."""
        try:
            # Валидация входных данных
            schema = ItemSchema()
            data = schema.load(request.get_json())
            
            # Создание товара
            item = Item(**data)
            db.session.add(item)
            db.session.commit()
            
            logger.info(f"Item created: {item.id}")
            
            # Возврат созданного товара
            return schema.dump(item), 201
            
        except ValidationError as e:
            logger.warning(f"Validation error: {e.messages}")
            return {'errors': e.messages}, 400
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating item: {str(e)}")
            return {'error': 'Internal server error'}, 500


class ItemResource(Resource):
    """Ресурс для работы с конкретным товаром."""
    
    def get(self, item_id):
        """Получение товара по ID."""
        try:
            item = Item.query.get(item_id)
            
            if not item:
                return {'error': 'Item not found'}, 404
            
            schema = ItemSchema()
            return schema.dump(item), 200
            
        except Exception as e:
            logger.error(f"Error getting item {item_id}: {str(e)}")
            return {'error': 'Internal server error'}, 500
    
    def put(self, item_id):
        """Полное обновление товара."""
        try:
            item = Item.query.get(item_id)
            
            if not item:
                return {'error': 'Item not found'}, 404
            
            # Валидация входных данных
            schema = ItemSchema()
            data = schema.load(request.get_json())
            
            # Обновление полей
            for key, value in data.items():
                setattr(item, key, value)
            
            db.session.commit()
            
            logger.info(f"Item updated: {item_id}")
            return schema.dump(item), 200
            
        except ValidationError as e:
            return {'errors': e.messages}, 400
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating item {item_id}: {str(e)}")
            return {'error': 'Internal server error'}, 500
    
    def patch(self, item_id):
        """Частичное обновление товара."""
        try:
            item = Item.query.get(item_id)
            
            if not item:
                return {'error': 'Item not found'}, 404
            
            # Частичная валидация
            data = request.get_json()
            schema = ItemSchema(partial=True)
            validated_data = schema.load(data)
            
            # Обновление только переданных полей
            for key, value in validated_data.items():
                setattr(item, key, value)
            
            db.session.commit()
            
            logger.info(f"Item partially updated: {item_id}")
            
            # Возврат полного объекта
            full_schema = ItemSchema()
            return full_schema.dump(item), 200
            
        except ValidationError as e:
            return {'errors': e.messages}, 400
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error patching item {item_id}: {str(e)}")
            return {'error': 'Internal server error'}, 500
    
    def delete(self, item_id):
        """Удаление товара."""
        try:
            item = Item.query.get(item_id)
            
            if not item:
                return {'error': 'Item not found'}, 404
            
            db.session.delete(item)
            db.session.commit()
            
            logger.info(f"Item deleted: {item_id}")
            return {'message': 'Item deleted successfully'}, 200
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting item {item_id}: {str(e)}")
            return {'error': 'Internal server error'}, 500