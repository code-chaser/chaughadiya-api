from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from flask import jsonify, render_template, request


class ApiError(Exception):
    """Base exception for API errors with a JSON representation."""

    status_code: int = 500

    def __init__(self, message: str, *, status_code: Optional[int] = None, payload: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.payload = payload or {}
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self) -> Dict[str, Any]:
        data = {"error": self.message}
        data.update(self.payload)
        return data


class ValidationError(ApiError):
    status_code = 400


class NotFoundError(ApiError):
    status_code = 404


class DomainError(ApiError):
    status_code = 422


def register_error_handlers(app) -> None:  # pragma: no cover - glue logic
    @app.errorhandler(ApiError)
    def handle_api_error(error: ApiError):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.errorhandler(404)
    def handle_not_found(error):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Resource not found"}), 404
        return render_template("static/page-not-found.html"), 404

    @app.errorhandler(Exception)
    def handle_unexpected(error: Exception):
        app.logger.exception("Unexpected application error")
        response = jsonify({"error": "Internal server error"})
        response.status_code = 500
        return response

