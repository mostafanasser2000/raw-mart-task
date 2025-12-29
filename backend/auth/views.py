from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)

from backend.auth.schemas import LoginSchema, RegisterSchema
from backend.auth.service import (
    add_token_to_database,
    create_user,
    get_user,
    is_token_revoked,
    revoke_all_user_tokens,
    revoke_token,
)
from backend.extensions import jwt
from backend.models import User

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@bp.route("/register", methods=["POST"])
def register():
    schema = RegisterSchema()
    try:
        payload = request.get_json(silent=True) or {}
        data = schema.load(payload)
        user = create_user(
            name=data["name"], email=data["email"], password=data["password1"]
        )

        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        add_token_to_database(access_token, "sub")
        add_token_to_database(refresh_token, "sub")
        return (
            jsonify(
                {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": user.to_dict(include_email=True),
                }
            ),
            201,
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@bp.route("/login", methods=["POST"])
def login():
    schema = LoginSchema()
    payload = request.get_json(silent=True) or {}
    data = schema.load(payload)

    user = get_user(data["email"])
    if not user or not user.check_password(data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    revoke_all_user_tokens(user.id)

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    add_token_to_database(access_token, "sub")
    add_token_to_database(refresh_token, "sub")

    return (
        jsonify(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": user.to_dict(include_email=True),
            }
        ),
        200,
    )


@bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    user_id = int(get_jwt_identity())
    new_access_token = create_access_token(identity=str(user_id))
    add_token_to_database(
        new_access_token,
    )
    return jsonify({"access_token": new_access_token}), 200


@bp.route("/logout", methods=["POST"])
@jwt_required(refresh=True)
def logout():
    try:
        jti = get_jwt()["jti"]
        user_id = int(get_jwt_identity())
        revoke_token(jti, user_id)
        return jsonify({"message": "Logout successful"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@jwt.user_lookup_loader
def user_loader_callback(jwt_headers, jwt_payload):
    return User.query.get(int(jwt_payload["sub"]))


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_headers, jwt_payload):
    return is_token_revoked(jwt_payload)
