from typing import Any

import pandas as pd
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .controller import Controller


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: ConfigEntry) -> dict[str, Any]:
    controller: Controller = hass.data[DOMAIN][entry.entry_id]["controller"]

    def serialize(df: pd.DataFrame | None) -> Any:
        if df is None:
            return None
        # TODO: This does not include the index
        return df.to_dict(orient="index")

    state = controller.state
    return {
        "initial_load_forecast": serialize(state.initial_load_forecast),
        "load_forecast": serialize(state.load_forecast),
        "solar_forecast": serialize(state.solar_forecast),
        "electricity_rates": serialize(state.electricity_rates),
    }
