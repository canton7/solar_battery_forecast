from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import MutableMapping

import pandas as pd
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.sensor.const import SensorDeviceClass
from homeassistant.components.sensor.const import SensorStateClass
from homeassistant.const import Platform

from .entity_controller import EntityController
from .entity_mixin import EntityMixin


class LoadForecastSensorBase(EntityMixin, SensorEntity, ABC):
    def __init__(self, controller: EntityController) -> None:
        self._controller = controller

        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = "kWh"

    @abstractmethod
    def _get_load_forecast(self) -> pd.DataFrame | None:
        pass

    @abstractmethod
    def _get_native_value(self) -> float | None:
        pass

    def _update(self) -> None:
        # Calculate these once, then cache
        self._attr_native_value = self._get_native_value()
        self._attr_extra_state_attributes = self._get_extra_state_attributes()

    def _get_extra_state_attributes(self) -> MutableMapping[str, Any]:
        load_forecast = self._get_load_forecast()
        if load_forecast is None:
            return {"forecast": []}

        return {
            "forecast": [
                {
                    "start": x.Index.isoformat(),
                    "predicted": x.predicted,
                    "upper": x.predicted_upper,
                    "lower": x.predicted_lower,
                }
                for x in load_forecast.round(2).itertuples()
            ]
        }


class LoadForecastSensor(LoadForecastSensorBase):
    def __init__(self, controller: EntityController) -> None:
        super().__init__(controller)

        self._key = "load_forecast"
        self._attr_name = "Load Forecast"
        self.entity_id = self._get_entity_id(Platform.SENSOR)

    def _get_load_forecast(self) -> pd.DataFrame | None:
        return self._controller.state.load_forecast

    def _get_native_value(self) -> float | None:
        load_forecast = self._controller.state.load_forecast
        load_today = self._controller.state.load_today
        if load_forecast is None or load_today is None:
            return None

        sum_today: float = round(load_today.sum()["value"] + load_forecast.resample("D").sum().iloc[0]["predicted"], 2)
        return sum_today


class InitialLoadForecastSensor(LoadForecastSensorBase):
    def __init__(self, controller: EntityController) -> None:
        super().__init__(controller)

        self._key = "load_forecast_midnight"
        self._attr_name = "Load Forecast (Midnight)"
        self.entity_id = self._get_entity_id(Platform.SENSOR)

    def _get_load_forecast(self) -> pd.DataFrame | None:
        return self._controller.state.initial_load_forecast

    def _get_native_value(self) -> float | None:
        load_forecast = self._controller.state.initial_load_forecast
        if load_forecast is None:
            return None

        sum_today: float = round(load_forecast.resample("D").sum().iloc[0]["predicted"], 2)
        return sum_today
