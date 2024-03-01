from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from datetime import time

import pandas as pd
from homeassistant.config_entries import ConfigEntry

from ..brains.battery_model import Action


class EntityControllerSubscriber(ABC):
    @abstractmethod
    def controller_updated(self) -> None:
        pass


@dataclass
class EntityControllerState:
    last_update: datetime | None = None
    load_today: pd.DataFrame | None = None
    """The load from midnight until now"""

    load_forecast: pd.DataFrame | None = None
    """Load prediction from now for PREDICTION_PERIOD"""

    initial_load_forecast: pd.DataFrame | None = None
    """Load prediction calculated at midnight for PREDICTION_PERIOD"""

    solar_forecast: pd.DataFrame | None = None
    """The solar forcast from now for PREDICTION_PERIOD"""

    electricity_rates: pd.DataFrame | None = None
    """The electricity rates from now for PREDICTION_PERIOD"""

    current_action: Action | None = None
    """The battery action for this hour"""

    battery_forecast: pd.DataFrame | None = None
    """The battery forecast from now"""

    initial_battery_forecast: pd.DataFrame | None = None
    """The battery forecast calculated at midnight"""


def _midnight() -> time:
    return time(0, 0, 0)


@dataclass
class RateOverrides:
    rate_adjust_enable: bool = False
    rate_adjust_start: time = field(default_factory=_midnight)
    rate_adjust_end: time = field(default_factory=_midnight)
    rate_adjust_value: float = 0.0


class EntityController(ABC):
    @property
    @abstractmethod
    def config_entry(self) -> ConfigEntry:
        pass

    @property
    @abstractmethod
    def state(self) -> EntityControllerState:
        pass

    @property
    @abstractmethod
    def rate_overrides(self) -> RateOverrides:
        pass

    @abstractmethod
    async def reload(self) -> None:
        pass

    @abstractmethod
    def subscribe(self, subscriber: EntityControllerSubscriber) -> None:
        pass

    @abstractmethod
    def unsubscribe(self, subscriber: EntityControllerSubscriber) -> None:
        pass
