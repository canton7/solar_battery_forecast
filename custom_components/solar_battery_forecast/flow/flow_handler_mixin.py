from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING
from typing import Any
from typing import Awaitable
from typing import Callable

import voluptuous as vol
from homeassistant import data_entry_flow
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv

from ..data.user_config import UserConfig

if TYPE_CHECKING:
    _FlowHandlerMixinBase = data_entry_flow.FlowHandler
else:
    _FlowHandlerMixinBase = object


class FlowHandlerMixin(ABC, _FlowHandlerMixinBase):
    """Mixin for config flow / options flow classes, providing common functionality"""

    async def with_default_form(
        self,
        body: Callable[[dict[str, Any]], Awaitable[FlowResult | None]],
        user_input: dict[str, Any] | None,
        step_id: str,
        data_schema: vol.Schema,
        *,
        suggested_values: dict[str, Any] | None = None,
        description_placeholders: dict[str, str] | None = None,
    ) -> FlowResult:
        """
        If user_input is not None, call body() and return the result.
        If body throws a ValidationFailedException, or returns None, or user_input is None,
        show the default form specified by step_id and data_schema
        """

        errors: dict[str, str] | None = None
        if user_input is not None:
            try:
                result = await body(user_input)
                if result is not None:
                    return result
            except ValidationFailedError as ex:
                errors = ex.errors
                if ex.errors:
                    if description_placeholders is None:
                        description_placeholders = ex.error_placeholders
                    elif ex.error_placeholders is not None:
                        description_placeholders.update(ex.error_placeholders)

        schema_with_input = self.add_suggested_values_to_schema(data_schema, user_input)
        if suggested_values:
            schema_with_input = self.add_suggested_values_to_schema(schema_with_input, suggested_values)
        return self.async_show_form(
            step_id=step_id,
            data_schema=schema_with_input,
            errors=errors,
            description_placeholders=description_placeholders,
        )

    async def async_step_api_details(
        self, user_input: dict[str, Any] | None = None, config: UserConfig | None = None
    ) -> FlowResult:
        """Handle a flow initialized by the user."""

        async def body(user_input: dict[str, Any]) -> FlowResult:
            config = UserConfig(user_input)
            return self.save(config)

        schema = vol.Schema(
            {
                vol.Required("octopus_account_id"): cv.string,
                vol.Required("octopus_api_key"): cv.string,
            }
        )

        suggested_values: dict[str, Any] = config if config is not None else {}
        return await self.with_default_form(body, user_input, "api_details", schema, suggested_values=suggested_values)

    @abstractmethod
    def save(self, config: UserConfig) -> FlowResult:
        pass


class ValidationFailedError(Exception):
    """Throw to cause a validation error to be shown"""

    def __init__(
        self,
        errors: dict[str, str],
        error_placeholders: dict[str, str] | None = None,
    ) -> None:
        self.errors = errors
        self.error_placeholders = error_placeholders
