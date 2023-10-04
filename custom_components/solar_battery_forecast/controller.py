import logging
from datetime import datetime
from datetime import timedelta
from typing import Callable

import pandas as pd
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_change
from homeassistant.util import dt

from .brains import load_forecaster
from .brains.battery_model import BATTERY_CAPACITY
from .brains.battery_model import BatteryModel
from .brains.battery_model import TimeSegment
from .brains.load_forecaster import LoadForecaster
from .data.data_source import DataSource
from .data.hass_data_source import HassDataSource
from .entities.entity_controller import EntityController
from .entities.entity_controller import EntityControllerState
from .entities.entity_controller import EntityControllerSubscriber
from .main_config import MainConfig

_LOGGER = logging.getLogger(__name__)

CONFIG = MainConfig(
    load_power_sum_sensor="sensor.load_energy_today",
    soc_sensor="sensor.battery_soc",
    solar_forecast_today_sensor="sensor.solcast_pv_forecast_forecast_today",
    solar_forecast_tomorrow_sensor="sensor.solcast_pv_forecast_forecast_tomorrow",
    solar_forecast_d3_sensor="sensor.solcast_pv_forecast_forecast_day_3",
    electricity_import_rate_sensor="sensor.octopus_energy_electricity_current_rate",
    electricity_feed_in_rate_sensor="sensor.octopus_energy_electricity_export_current_rate",
)


class Controller(EntityController):
    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        self._hass = hass
        self._config_entry = config_entry

        self._entities: set[EntityControllerSubscriber] = set()
        self._unload: list[Callable[[], None]] = []

        self.data_source: DataSource = HassDataSource(hass, CONFIG)
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
        now = dt.as_local(now)
        self._state.last_update = now
        await self._create_load_forecast(now)
        self.state.solar_forecast = self.data_source.load_solar_forecast(now, load_forecaster.PREDICTION_PERIOD)
        self.state.electricity_rates = self.data_source.load_electricity_rates(now, load_forecaster.PREDICTION_PERIOD)
        await self._run_model(now)
        self._update_entities()

    async def _create_load_forecast(self, now: datetime) -> None:
        midnight = datetime(now.year, now.month, now.day, tzinfo=now.tzinfo)

        load_history = await self.data_source.load_sensor_history(now, load_forecaster.TRAIN_PERIOD)

        self._state.load_today = None
        self._state.load_forecast = None
        self._state.initial_load_forecast = None

        is_midnight = now.hour == 0
        if load_history is not None:
            self._state.load_today = load_history[midnight:]  # type: ignore

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

    async def _run_model(self, now: datetime) -> None:
        now = dt.as_local(now)
        start = datetime(now.year, now.month, now.day, now.hour, tzinfo=now.tzinfo)

        # TODO: This probably wants to be soc at the start of the hour, in case we're run at a different point?
        soc = self.data_source.get_soc()
        if (
            soc is None
            or self._state.electricity_rates is None
            or self._state.load_forecast is None
            or self._state.solar_forecast is None
        ):
            self._state.current_action = None
            self._state.battery_forecast = None
            return

        df = self._state.electricity_rates.combine_first(self._state.load_forecast).combine_first(
            self._state.solar_forecast
        )
        df = df[start : start + load_forecaster.PREDICTION_PERIOD]  # type: ignore

        # If there's missing data, backfill from 24h prior
        # TODO: What if the data 24h prior is missing? Currently this is only affecting tariffs > end of tomorrow, so
        # it isn't an issue...
        df = df.fillna(df.shift(24))
        df = df.tz_convert(tz=now.tzinfo)

        segments = [
            TimeSegment(
                generation=x.pv_estimate,
                consumption=x.predicted,
                feed_in_tariff=x.feed_in_tariff,
                import_tariff=x.import_tariff,
            )
            for x in df.itertuples(index=False)
        ]

        initial_battery = soc * BATTERY_CAPACITY / 100
        battery_model = BatteryModel(initial_battery=initial_battery)
        actions, outputs = await self._hass.async_add_executor_job(battery_model.shotgun_hillclimb, segments)
        self._state.current_action = actions[0]
        self._state.battery_forecast = pd.DataFrame((vars(x) for x in outputs.segments), index=df.index)

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
