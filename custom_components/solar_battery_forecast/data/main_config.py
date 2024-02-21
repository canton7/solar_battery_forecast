from typing import TypedDict


# TODO: Phase this out, and move to UserConfig
class MainConfig(TypedDict):
    load_power_sum_sensor: str
    soc_sensor: str
    solar_forecast_today_sensor: str
    solar_forecast_tomorrow_sensor: str
    solar_forecast_d3_sensor: str
