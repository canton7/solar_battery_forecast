from homeassistant.components.button import ButtonEntity
from homeassistant.const import Platform

from .entity_controller import EntityController
from .entity_mixin import EntityMixin


class UpdateButtonEntity(EntityMixin, ButtonEntity):
    def __init__(self, controller: EntityController) -> None:
        self._controller = controller
        self._key = "reload_button"
        self._attr_name = "Reload"
        self.entity_id = self._get_entity_id(Platform.BUTTON)

    async def async_press(self) -> None:
        await self._controller.reload()
