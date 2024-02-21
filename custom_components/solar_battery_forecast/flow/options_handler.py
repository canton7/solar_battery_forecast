from typing import Any

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from ..const import CONFIG_ENTRY_TITLE
from ..data.config import Config
from .flow_handler_mixin import FlowHandlerMixin


class OptionsHandler(FlowHandlerMixin, config_entries.OptionsFlow):
    """Options flow handler"""

    def __init__(self, config: config_entries.ConfigEntry) -> None:
        self._config = config

    async def async_step_init(
        self, _user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Start the config flow"""

        return await self.async_step_api_details(config=self._config.data)

    def save(self, config: Config) -> FlowResult:
        self.hass.config_entries.async_update_entry(
            entry=self._config,
            title=CONFIG_ENTRY_TITLE,
            data=config,
            options=self._config.options,
        )

        return self.async_create_entry(title="", data={})
