from typing import Any
from typing import Mapping

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.sensor.const import SensorDeviceClass
from homeassistant.components.sensor.const import SensorStateClass
from homeassistant.const import Platform

from .entity_controller import EntityController
from .entity_mixin import EntityMixin


class LoadForecastSensor(EntityMixin, SensorEntity):
    def __init__(self, controller: EntityController) -> None:
        self._controller = controller

        self._key = "load_forecast"
        self._attr_name = "Load Forecast"
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = "kWh"

        self.entity_id = self._get_entity_id(Platform.SENSOR)

    @property
    def native_value(self) -> float | None:
        load_forecast = self._controller.load_forecast
        if load_forecast is None:
            return None

        sum_today: float = load_forecast.resample("D").sum().iloc[0]["predicted"]
        return sum_today

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        load_forecast = self._controller.load_forecast
        if load_forecast is None:
            return None

        return {
            "forecast": [
                {
                    "start": x.Index.isoformat(),
                    "predicted": x.predicted,
                    "upper": x.predicted_upper,
                    "lower": x.predicted_lower,
                }
                for x in load_forecast.itertuples()
            ]
        }
