from typing import TYPE_CHECKING
from typing import Protocol

from homeassistant.const import Platform
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity import Entity

from ..const import DOMAIN
from ..const import ENTITY_ID_PREFIX
from .entity_controller import EntityController
from .entity_controller import EntityControllerSubscriber


class ModbusEntityProtocol(Protocol):
    """Protocol which types including ModbusEntityMixin must implement"""

    _controller: EntityController
    _key: str


if TYPE_CHECKING:
    _ModbusEntityMixinBase = Entity
else:
    _ModbusEntityMixinBase = object


class EntityMixinMetaclass(type(Entity), type(Protocol)):  # type: ignore
    pass


class EntityMixin(
    EntityControllerSubscriber, ModbusEntityProtocol, _ModbusEntityMixinBase, metaclass=EntityMixinMetaclass
):
    @property
    def unique_id(self) -> str:
        # TODO: DO we want to support multiple configs?
        return self._key

    def _get_entity_id(self, platform: Platform) -> str:
        return f"{platform}.{ENTITY_ID_PREFIX}{self._key}"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._controller.config_entry.entry_id)},
            name="Solar Battery Forecast",
            model=None,
            entry_type=DeviceEntryType.SERVICE,
        )

    async def async_added_to_hass(self) -> None:
        """Called when the entity is added to hass"""
        await super().async_added_to_hass()
        self._controller.subscribe(self)
        self._update()

    async def async_will_remove_from_hass(self) -> None:
        """Called when the entity is about to be removed from hass"""
        self._controller.unsubscribe(self)
        await super().async_will_remove_from_hass()

    def controller_updated(self) -> None:
        self._update()
        self.schedule_update_ha_state()

    def _update(self) -> None:
        pass

    @property
    def should_poll(self) -> bool:
        return False

    # Implement reference equality
    def __eq__(self, other: object) -> bool:
        return self is other

    def __hash__(self) -> int:
        return id(self)
