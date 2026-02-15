from flask import Flask, jsonify
from app.core.config import Config
from app.services.task_service import TaskService


task_service = TaskService()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    @app.route("/tasks")
    def tasks():
        tasks = task_service.get_tasks()
        return jsonify([
            {"title": t.title, "completed": t.completed}
                         for t in tasks
        ])
    
    return app
    