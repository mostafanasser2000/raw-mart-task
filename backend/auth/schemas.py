from marshmallow import (
    EXCLUDE,
    Schema,
    ValidationError,
    fields,
    validate,
    validates_schema,
)


class RegisterSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    email = fields.Email(required=True)
    name = fields.String(required=True, validate=validate.Length(min=1, max=64))
    password1 = fields.String(
        required=True, load_only=True, validate=validate.Length(min=8)
    )
    password2 = fields.String(required=True, load_only=True)

    @validates_schema
    def validate_and_normalize(self, data, **kwargs):
        name = data.get("name", "").strip()
        if not name:
            raise ValidationError("Name cannot be empty.", field_name="name")
        data["name"] = name
        if data["password1"] != data["password2"]:
            raise ValidationError("Passwords do not match.", field_name="password2")


class LoginSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    email = fields.Email(required=True)
    password = fields.String(
        required=True, load_only=True, validate=validate.Length(min=1)
    )


class RefreshTokenSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    refresh_token = fields.String(required=True, validate=validate.Length(min=1))
    refresh_token = fields.String(required=True, validate=validate.Length(min=1))
