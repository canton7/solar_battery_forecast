import asyncio
import logging

from homeassistant import loader
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import Config
from homeassistant.core import CoreState
from homeassistant.core import Event
from homeassistant.core import HomeAssistant
from homeassistant.util import dt

from .const import DOMAIN
from .controller import Controller

PLATFORMS: list[str] = ["sensor", "time", "switch", "button", "number"]

_LOGGER = logging.getLogger(__name__)


async def async_setup(_hass: HomeAssistant, _config: Config) -> bool:
    """Setting up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up this integration using UI."""

    hass.data.setdefault(DOMAIN, {}).setdefault(entry.entry_id, {})

    controller = Controller(hass, entry)

    hass.data[DOMAIN][entry.entry_id]["controller"] = controller

    version = ""
    try:
        integration = await loader.async_get_integration(hass, DOMAIN)
        version = str(integration.version)
        _LOGGER.info(f"{DOMAIN} version: {version}")
    except loader.IntegrationNotFound:
        pass

    # We depend on other integrations. Give them a chance to start first
    if hass.state in [CoreState.not_running, CoreState.starting]:

        async def run(_event: Event) -> None:
            await controller.load(dt.now())

        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, run)
    else:
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
