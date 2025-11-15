from __future__ import annotations

from flask import Blueprint, jsonify, request

from chaughadiya_api.schemas.requests import (
    DailyChaughadiyaQuery,
    MuhuratQuery,
    TithiQuery,
    TithiRangeQuery,
)
from chaughadiya_api.services.chaughadiya_service import ChaughadiyaService
from chaughadiya_api.services.tithi_service import TithiService


api_bp = Blueprint("api", __name__)

_chaughadiya_service = ChaughadiyaService()
_tithi_service = TithiService()


@api_bp.get("/get-chaughadiya")
def get_chaughadiya():
    query = DailyChaughadiyaQuery.from_request_args(request.args)
    response = _chaughadiya_service.get_daily_chaughadiya(query)
    return jsonify(response)


@api_bp.get("/get-muhurat")
def get_muhurat():
    query = MuhuratQuery.from_request_args(request.args)
    response = _chaughadiya_service.get_current_muhurat(query)
    return jsonify(response)


@api_bp.get("/get-tithi")
def get_tithi():
    query = TithiQuery.from_request_args(request.args)
    response = _tithi_service.get_tithi(query)
    return jsonify(response)


@api_bp.get("/get-tithi-range")
def get_tithi_range():
    query = TithiRangeQuery.from_request_args(request.args)
    response = _tithi_service.get_tithi_range(query)
    return jsonify({"tithis": response})

