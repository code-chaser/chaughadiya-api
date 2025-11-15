from __future__ import annotations

import datetime as dt

from flask import Blueprint, jsonify, render_template


pages_bp = Blueprint("pages", __name__)


@pages_bp.route("/")
def home():
    return render_template("static/home.html")


@pages_bp.route("/api/docs")
def api_docs():
    return render_template("static/api-documentation.html")


@pages_bp.route("/health")
def health_check():
    return jsonify({"status": "ok", "timestamp": dt.datetime.now(dt.timezone.utc).isoformat()})

