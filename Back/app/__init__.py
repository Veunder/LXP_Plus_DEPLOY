from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

import os

from app.config import Config
from app.extensions import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # CORS: разрешаем фронту обращаться к /api.
    # Локальные адреса Vite (host 127.0.0.1 — см. vite.config.js; 127.0.0.1 и
    # localhost для браузера РАЗНЫЕ, поэтому оба варианта). На бою адрес фронта
    # (например, https://имя.onrender.com) задаётся переменной FRONTEND_ORIGIN,
    # можно несколько через запятую — править код не нужно.
    origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ]
    frontend_origin = os.getenv("FRONTEND_ORIGIN")
    if frontend_origin:
        origins.extend(o.strip() for o in frontend_origin.split(",") if o.strip())
    CORS(app, resources={r"/api/*": {"origins": origins}})

    # Импорт маршрутов внутри функции — чтобы избежать циклических импортов.
    from app.routes import api
    app.register_blueprint(api)

    # Ошибки отдаём в JSON, чтобы фронт показывал понятный текст, а не заглушку.
    @app.errorhandler(HTTPException)
    def _handle_http_exception(e):
        return jsonify({"error": e.description}), e.code

    @app.errorhandler(Exception)
    def _handle_exception(e):
        return jsonify({"error": f"Внутренняя ошибка сервера: {e}"}), 500

    # Создаём таблицы, если их ещё нет.
    with app.app_context():
        db.create_all()
        # Авто-наполнение демо-данными на хостинге (например, Render): если
        # задана SEED_ON_START и база пустая — заполняем. Повторно не затирает.
        if os.getenv("SEED_ON_START", "").strip().lower() in ("1", "true", "yes"):
            from app.demo_seed import seed_demo
            seed_demo()

    return app
