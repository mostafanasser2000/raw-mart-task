from typing import Optional

from sqlalchemy import select

from backend.extensions import db
from backend.models import Task, TaskStatus


def create_task(
    title: str,
    description: str,
    status: TaskStatus,
    user_id: int,
) -> Task:
    task = Task(
        title=title,
        description=description,
        status=status,
        user_id=user_id,
    )
    db.session.add(task)
    db.session.commit()
    return task


def get_task(task_id: int) -> Optional[Task]:
    stmt = select(Task).where(Task.id == task_id)
    return db.session.scalar(stmt)


def get_user_tasks(user_id: int) -> list[Task]:
    stmt = select(Task).where(Task.user_id == user_id).order_by(Task.created_at.desc())
    return db.session.scalars(stmt).all()


def update_task(
    task_id: int,
    title: str,
    description: str,
    status: TaskStatus,
) -> Optional[Task]:
    task = get_task(task_id)
    if task is None:
        return None

    task.title = title
    task.description = description
    task.status = status

    db.session.commit()
    return task


def delete_task(task_id: int) -> Optional[Task]:
    task = get_task(task_id)
    if task is None:
        return None

    db.session.delete(task)
    db.session.commit()
    return task
    return task
