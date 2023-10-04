import json
from datetime import datetime
from datetime import timedelta
from io import TextIOWrapper

import pandas as pd

from .data_source import DataSource


class FileDataSource(DataSource):
    def __init__(self, file: TextIOWrapper) -> None:
        self._file = json.load(file)

    async def load_sensor_history(self, now: datetime, period: timedelta) -> pd.DataFrame | None:
        pass

    def get_soc(self) -> float | None:
        pass

    def load_solar_forecast(self, now: datetime, period: timedelta) -> pd.DataFrame | None:
        pass

    def load_electricity_rates(self, now: datetime, period: timedelta) -> pd.DataFrame | None:
        pass
