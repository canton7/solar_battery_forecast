from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .controller import Controller
from .entities.update_button_entity import UpdateButtonEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback) -> None:
    controller: Controller = hass.data[DOMAIN][entry.entry_id]["controller"]

    async_add_devices(
        [
            UpdateButtonEntity(controller),
        ]
    )
