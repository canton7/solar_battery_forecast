import logging
from datetime import datetime
from typing import Callable

import pandas as pd
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_change

from .brains import load_forecaster
from .brains.load_forecaster import LoadForecaster
from .data_source import DataSource
from .entities.entity_controller import EntityController
from .entities.entity_controller import EntityControllerSubscriber
from .main_config import MainConfig

_LOGGER = logging.getLogger(__name__)

CONFIG = MainConfig(load_power_sum_sensor="sensor.load_energy_today")


class Controller(EntityController):
    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        self._hass = hass
        self._config_entry = config_entry

        self._entities: set[EntityControllerSubscriber] = set()
        self._unload: list[Callable[[], None]] = []

        self._data_source = DataSource(hass, CONFIG)
        self._load_forecaster = LoadForecaster()

        self._load_forecast: pd.DataFrame | None = None

        async def _refresh(_datetime: datetime) -> None:
            await self.load()

        self._unload.append(async_track_time_change(self._hass, _refresh, minute=0, second=0))

    @property
    def load_forecast(self) -> pd.DataFrame | None:
        return self._load_forecast

    @property
    def config_entry(self) -> ConfigEntry:
        return self._config_entry

    async def load(self) -> None:
        _LOGGER.info("Reloading forecasts")
        self._load_forecast = await self._create_load_forecast()
        self._update_entities()

    async def _create_load_forecast(self) -> pd.DataFrame | None:
        df = await self._data_source.load_sensor_history(load_forecaster.TRAIN_PERIOD)

        if df is None:
            return None

        forecast = self._load_forecaster.predict(df)
        return forecast

    def unload(self) -> None:
        for u in self._unload:
            u()

    def _update_entities(self) -> None:
        for entity in self._entities:
            entity.controller_updated()

    def subscribe(self, subscriber: EntityControllerSubscriber) -> None:
        self._entities.add(subscriber)

    def unsubscribe(self, subscriber: EntityControllerSubscriber) -> None:
        self._entities.remove(subscriber)
