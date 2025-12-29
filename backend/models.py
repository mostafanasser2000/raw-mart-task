import enum
from datetime import datetime, timezone

import sqlalchemy as sa
import sqlalchemy.orm as so
from werkzeug.security import check_password_hash, generate_password_hash

from backend.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    email: so.Mapped[str] = so.mapped_column(
        sa.String(64), unique=True, index=True, nullable=False
    )
    name: so.Mapped[str] = so.mapped_column(sa.String(64), nullable=False)
    password_hash: so.Mapped[str] = so.mapped_column(sa.String(256), nullable=False)

    tasks: so.Mapped[list["Task"]] = so.relationship(
        "Task",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self, include_email: bool = False) -> dict:
        data = {
            "id": self.id,
            "name": self.name,
            "tasks": [task.to_dict() for task in self.tasks],
        }
        if include_email:
            data["email"] = self.email
        return data


class TaskStatus(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class Task(db.Model):
    __tablename__ = "tasks"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    title: so.Mapped[str] = so.mapped_column(sa.String(255), nullable=False)
    description: so.Mapped[str] = so.mapped_column(sa.String(500), default="")
    status: so.Mapped[TaskStatus] = so.mapped_column(
        sa.Enum(
            TaskStatus,
            name="task_status",
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
        default=TaskStatus.PENDING,
    )
    created_at: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    user_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("users.id"), index=True, nullable=False
    )
    user: so.Mapped["User"] = so.relationship(back_populates="tasks")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
        }


class TokenBlocklist(db.Model):
    __tablename__ = "token_blocklist"

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, unique=True)
    token_type = db.Column(db.String(10), nullable=False)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    revoked = db.Column(db.Boolean, nullable=False, default=False)
    expires = db.Column(db.DateTime(timezone=True), nullable=False)

    user = db.relationship("User", lazy="joined")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "jti": self.jti,
            "token_type": self.token_type,
            "user_id": self.user_id,
            "revoked": self.revoked,
            "expires": self.expires.isoformat(),
        }
