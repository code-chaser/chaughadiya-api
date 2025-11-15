from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Iterable, List, Sequence

from suntime import Sun, SunTimeException

from chaughadiya_api.errors import DomainError

DAY_NAMES = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday",
}

MUHURATS = {
    0: "Udveg",
    1: "Kaal",
    2: "Rog",
    3: "Chal",
    4: "Labh",
    5: "Amrit",
    6: "Shubh",
}

CHAUGHADIYA = {
    0: [[5, 1, 6, 2, 0, 3, 4, 5], [3, 2, 1, 4, 0, 6, 5, 3]],
    1: [[2, 0, 3, 4, 5, 1, 6, 2], [1, 4, 0, 6, 5, 3, 2, 1]],
    2: [[4, 5, 1, 6, 2, 0, 3, 4], [0, 6, 5, 3, 2, 1, 4, 0]],
    3: [[6, 2, 0, 3, 4, 5, 1, 6], [5, 3, 2, 1, 4, 0, 6, 5]],
    4: [[3, 4, 5, 1, 6, 2, 0, 3], [2, 1, 4, 0, 6, 5, 3, 2]],
    5: [[1, 6, 2, 0, 3, 4, 5, 1], [4, 0, 6, 5, 3, 2, 1, 4]],
    6: [[0, 3, 4, 5, 1, 6, 2, 0], [6, 5, 3, 2, 1, 4, 0, 6]],
}


@dataclass(frozen=True)
class MuhuratSlot:
    muhurat_id: int
    name: str
    phase: str
    start: dt.datetime
    end: dt.datetime

    def to_payload(self) -> dict:
        return {
            "muhurat-id": self.muhurat_id,
            "muhurat": self.name,
            "phase": self.phase,
            "start-time": self.start.strftime("%H:%M:%S"),
            "end-time": self.end.strftime("%H:%M:%S"),
        }


@dataclass(frozen=True)
class DailyChaughadiya:
    date: dt.date
    prev_sunset: dt.datetime
    sunrise: dt.datetime
    sunset: dt.datetime
    next_sunrise: dt.datetime
    slots: Sequence[MuhuratSlot]
    day_segment_seconds: float
    night_segment_seconds: float

    def to_payload(self) -> dict:
        return {
            "date": self.date.isoformat(),
            "weekday": DAY_NAMES[self.date.weekday()],
            "prev-sunset-time": self.prev_sunset.strftime("%H:%M:%S"),
            "sunrise-time": self.sunrise.strftime("%H:%M:%S"),
            "sunset-time": self.sunset.strftime("%H:%M:%S"),
            "next-sunrise-time": self.next_sunrise.strftime("%H:%M:%S"),
            "day-muhurat-length": str(dt.timedelta(seconds=self.day_segment_seconds)),
            "night-muhurat-length": str(dt.timedelta(seconds=self.night_segment_seconds)),
            "chaughadiya": [slot.to_payload() for slot in self.slots],
        }

    def find_slot_for(self, moment: dt.datetime) -> MuhuratSlot:
        for slot in self.slots:
            if slot.start <= moment < slot.end:
                return slot
        raise DomainError("Timestamp is outside of calculated muhurats", payload={"timestamp": moment.isoformat()})


class ChaughadiyaCalculator:
    """Encapsulates the logic required to compute chaughadiya windows."""

    def __init__(self, latitude: float, longitude: float) -> None:
        self.latitude = latitude
        self.longitude = longitude
        self.sun = Sun(latitude, longitude)

    def calculate(self, date: dt.date) -> DailyChaughadiya:
        target = dt.datetime.combine(date, dt.time())
        try:
            sunrise = self.sun.get_sunrise_time(target)
            sunset = self.sun.get_sunset_time(target)
            prev_sunset = self.sun.get_sunset_time(target - dt.timedelta(days=1))
            next_sunrise = self.sun.get_sunrise_time(target + dt.timedelta(days=1))
        except SunTimeException as exc:
            raise DomainError("Unable to calculate sun times", payload={"date": date.isoformat()}) from exc

        while sunset < sunrise:
            prev_sunset = sunset
            sunset += dt.timedelta(days=1)

        pre_dawn_length = (sunrise - prev_sunset).total_seconds() / 8
        day_length = (sunset - sunrise).total_seconds() / 8
        night_length = (next_sunrise - sunset).total_seconds() / 8

        slots = self._build_slots(
            weekday=date.weekday(),
            prev_sunset=prev_sunset,
            sunrise=sunrise,
            sunset=sunset,
            lengths=(pre_dawn_length, day_length, night_length),
        )

        return DailyChaughadiya(
            date=date,
            prev_sunset=prev_sunset,
            sunrise=sunrise,
            sunset=sunset,
            next_sunrise=next_sunrise,
            slots=slots,
            day_segment_seconds=day_length,
            night_segment_seconds=night_length,
        )

    def _build_slots(
        self,
        weekday: int,
        prev_sunset: dt.datetime,
        sunrise: dt.datetime,
        sunset: dt.datetime,
        lengths: Sequence[float],
    ) -> List[MuhuratSlot]:
        slots: List[MuhuratSlot] = []
        prev_day = (weekday - 1) % 7

        # Pre-dawn segment (previous sunset to today's sunrise)
        for index in range(8):
            start = prev_sunset + dt.timedelta(seconds=lengths[0] * index)
            end = prev_sunset + dt.timedelta(seconds=lengths[0] * (index + 1))
            muhurat_id = CHAUGHADIYA[weekday][0][index]
            muhurat_name = MUHURATS[CHAUGHADIYA[prev_day][1][index]]
            slots.append(MuhuratSlot(muhurat_id, muhurat_name, "pre-dawn", start, end))

        # Day segment
        for index in range(8):
            start = sunrise + dt.timedelta(seconds=lengths[1] * index)
            end = sunrise + dt.timedelta(seconds=lengths[1] * (index + 1))
            muhurat_id = CHAUGHADIYA[weekday][0][index]
            muhurat_name = MUHURATS[CHAUGHADIYA[weekday][0][index]]
            slots.append(MuhuratSlot(muhurat_id, muhurat_name, "day", start, end))

        # Night segment
        for index in range(8):
            start = sunset + dt.timedelta(seconds=lengths[2] * index)
            end = sunset + dt.timedelta(seconds=lengths[2] * (index + 1))
            muhurat_id = CHAUGHADIYA[weekday][0][index]
            muhurat_name = MUHURATS[CHAUGHADIYA[weekday][1][index]]
            slots.append(MuhuratSlot(muhurat_id, muhurat_name, "night", start, end))

        return slots

