from __future__ import annotations

import datetime as dt

from chaughadiya_api.domain.tithi import TithiCalculator, calculate_tithi_range
from chaughadiya_api.schemas.requests import TithiQuery, TithiRangeQuery


class TithiService:
    def __init__(self, calculator_cls=TithiCalculator) -> None:
        self.calculator_cls = calculator_cls

    def get_tithi(self, query: TithiQuery) -> dict:
        calculator = self.calculator_cls()
        result = calculator.calculate(query.moment)
        metadata = {
            "input_date": query.input_value,
            "latitude": query.coordinates.latitude,
            "longitude": query.coordinates.longitude,
            "timezone": query.timezone.zone,
        }
        return result.to_payload(metadata)

    def get_tithi_range(self, query: TithiRangeQuery) -> list[dict]:
        calculator = self.calculator_cls()
        results = calculate_tithi_range(calculator, query.start_date, query.end_date, query.timezone)

        entries = []
        current_date = query.start_date
        for result in results:
            metadata = {
                "input_date": current_date.isoformat(),
                "latitude": query.coordinates.latitude,
                "longitude": query.coordinates.longitude,
                "timezone": query.timezone.zone,
            }
            entries.append(result.to_payload(metadata))
            current_date += dt.timedelta(days=1)
        return entries

