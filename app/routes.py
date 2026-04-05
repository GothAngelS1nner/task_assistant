from flask import Blueprint, jsonify, request
from app.services.task_service import TaskService

tasks_bp = Blueprint("tasks", __name__)
task_service = TaskService()

@tasks_bp.route("/tasks", methods=["GET"])
def get_tasks():
    tasks = task_service.get_tasks()
    return jsonify([
        {"id": t.id, "title": t.title, "completed": t.completed}
        for t in tasks
    ])

@tasks_bp.route("/tasks", methods=["POST"])
def add_task():
    data = request.get_json()
    if not data or "title" not in data:
        return jsonify({"error": "Title is required"}), 400
    task = task_service.add_task(data["title"])
    if task is None:
        return jsonify({"error": "Task already exists"}), 409
    return jsonify({"id": task.id, "title": task.title, "completed": task.completed}), 201

@tasks_bp.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    if task_service.delete_task(task_id):
        return jsonify({"message": "Deleted"}), 200
    return jsonify({"error": "Task not found"}), 404