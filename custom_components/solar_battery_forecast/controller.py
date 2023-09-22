import logging
from datetime import datetime
from datetime import timedelta
from typing import Callable

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_change
from homeassistant.util import dt

from .brains import load_forecaster
from .brains.load_forecaster import LoadForecaster
from .data_source import DataSource
from .entities.entity_controller import EntityController
from .entities.entity_controller import EntityControllerState
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

        self._state = EntityControllerState()

        async def _refresh(datetime: datetime) -> None:
            # Create a new initial forecast at midnight
            await self.load(datetime)

        self._unload.append(async_track_time_change(self._hass, _refresh, minute=5, second=0))

    @property
    def state(self) -> EntityControllerState:
        return self._state

    @property
    def config_entry(self) -> ConfigEntry:
        return self._config_entry

    async def load(self, now: datetime) -> None:
        _LOGGER.info("Reloading forecasts")
        await self._create_load_forecast(now)
        self._update_entities()

    async def _create_load_forecast(self, now: datetime) -> None:
        now = dt.as_local(now)
        midnight = datetime(now.year, now.month, now.day, tzinfo=now.tzinfo)

        load_history = await self._data_source.load_sensor_history(load_forecaster.TRAIN_PERIOD)
        self._state.load_today = load_history[midnight:]  # type: ignore

        is_midnight = now.hour == 0
        if load_history is not None:
            self._state.load_forecast = await self._hass.async_add_executor_job(
                self._load_forecaster.predict, load_history
            )
            if is_midnight:
                self._state.initial_load_forecast = self._state.load_forecast
            elif self._state.initial_load_forecast is None:
                # If we never stored an initial forecast, re-calculate one from data up to midnight
                load_history_to_midnight = load_history.loc[: midnight - timedelta(hours=1)].copy()  # type: ignore
                self._state.initial_load_forecast = await self._hass.async_add_executor_job(
                    self._load_forecaster.predict, load_history_to_midnight
                )

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
