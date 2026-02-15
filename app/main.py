from flask import Flask, jsonify, request
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
    
    @app.route("/tasks", methods=["POST"])
    def add_task():
        data = request.get_json()

        if not data or "title" not in data:
            return jsonify({"error": "Title is required"}), 400
        
        task = task_service.add_task(data["title"])
        return jsonify({"title": task.title, "completed": task.completed}), 201
    
    return app
    