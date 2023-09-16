from typing import Any

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import CONFIG_ENTRY_TITLE
from .const import DOMAIN


class CustomFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, _user_input: dict[str, Any] | None = None) -> FlowResult:
        return self.async_create_entry(title=CONFIG_ENTRY_TITLE, data={})
