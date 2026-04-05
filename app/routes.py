import json
from flask import Blueprint, jsonify, request, Response
from app.services.task_service import TaskService


tasks_bp = Blueprint("tasks", __name__)
task_service = TaskService()


@tasks_bp.route("/tasks/<int:user_id>", methods=["GET"])
def get_tasks(user_id):
    tasks = task_service.get_tasks(user_id)
    data = [{"id": t.id, "title": t.title, "completed": t.completed} for t in tasks]
    return Response(
        json.dumps(data, ensure_ascii=False),
        mimetype="application/json"
    )


@tasks_bp.route("/tasks/<int:user_id>", methods=["POST"])
def add_task(user_id):
    data = request.get_json()
    if not data or "title" not in data:
        return jsonify({"error": "Title is required"}), 400
    task = task_service.add_task(user_id, data["title"])
    if task is None:
        return jsonify({"error": "Task already exists"}), 409
    return jsonify({"id": task.id, "title": task.title, "completed": task.completed}), 201


@tasks_bp.route("/tasks/<int:user_id>/<int:task_id>", methods=["DELETE"])
def delete_task(user_id, task_id):
    if task_service.delete_task(user_id, task_id):
        return jsonify({"message": "Deleted"}), 200
    return jsonify({"error": "Task not found"}), 404