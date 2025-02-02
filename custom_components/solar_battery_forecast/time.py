from homeassistant.config_entries import ConfigEntry  # noqa: A005
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .controller import Controller
from .entities.rate_adjust_entities import RateAdjustEndEntity
from .entities.rate_adjust_entities import RateAdjustStartEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    controller: Controller = hass.data[DOMAIN][entry.entry_id]["controller"]

    async_add_entities([RateAdjustStartEntity(controller), RateAdjustEndEntity(controller)])
