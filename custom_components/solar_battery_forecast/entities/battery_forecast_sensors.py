from abc import ABC
from abc import abstractmethod
from datetime import datetime
from datetime import timedelta
from typing import Any
from typing import MutableMapping

import pandas as pd
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.sensor.const import SensorDeviceClass
from homeassistant.components.sensor.const import SensorStateClass
from homeassistant.const import Platform
from homeassistant.util import dt

from .entity_controller import EntityController
from .entity_mixin import EntityMixin


class BatteryForecastSensorBase(EntityMixin, SensorEntity, ABC):
    def __init__(self, controller: EntityController) -> None:
        self._controller = controller

        self._attr_device_class = SensorDeviceClass.BATTERY
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = "%"

    @abstractmethod
    def _get_battery_forecast(self) -> pd.DataFrame | None:
        pass

    def _get_native_value(self) -> float | None:
        battery_forecast = self._get_battery_forecast()
        if battery_forecast is None:
            return None

        now = dt.now()
        midnight_today = datetime(now.year, now.month, now.day, 0, 0, 0, tzinfo=now.tzinfo) + timedelta(days=1)

        return battery_forecast.loc[midnight_today, "battery_soc"]  # type: ignore

    def _update(self) -> None:
        # Calculate these once, then cache
        self._attr_native_value = self._get_native_value()
        self._attr_extra_state_attributes = self._get_extra_state_attributes()

    def _get_extra_state_attributes(self) -> MutableMapping[str, Any]:
        battery_forecast = self._get_battery_forecast()
        if battery_forecast is None:
            return {"forecast": []}

        return {
            "forecast": [
                {
                    "start": x.Index.isoformat(),
                    "soc": x.battery_soc,
                    "feed_in_kwh": x.feed_in_kwh,
                    "import_kwh": x.import_kwh,
                }
                for x in battery_forecast.itertuples()
            ]
        }


class BatteryForecastSensor(BatteryForecastSensorBase):
    def __init__(self, controller: EntityController) -> None:
        super().__init__(controller)

        self._key = "battery_forecast"
        self._attr_name = "Battery Forecast"
        self.entity_id = self._get_entity_id(Platform.SENSOR)

    def _get_battery_forecast(self) -> pd.DataFrame | None:
        return self._controller.state.battery_forecast


class InitialBatteryForecastSensor(BatteryForecastSensorBase):
    def __init__(self, controller: EntityController) -> None:
        super().__init__(controller)

        self._key = "battery_forecast_midnight"
        self._attr_name = "Battery Forecast (Midnight)"
        self.entity_id = self._get_entity_id(Platform.SENSOR)

    def _get_battery_forecast(self) -> pd.DataFrame | None:
        return self._controller.state.initial_battery_forecast
