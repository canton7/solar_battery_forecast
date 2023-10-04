from abc import ABC
from abc import abstractmethod
from datetime import datetime
from datetime import timedelta

import pandas as pd


class DataSource(ABC):
    @abstractmethod
    async def load_sensor_history(self, now: datetime, period: timedelta) -> pd.DataFrame | None:
        pass

    @abstractmethod
    def get_soc(self) -> float | None:
        pass

    @abstractmethod
    def load_solar_forecast(self, now: datetime, period: timedelta) -> pd.DataFrame | None:
        pass

    @abstractmethod
    def load_electricity_rates(self, now: datetime, period: timedelta) -> pd.DataFrame | None:
        pass
