from __future__ import annotations

from chaughadiya_api.domain.chaughadiya import ChaughadiyaCalculator
from chaughadiya_api.schemas.requests import DailyChaughadiyaQuery, MuhuratQuery


class ChaughadiyaService:
    def __init__(self, calculator_cls=ChaughadiyaCalculator) -> None:
        self.calculator_cls = calculator_cls

    def _build_calculator(self, coordinates):
        return self.calculator_cls(coordinates.latitude, coordinates.longitude)

    @staticmethod
    def _location_payload(coordinates) -> dict:
        return {"latitude": coordinates.latitude, "longitude": coordinates.longitude}

    def get_daily_chaughadiya(self, query: DailyChaughadiyaQuery) -> dict:
        calculator = self._build_calculator(query.coordinates)
        daily = calculator.calculate(query.date)
        payload = daily.to_payload()
        payload["location"] = self._location_payload(query.coordinates)
        return payload

    def get_current_muhurat(self, query: MuhuratQuery) -> dict:
        calculator = self._build_calculator(query.coordinates)
        daily = calculator.calculate(query.timestamp.date())
        slot = daily.find_slot_for(query.timestamp)
        payload = daily.to_payload()
        payload["location"] = self._location_payload(query.coordinates)
        payload["current-muhurat-id"] = slot.muhurat_id
        payload["current-muhurat"] = slot.name
        payload["current-muhurat-start-time"] = slot.start.strftime("%H:%M:%S")
        payload["current-muhurat-end-time"] = slot.end.strftime("%H:%M:%S")
        payload["current_muhurat"] = slot.to_payload()
        return payload

