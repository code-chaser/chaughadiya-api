from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

import pytz
from werkzeug.datastructures import MultiDict

from chaughadiya_api.errors import ValidationError
from chaughadiya_api.utils import parsing


@dataclass(frozen=True)
class GeoCoordinates:
    latitude: float
    longitude: float

    @classmethod
    def from_args(cls, args: MultiDict[str, str]) -> "GeoCoordinates":
        return cls(
            latitude=parsing.parse_float(args.get("latitude"), "latitude", min_value=-90, max_value=90),
            longitude=parsing.parse_float(args.get("longitude"), "longitude", min_value=-180, max_value=180),
        )


@dataclass(frozen=True)
class DailyChaughadiyaQuery:
    date: dt.date
    coordinates: GeoCoordinates

    @classmethod
    def from_request_args(cls, args: MultiDict[str, str]) -> "DailyChaughadiyaQuery":
        return cls(date=parsing.parse_date(args.get("date"), "date"), coordinates=GeoCoordinates.from_args(args))


@dataclass(frozen=True)
class MuhuratQuery:
    timestamp: dt.datetime
    coordinates: GeoCoordinates

    @classmethod
    def from_request_args(cls, args: MultiDict[str, str]) -> "MuhuratQuery":
        timestamp = parsing.parse_datetime(args.get("timestamp"), "timestamp")
        return cls(timestamp=timestamp, coordinates=GeoCoordinates.from_args(args))


@dataclass(frozen=True)
class TithiQuery:
    moment: dt.datetime
    timezone: pytz.timezone
    coordinates: GeoCoordinates
    input_value: str

    @classmethod
    def from_request_args(cls, args: MultiDict[str, str]) -> "TithiQuery":
        raw_date = parsing.require_value(args.get("date"), "date")
        if len(raw_date) == 10:
            parsed = dt.datetime.strptime(raw_date, "%Y-%m-%d").replace(hour=12, minute=0, second=0)
        else:
            parsed = parsing.parse_datetime(raw_date, "date")

        timezone = parsing.parse_timezone(args.get("timezone"))
        localized = timezone.localize(parsed)
        return cls(moment=localized, timezone=timezone, coordinates=GeoCoordinates.from_args(args), input_value=raw_date)


@dataclass(frozen=True)
class TithiRangeQuery:
    start_date: dt.date
    end_date: dt.date
    timezone: pytz.timezone
    coordinates: GeoCoordinates

    @classmethod
    def from_request_args(cls, args: MultiDict[str, str]) -> "TithiRangeQuery":
        start = parsing.parse_date(args.get("start_date"), "start_date")
        end = parsing.parse_date(args.get("end_date"), "end_date")
        if end < start:
            raise ValidationError("end_date must be on or after start_date")

        return cls(
            start_date=start,
            end_date=end,
            timezone=parsing.parse_timezone(args.get("timezone")),
            coordinates=GeoCoordinates.from_args(args),
        )

