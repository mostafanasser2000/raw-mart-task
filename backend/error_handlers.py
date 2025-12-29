import json
from typing import Tuple

from flask import Blueprint, jsonify
from marshmallow import ValidationError

bp = Blueprint("error_handlers", __name__)


@bp.app_errorhandler(ValidationError)
def validation_error(e: ValidationError) -> Tuple[json, int]:
    return jsonify({"errors": e.messages}), 400


@bp.app_errorhandler(404)
def not_found_error(e):
    return jsonify({"error": "Not Found"}), 404


@bp.app_errorhandler(500)
def server_error(e):
    return jsonify({"error": "Server Error"}), 500
