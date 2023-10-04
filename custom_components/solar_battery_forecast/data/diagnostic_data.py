from typing import Any
from typing import TypedDict


class DiagnosticData(TypedDict):
    soc: float | Any
    load_history: dict[str, Any] | None
    initial_load_forecast: dict[str, Any] | None
    load_forecast: dict[str, Any] | None
    solar_forecast: dict[str, Any] | None
    electricity_rates: dict[str, Any] | None
    current_action: dict[str, Any] | None
    battery_forecast: dict[str, Any] | None
    initial_battery_forecast: dict[str, Any] | None
