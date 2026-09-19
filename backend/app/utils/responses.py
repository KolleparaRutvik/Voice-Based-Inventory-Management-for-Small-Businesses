"""Response helpers for consistent API responses."""
from flask import jsonify


def success_response(data=None, status_code=200):
    """Return a successful API response."""
    response = {"success": True}
    if data is not None:
        response["data"] = data
    return jsonify(response), status_code


def error_response(message, code="ERROR", status_code=400):
    """Return an error API response."""
    return jsonify({
        "success": False,
        "error": {
            "code": code,
            "message": message
        }
    }), status_code
