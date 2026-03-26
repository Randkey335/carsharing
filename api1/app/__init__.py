from flask import Flask
from .config import Config
from .models import db


def create_app(test_config=None):
    """Фабрика приложения Flask"""
    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)
    
    # Инициализация БД
    db.init_app(app)
    
    # Регистрация blueprints
    from .routes import api
    app.register_blueprint(api)
    
    # Создание таблиц при первом запуске
    with app.app_context():
        db.create_all()
    
    return app
