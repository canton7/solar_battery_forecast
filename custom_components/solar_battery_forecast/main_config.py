from typing import TypedDict


class MainConfig(TypedDict):
    load_power_sum_sensor: str
    soc_sensor: str
    solar_forecast_today_sensor: str
    solar_forecast_tomorrow_sensor: str
    solar_forecast_d3_sensor: str
    electricity_import_rate_sensor: str
    electricity_feed_in_rate_sensor: str
