from typing import Any

import pandas as pd
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .brains import load_forecaster
from .const import DOMAIN
from .controller import Controller
from .data.diagnostic_data import DiagnosticData


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: ConfigEntry) -> dict[str, Any]:
    controller: Controller = hass.data[DOMAIN][entry.entry_id]["controller"]

    def serialize(df: pd.DataFrame | None) -> Any:
        if df is None:
            return None
        # Annoyingly, to_dict leads Timestamp object, which can't be json'd by default
        if isinstance(df.index, pd.DatetimeIndex):
            return {index.isoformat(): series.to_dict() for index, series in df.iterrows()}  # type: ignore
        return df.to_dict(orient="index")

    state = controller.state

    soc = controller.data_source.get_soc()
    load_history = (
        await controller.data_source.load_sensor_history(state.last_update, load_forecaster.TRAIN_PERIOD)
        if state.last_update is not None
        else None
    )

    data = DiagnosticData(
        soc=soc,
        load_history=serialize(load_history),
        initial_load_forecast=serialize(state.initial_load_forecast),
        load_forecast=serialize(state.load_forecast),
        solar_forecast=serialize(state.solar_forecast),
        electricity_rates=serialize(state.electricity_rates),
    )
    return data  # type: ignore
