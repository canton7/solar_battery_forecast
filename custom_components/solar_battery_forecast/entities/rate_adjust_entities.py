from datetime import time

from homeassistant.components.number import NumberEntity
from homeassistant.components.number import NumberMode
from homeassistant.components.switch import SwitchEntity
from homeassistant.components.time import TimeEntity
from homeassistant.const import Platform

from .entity_controller import EntityController
from .entity_mixin import EntityMixin


class RateAdjustStartEntity(EntityMixin, TimeEntity):
    def __init__(self, controller: EntityController) -> None:
        self._controller = controller
        self._key = "rate_adjust_start"
        self._attr_name = "Rate Adjust Start"
        self.entity_id = self._get_entity_id(Platform.TIME)

    @property
    def native_value(self) -> time | None:
        return self._controller.rate_overrides.rate_adjust_start

    async def async_set_value(self, value: time) -> None:
        self._controller.rate_overrides.rate_adjust_start = value
        self.async_write_ha_state()


class RateAdjustEndEntity(EntityMixin, TimeEntity):
    def __init__(self, controller: EntityController) -> None:
        self._controller = controller
        self._key = "rate_adjust_end"
        self._attr_name = "Rate Adjust End"
        self.entity_id = self._get_entity_id(Platform.TIME)

    @property
    def native_value(self) -> time | None:
        return self._controller.rate_overrides.rate_adjust_end

    async def async_set_value(self, value: time) -> None:
        self._controller.rate_overrides.rate_adjust_end = value
        self.async_write_ha_state()


class RateAdjustEnableEntity(EntityMixin, SwitchEntity):
    def __init__(self, controller: EntityController) -> None:
        self._controller = controller
        self._key = "rate_adjust_enable"
        self._attr_name = "Rate Adjust Enable"
        self.entity_id = self._get_entity_id(Platform.SWITCH)

    @property
    def is_on(self) -> bool | None:
        return self._controller.rate_overrides.rate_adjust_enable

    async def async_turn_on(self) -> None:
        self._controller.rate_overrides.rate_adjust_enable = True
        self.async_write_ha_state()

    async def async_turn_off(self) -> None:
        self._controller.rate_overrides.rate_adjust_enable = False
        self.async_write_ha_state()


class RateAdjustValueEntity(EntityMixin, NumberEntity):
    def __init__(self, controller: EntityController) -> None:
        self._controller = controller
        self._key = "rate_adjust_value"
        self._attr_name = "Rate Adjust Value"
        self.entity_id = self._get_entity_id(Platform.NUMBER)

        self._attr_native_min_value = 0.0
        self._attr_native_step = 0.01
        self._attr_mode = NumberMode.BOX

    @property
    def native_value(self) -> float:
        return self._controller.rate_overrides.rate_adjust_value

    async def async_set_native_value(self, value: float) -> None:
        self._controller.rate_overrides.rate_adjust_value = value
        self.async_write_ha_state()
