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

from .main_config import MainConfig

_LOGGER = logging.getLogger(__name__)


class DataSource:
    def __init__(self, hass: HomeAssistant, config: MainConfig) -> None:
        self._hass = hass
        self._load_power_sum_sensor = config["load_power_sum_sensor"]

    async def load_sensor_history(self, period: timedelta) -> pd.DataFrame | None:
        now = dt.now(timezone.utc)
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

        this_hour = datetime(now.year, now.month, now.day, now.hour, tzinfo=timezone.utc)
        start_of_last_hour = this_hour - timedelta(hours=1)

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
                        "value": stat_sum - prev_sum if stat_sum is not None else np.nan,
                    }
                    if stat_sum is not None:
                        prev_sum = stat_sum

            df = pd.DataFrame.from_records(get_records(), index="start")
            # Make sure that any missing values at the end are filled with nan
            df = df.reindex(
                pd.date_range(start=df.iloc[0].name, end=dt.as_local(start_of_last_hour), freq="H"),  # type: ignore
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
