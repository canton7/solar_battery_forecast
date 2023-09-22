import asyncio

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Config
from homeassistant.core import HomeAssistant
from homeassistant.util import dt

from .const import DOMAIN
from .controller import Controller

PLATFORMS: list[str] = ["sensor"]


async def async_setup(_hass: HomeAssistant, _config: Config) -> bool:
    """Setting up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up this integration using UI."""

    hass.data.setdefault(DOMAIN, {}).setdefault(entry.entry_id, {})

    controller = Controller(hass, entry)

    hass.data[DOMAIN][entry.entry_id]["controller"] = controller

    # Don't block this task, as it will block hacs and make it unhappy
    hass.async_create_task(controller.load(dt.now()))

    for platform in PLATFORMS:
        if entry.options.get(platform, True):
            hass.async_add_job(hass.config_entries.async_forward_entry_setup(entry, platform))

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    unloaded = all(
        await asyncio.gather(
            *[hass.config_entries.async_forward_entry_unload(entry, platform) for platform in PLATFORMS]
        )
    )

    if unloaded:
        hass.data[DOMAIN][entry.entry_id]["controller"].unload()
        hass.data[DOMAIN].pop(entry.entry_id)

    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
