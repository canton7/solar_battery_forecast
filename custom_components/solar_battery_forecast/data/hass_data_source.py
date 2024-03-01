import logging
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from typing import Any
from typing import Iterable

import numpy as np
import pandas as pd
from homeassistant.components import recorder
from homeassistant.components.recorder import statistics
from homeassistant.core import HomeAssistant
from homeassistant.util import dt

from ..octopus_api.client import OctopusApiClient
from .data_source import DataSource
from .main_config import MainConfig
from .user_config import UserConfig

_LOGGER = logging.getLogger(__name__)


class HassDataSource(DataSource):
    def __init__(self, hass: HomeAssistant, config: MainConfig, user_config: UserConfig) -> None:
        self._hass = hass
        self._octopus_client = OctopusApiClient(user_config["octopus_account_id"], user_config["octopus_api_key"])

        self._load_power_sum_sensor = config["load_power_sum_sensor"]
        self._soc_sensor = config["soc_sensor"]
        self._solar_forecast_sensors = [
            config["solar_forecast_today_sensor"],
            config["solar_forecast_tomorrow_sensor"],
            config["solar_forecast_d3_sensor"],
        ]

    async def load_sensor_history(self, now: datetime, period: timedelta) -> pd.DataFrame | None:
        now_utc = dt.as_utc(now)
        this_hour_utc = datetime(now_utc.year, now_utc.month, now_utc.day, now_utc.hour, tzinfo=timezone.utc)
        start = now - period

        r = recorder.get_instance(self._hass)

        # Each element holds the cumulative sum at the end of that period. Therefore we need an extra period at the
        # start, so we can get the sum as it was before the first period

        stats = await r.async_add_executor_job(
            statistics.statistics_during_period,
            self._hass,
            start - timedelta(hours=1),
            None,
            {self._load_power_sum_sensor},
            "hour",
            None,
            {"sum"},
        )

        df: pd.DataFrame | None = None

        start_of_last_hour = this_hour_utc - timedelta(hours=1)

        if self._load_power_sum_sensor in stats:
            energy_sum_stats = stats[self._load_power_sum_sensor]

            def get_records() -> Iterable[dict[str, Any]]:
                prev_sum = energy_sum_stats[0]["sum"]
                for i in range(1, len(energy_sum_stats)):
                    stat = energy_sum_stats[i]
                    stat_sum = stat["sum"]
                    # If prev_sum is None, then we started off not knowing what the sum was...
                    # We'll have to keep going until we find a non-None value
                    if prev_sum is None:
                        prev_sum = stat_sum
                        continue

                    assert prev_sum is not None

                    # If the sum has decreased (!), we've probably gone back to 0
                    if stat_sum is not None and stat_sum < prev_sum:
                        prev_sum = 0
                    # If the current sum is None, then yield np.nan
                    yield {
                        "start": dt.as_local(dt.utc_from_timestamp(stat["start"])),
                        "value": (stat_sum - prev_sum if stat_sum is not None else np.nan),
                    }
                    if stat_sum is not None:
                        prev_sum = stat_sum

            df = pd.DataFrame.from_records(get_records(), index="start")
            # Make sure that any missing values at the end are filled with nan
            df = df.reindex(
                pd.date_range(start=df.iloc[0].name, end=dt.as_local(start_of_last_hour), freq="h"),  # type: ignore
                fill_value=np.nan,
            )

        # This might not include everything

        # end_of_stats = (
        #     dt.utc_from_timestamp(stats[self._load_power_sensor][-1]["end"])
        #     if self._load_power_sensor in stats and len(stats[self._load_power_sensor]) > 0
        #     else start
        # )

        # if end_of_stats < this_hour:
        #     hist = await r.async_add_executor_job(
        #         history.state_changes_during_period,
        #         self._hass,
        #         start,
        #         None,
        #         self._load_power_sensor,
        #         True,
        #         False,
        #         None,
        #         True,
        #     )
        #     print(hist)

        if df is None:
            _LOGGER.warning(
                "Unable to find history for sensor '%s'. Is this sensor correct?",
                self._load_power_sum_sensor,
            )
            return None

        return df

    def get_soc(self) -> float | None:
        state = self._hass.states.get(self._soc_sensor)
        if state is None:
            _LOGGER.warning("SoC sensor '%s' is disabled or not yet loaded", self._soc_sensor)
            return None
        str_value = state.state
        if str_value in [None, "unknown", "unavailable"]:
            _LOGGER.warning("SoC sensor '%s' has value '%s'", self._soc_sensor, str_value)
            return None
        try:
            float_value = float(str_value)
            return float_value
        except ValueError:
            _LOGGER.warning(
                "SoC sensor '%s' has non-floating-point value '%s'",
                self._soc_sensor,
                str_value,
            )
            return None

    def load_solar_forecast(self, now: datetime, period: timedelta) -> pd.DataFrame | None:
        this_hour = datetime(now.year, now.month, now.day, now.hour, tzinfo=now.tzinfo)

        periods = []
        for forecast_sensor in self._solar_forecast_sensors:
            state = self._hass.states.get(forecast_sensor)
            if state is None:
                _LOGGER.warning(
                    "Solar forecast sensor '%s' is disabled or not yet loaded",
                    forecast_sensor,
                )
                return None
            forecast = state.attributes.get("detailedHourly", None)
            if forecast is None:
                _LOGGER.warning(
                    "Solar forecast sensor '%s' has no attribute 'detailedHourly",
                    forecast_sensor,
                )
                return None
            periods.extend(forecast)

        if len(periods) == 0:
            return None

        df = pd.DataFrame.from_records(periods, index="period_start")
        df.index.rename("start", inplace=True)
        # It seems that Solcast provides half-hourly readings for today
        df = df.resample("h").sum()
        df = df.loc[this_hour : this_hour + period]  # type: ignore
        return df

    async def load_electricity_rates(self, now: datetime, period: timedelta) -> pd.DataFrame | None:
        this_hour_utc = dt.as_utc(datetime(now.year, now.month, now.day, now.hour, tzinfo=now.tzinfo))

        tariff = await self._octopus_client.get_tariff()

        # We currently work with hourly data across the board. If we need to combine two half-hours with different
        # rates, take the max
        tariff = tariff.resample("h").max()

        # Forecast might not be long enough. Fill with data 24h ago if that's the case
        extended_df = tariff.reindex(pd.date_range(tariff.iloc[0].name, this_hour_utc + period, freq="h"))  # type: ignore
        while extended_df.isnull().any().any():
            extended_df = extended_df.fillna(extended_df.shift(24))
        extended_df = extended_df.loc[this_hour_utc : this_hour_utc + period]  # type: ignore

        return extended_df
