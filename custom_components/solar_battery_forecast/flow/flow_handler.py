from typing import Any

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from ..const import CONFIG_ENTRY_TITLE
from ..const import DOMAIN
from ..data.config import Config
from .flow_handler_mixin import FlowHandlerMixin
from .options_handler import OptionsHandler


class FlowHandler(FlowHandlerMixin, config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, _user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle a flow initialized by the user."""

        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        return await self.async_step_api_details()

    def save(self, config: Config) -> FlowResult:
        return self.async_create_entry(title=CONFIG_ENTRY_TITLE, data=config)

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return OptionsHandler(config_entry)
