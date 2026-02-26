from flask import Flask, jsonify
from flask_restful import Api
from database.db import db, init_db
from resources.item_resource import ItemListResource, ItemResource
from config import config
import logging
import os
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app(config_name=None):
    """Фабрика приложений Flask."""
    
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    
    # Загрузка конфигурации
    app.config.from_object(config[config_name])
    
    # Инициализация расширений
    init_db(app)
    
    # Настройка API
    api = Api(app)
    
    # Регистрация ресурсов
    api.add_resource(ItemListResource, '/api/items')
    api.add_resource(ItemResource, '/api/items/<int:item_id>')
    
    # Health check эндпоинт
    @app.route('/health')
    def health():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'environment': config_name
        })
    
    # Обработчик ошибок 404
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    # Обработчик ошибок 500
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    
    logger.info(f"✅ Application started in {config_name} mode")
    logger.info(f"   Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)