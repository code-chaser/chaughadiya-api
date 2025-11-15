from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import List, Sequence

import pytz

from chaughadiya_api.errors import DomainError

try:  # pragma: no cover - import guarded for environments without pyswisseph
    import swisseph as swe
except ImportError:  # pragma: no cover
    swe = None


TITHI_NAMES = [
    "Pratipada (Shukla)",
    "Dwitiya (Shukla)",
    "Tritiya (Shukla)",
    "Chaturthi (Shukla)",
    "Panchami (Shukla)",
    "Shashthi (Shukla)",
    "Saptami (Shukla)",
    "Ashtami (Shukla)",
    "Navami (Shukla)",
    "Dashami (Shukla)",
    "Ekadashi (Shukla)",
    "Dwadashi (Shukla)",
    "Trayodashi (Shukla)",
    "Chaturdashi (Shukla)",
    "Purnima",
    "Pratipada (Krishna)",
    "Dwitiya (Krishna)",
    "Tritiya (Krishna)",
    "Chaturthi (Krishna)",
    "Panchami (Krishna)",
    "Shashthi (Krishna)",
    "Saptami (Krishna)",
    "Ashtami (Krishna)",
    "Navami (Krishna)",
    "Dashami (Krishna)",
    "Ekadashi (Krishna)",
    "Dwadashi (Krishna)",
    "Trayodashi (Krishna)",
    "Chaturdashi (Krishna)",
    "Amavasya",
]

TITHI_SIGNIFICANCE = {
    "Pratipada (Shukla)": "Beginning, new ventures",
    "Dwitiya (Shukla)": "Worship of deities",
    "Tritiya (Shukla)": "Auspicious for spiritual activities",
    "Chaturthi (Shukla)": "Worship of Ganesha",
    "Panchami (Shukla)": "Worship of Saraswati",
    "Shashthi (Shukla)": "Worship of Kartikeya",
    "Saptami (Shukla)": "Worship of Sun",
    "Ashtami (Shukla)": "Worship of Durga",
    "Navami (Shukla)": "Worship of Durga",
    "Dashami (Shukla)": "Auspicious for ceremonies",
    "Ekadashi (Shukla)": "Fasting and spiritual practices",
    "Dwadashi (Shukla)": "Worship of Vishnu",
    "Trayodashi (Shukla)": "Auspicious for religious activities",
    "Chaturdashi (Shukla)": "Worship of Shiva",
    "Purnima": "Full Moon - highly auspicious",
    "Pratipada (Krishna)": "Beginning of waning phase",
    "Dwitiya (Krishna)": "Second day of waning",
    "Tritiya (Krishna)": "Third day of waning",
    "Chaturthi (Krishna)": "Fourth day of waning",
    "Panchami (Krishna)": "Fifth day of waning",
    "Shashthi (Krishna)": "Sixth day of waning",
    "Saptami (Krishna)": "Seventh day of waning",
    "Ashtami (Krishna)": "Worship of Krishna",
    "Navami (Krishna)": "Ninth day of waning",
    "Dashami (Krishna)": "Tenth day of waning",
    "Ekadashi (Krishna)": "Fasting and spiritual practices",
    "Dwadashi (Krishna)": "Twelfth day of waning",
    "Trayodashi (Krishna)": "Thirteenth day of waning",
    "Chaturdashi (Krishna)": "Worship of Shiva",
    "Amavasya": "New Moon - for ancestor worship",
}


@dataclass(frozen=True)
class TithiResult:
    tithi_number: int
    tithi_name: str
    paksha: str
    elongation_degrees: float
    progress_percentage: float
    start_time: dt.datetime
    end_time: dt.datetime
    next_tithi_number: int
    next_tithi_name: str
    significance: str
    calculation_time: dt.datetime

    def to_payload(self, metadata: dict | None = None) -> dict:
        payload = {
            "tithi_number": self.tithi_number,
            "tithi_name": self.tithi_name,
            "paksha": self.paksha,
            "elongation_degrees": self.elongation_degrees,
            "progress_percentage": self.progress_percentage,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "next_tithi_number": self.next_tithi_number,
            "next_tithi_name": self.next_tithi_name,
            "significance": self.significance,
            "calculation_time": self.calculation_time.isoformat(),
        }
        if metadata:
            payload.update(metadata)
        return payload


class TithiCalculator:
    def __init__(self) -> None:
        if swe is None:
            raise DomainError("Swiss Ephemeris library (pyswisseph) is required for Tithi calculations")

    def calculate(self, moment: dt.datetime) -> TithiResult:
        if moment.tzinfo is None:
            moment = pytz.UTC.localize(moment)
        timestamp = moment.astimezone(pytz.UTC)

        jd = swe.julday(
            timestamp.year,
            timestamp.month,
            timestamp.day,
            timestamp.hour + timestamp.minute / 60.0 + timestamp.second / 3600.0,
        )

        sun_longitude = swe.calc_ut(jd, swe.SUN)[0][0]
        moon_longitude = swe.calc_ut(jd, swe.MOON)[0][0]

        elongation = moon_longitude - sun_longitude
        if elongation < 0:
            elongation += 360
        tithi_number = int(elongation / 12) + 1
        progress = (elongation % 12) / 12
        if tithi_number > 30:
            tithi_number %= 30
            if tithi_number == 0:
                tithi_number = 30

        tithi_name = TITHI_NAMES[tithi_number - 1]
        paksha = "Shukla Paksha (Waxing)" if tithi_number <= 15 else "Krishna Paksha (Waning)"

        remaining_degrees = 12 * (1 - progress)
        hours_remaining = remaining_degrees / 0.55
        hours_elapsed = (elongation % 12) / 0.55

        tithi_end = timestamp + dt.timedelta(hours=hours_remaining)
        tithi_start = timestamp - dt.timedelta(hours=hours_elapsed)

        next_tithi_number = (tithi_number % 30) + 1
        next_tithi_name = TITHI_NAMES[next_tithi_number - 1]

        return TithiResult(
            tithi_number=tithi_number,
            tithi_name=tithi_name,
            paksha=paksha,
            elongation_degrees=round(elongation, 2),
            progress_percentage=round(progress * 100, 2),
            start_time=tithi_start,
            end_time=tithi_end,
            next_tithi_number=next_tithi_number,
            next_tithi_name=next_tithi_name,
            significance=TITHI_SIGNIFICANCE.get(tithi_name, "Traditional lunar day"),
            calculation_time=timestamp,
        )


def calculate_tithi_range(calculator: TithiCalculator, start: dt.date, end: dt.date, timezone: pytz.timezone) -> List[TithiResult]:
    current = start
    results: List[TithiResult] = []
    while current <= end:
        localized = timezone.localize(dt.datetime.combine(current, dt.time(hour=12)))
        results.append(calculator.calculate(localized))
        current += dt.timedelta(days=1)
    return results

