import logging
from datetime import timezone

import numpy as np
import pandas as pd
from homeassistant.components import recorder
from homeassistant.components.recorder import statistics
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.util import dt

from . import load_forecaster
from .entities.entity_controller import EntityController
from .entities.entity_controller import EntityControllerSubscriber
from .load_forecaster import LoadForecaster

_LOGGER = logging.getLogger(__name__)


class Controller(EntityController):
    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        self._hass = hass
        self._config_entry = config_entry

        self._entities: set[EntityControllerSubscriber] = set()
        self._load_forecaster = LoadForecaster()
        self._load_power_sensor = "sensor.load_power"

        self._load_forecast: pd.DataFrame | None = None

    @property
    def load_forecast(self) -> pd.DataFrame | None:
        return self._load_forecast

    @property
    def config_entry(self) -> ConfigEntry:
        return self._config_entry

    async def load(self) -> None:
        self._load_forecast = await self._create_load_forecast()
        self._update_entities()

    async def _create_load_forecast(self) -> pd.DataFrame | None:
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

        if self._load_power_sensor not in stats:
            _LOGGER.warning("Unable to find history for sensor '%s'. Is this sensor correct?", self._load_power_sensor)
            return None

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
        return forecast

    def unload(self) -> None:
        pass

    def _update_entities(self) -> None:
        for entity in self._entities:
            entity.controller_updated()

    def subscribe(self, subscriber: EntityControllerSubscriber) -> None:
        self._entities.add(subscriber)

    def unsubscribe(self, subscriber: EntityControllerSubscriber) -> None:
        self._entities.remove(subscriber)
