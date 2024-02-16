import json
from datetime import datetime
from datetime import timedelta
from datetime import tzinfo
from io import TextIOWrapper
from typing import Any
from typing import cast

import pandas as pd

from .data_source import DataSource
from .diagnostic_data import DiagnosticData


class FileDataSource(DataSource):
    def __init__(self, file: TextIOWrapper) -> None:
        self._file = cast(DiagnosticData, json.load(file)["data"])

    def _deserialize(self, data: dict[str, Any] | None, tz: tzinfo | None, freq: str) -> pd.DataFrame | None:
        if data is None:
            return None

        d = {pd.Timestamp(k, tz=tz): v for k, v in data.items()}
        df = pd.DataFrame.from_dict(d, orient="index")
        return df.asfreq(freq)

    async def load_sensor_history(self, now: datetime, _period: timedelta) -> pd.DataFrame | None:
        return self._deserialize(self._file["load_history"], now.tzinfo, "h")

    def get_soc(self) -> float | None:
        return self._file["soc"]

    def load_solar_forecast(self, now: datetime, _period: timedelta) -> pd.DataFrame | None:
        return self._deserialize(self._file["solar_forecast"], now.tzinfo, "h")

    def load_electricity_rates(self, now: datetime, _period: timedelta) -> pd.DataFrame | None:
        return self._deserialize(self._file["electricity_rates"], now.tzinfo, "h")

    def load_load_forecast(self, now: datetime, _period: timedelta) -> pd.DataFrame | None:
        return self._deserialize(self._file["load_forecast"], now.tzinfo, "h")
