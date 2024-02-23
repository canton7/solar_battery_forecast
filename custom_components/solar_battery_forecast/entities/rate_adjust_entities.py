import datetime

from homeassistant.components.switch import SwitchEntity
from homeassistant.components.time import TimeEntity
from homeassistant.const import Platform

from .entity_controller import EntityController
from .entity_mixin import EntityMixin


class ImportAdjustStartEntity(EntityMixin, TimeEntity):
    def __init__(self, controller: EntityController) -> None:
        self._controller = controller
        self._key = "import_adjust_start"
        self._attr_name = "Import Adjust Start"
        self.entity_id = self._get_entity_id(Platform.TIME)

        self._attr_native_value = datetime.time(0, 0, 0)


class ImportAdjustEndEntity(EntityMixin, TimeEntity):
    def __init__(self, controller: EntityController) -> None:
        self._controller = controller
        self._key = "import_adjust_end"
        self._attr_name = "Import Adjust End"
        self.entity_id = self._get_entity_id(Platform.TIME)

        self._attr_native_value = datetime.time(0, 0, 0)


class ImportAdjustEnableEntity(EntityMixin, SwitchEntity):
    def __init__(self, controller: EntityController) -> None:
        self._controller = controller
        self._key = "import_adjust_enable"
        self._attr_name = "Import Adjust Enable"
        self.entity_id = self._get_entity_id(Platform.SWITCH)

    async def async_turn_on(self) -> None:
        """Turn the entity on."""

    async def async_turn_off(self) -> None:
        """Turn the entity off."""
