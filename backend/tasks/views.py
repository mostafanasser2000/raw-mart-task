from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from backend.models import TaskStatus
from backend.tasks.schema import TaskSchema, TaskUpdateSchema
from backend.tasks.service import (
    create_task,
    delete_task,
    get_task,
    get_user_tasks,
    update_task,
)

bp = Blueprint("tasks", __name__, url_prefix="/api/tasks")


@bp.route("", methods=["GET", "POST"])
@jwt_required()
def tasks():
    user_id = int(get_jwt_identity())
    if request.method == "GET":
        tasks = get_user_tasks(user_id)
        return jsonify({"tasks": [task.to_dict() for task in tasks]}), 200
    schema = TaskSchema()
    payload = request.get_json(silent=True) or {}
    data = schema.load(payload)
    status_str = data.get("status")
    status = TaskStatus(status_str) if status_str else TaskStatus.PENDING
    task = create_task(
        title=data["title"],
        description=data.get("description", ""),
        status=status,
        user_id=user_id,
    )
    return jsonify({"task": task.to_dict()}), 201


@bp.route("/<int:task_id>", methods=["GET", "PUT"])
@jwt_required()
def task_detail(task_id: int):
    task = get_task(task_id)
    user_id = int(get_jwt_identity())

    if task is None:
        return jsonify({"error": "Task not found"}), 404
    if task.user_id != user_id:
        return jsonify({"error": "Permission denied"}), 403

    if request.method == "GET":
        return jsonify({"task": task.to_dict()}), 200

    schema = TaskUpdateSchema()
    payload = request.get_json(silent=True) or {}
    data = schema.load(payload)
    status_str = data.get("status")
    status = TaskStatus(status_str) if status_str else task.status
    task = update_task(
        task_id=task_id,
        title=data.get("title", task.title),
        description=data.get("description", task.description),
        status=status,
    )
    return jsonify({"task": task.to_dict()}), 200


@bp.route("/<int:task_id>", methods=["DELETE"])
@jwt_required()
def task_delete(task_id: int):
    task_id = int(task_id)
    user_id = int(get_jwt_identity())
    task = get_task(task_id)
    if task is None:
        return jsonify({"error": "Task not found"}), 404
    if task.user_id != user_id:
        return jsonify({"error": "Permission denied"}), 403
    task = delete_task(task_id)
    return jsonify({"message": "Task deleted successfully"}), 204
