from __future__ import annotations

import datetime as dt
from typing import Optional

import pytz

from chaughadiya_api.errors import ValidationError


def require_value(value: Optional[str], field: str) -> str:
    if value is None or value == "":
        raise ValidationError(f"{field} parameter is required", payload={"field": field})
    return value


def parse_float(value: Optional[str], field: str, *, min_value: Optional[float] = None, max_value: Optional[float] = None) -> float:
    text = require_value(value, field)
    try:
        number = float(text)
    except ValueError as exc:  # pragma: no cover - simple defensive code
        raise ValidationError(f"{field} must be a valid number", payload={"field": field}) from exc

    if min_value is not None and number < min_value:
        raise ValidationError(f"{field} must be >= {min_value}", payload={"field": field, "min": min_value})
    if max_value is not None and number > max_value:
        raise ValidationError(f"{field} must be <= {max_value}", payload={"field": field, "max": max_value})
    return number


def parse_date(value: Optional[str], field: str, fmt: str = "%Y-%m-%d") -> dt.date:
    text = require_value(value, field)
    try:
        return dt.datetime.strptime(text, fmt).date()
    except ValueError as exc:
        raise ValidationError(f"{field} must match format {fmt}", payload={"field": field}) from exc


def parse_datetime(value: Optional[str], field: str, fmt: str = "%Y-%m-%d %H:%M:%S") -> dt.datetime:
    text = require_value(value, field)
    try:
        return dt.datetime.strptime(text, fmt)
    except ValueError as exc:
        raise ValidationError(f"{field} must match format {fmt}", payload={"field": field}) from exc


def parse_timezone(value: Optional[str], default: str = "UTC") -> pytz.timezone:
    target = value or default
    try:
        return pytz.timezone(target)
    except pytz.UnknownTimeZoneError as exc:
        raise ValidationError("timezone parameter is invalid", payload={"field": "timezone"}) from exc

