from flask import Flask

from backend import auth, error_handlers, tasks
from backend.config import Config
from backend.extensions import cors, db, jwt, migrate


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    configure_extensions(app)
    register_blueprints(app)
    return app


def configure_extensions(app):
    """Configure flask extensions"""
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)


def register_blueprints(app):
    app.register_blueprint(auth.views.bp)
    app.register_blueprint(error_handlers.bp)
    app.register_blueprint(tasks.views.bp)
