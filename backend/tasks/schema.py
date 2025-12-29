from marshmallow import EXCLUDE, Schema, fields, validate

from backend.models import TaskStatus


class TaskSchema(Schema):

    title = fields.String(required=True, validate=validate.Length(min=1, max=255))
    description = fields.String(required=False, validate=validate.Length(max=500))
    status = fields.String(
        required=False,
        validate=validate.OneOf([status.value for status in TaskStatus]),
    )

    class Meta:
        unknown = EXCLUDE


class TaskUpdateSchema(Schema):

    title = fields.String(required=False, validate=validate.Length(min=1, max=255))
    description = fields.String(required=False, validate=validate.Length(max=500))
    status = fields.String(
        required=False,
        validate=validate.OneOf([status.value for status in TaskStatus]),
    )

    class Meta:
        unknown = EXCLUDE
