import logging
from datetime import timezone

import numpy as np
import pandas as pd
from homeassistant.components import recorder
from homeassistant.components.recorder import statistics
from homeassistant.core import HomeAssistant
from homeassistant.util import dt

from . import load_forecaster
from .load_forecaster import LoadForecaster

_LOGGER = logging.getLogger(__name__)


class Controller:
    def __init__(self, hass: HomeAssistant) -> None:
        self._hass = hass
        self._load_forecaster = LoadForecaster()
        self._load_power_sensor = "sensor.load_power"

    async def load(self) -> None:
        start = dt.now(timezone.utc) - load_forecaster.TRAIN_PERIOD

        stats = await recorder.get_instance(self._hass).async_add_executor_job(
            statistics.statistics_during_period,
            self._hass,
            start,
            None,
            {self._load_power_sensor},
            "hour",
            None,
            {"mean"},
        )
        records = (
            {
                "start": dt.as_local(dt.utc_from_timestamp(x["start"])),
                "mean": x["mean"] if x["mean"] not in (None, "", "unknown", "unavailable") else np.nan,
            }
            for x in stats[self._load_power_sensor]
        )
        df = pd.DataFrame.from_records(records, index="start")
        df = df.asfreq(freq="H")
        df.interpolate(inplace=True)

        forecast = self._load_forecaster.predict(df)
        print(forecast)

    def unload(self) -> None:
        pass
