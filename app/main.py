from flask import Flask
from app.core.config import Config
from app.extensions import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    app.config['JSON_ENSURE_ASCII'] = False

    from app.models.task import Task
    from app.routes import tasks_bp

    with app.app_context():
        db.create_all()

    app.register_blueprint(tasks_bp)
    
    return app
    