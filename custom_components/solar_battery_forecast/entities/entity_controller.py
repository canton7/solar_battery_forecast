from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime

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


class EntityController(ABC):
    @property
    @abstractmethod
    def config_entry(self) -> ConfigEntry:
        pass

    @property
    @abstractmethod
    def state(self) -> EntityControllerState:
        pass

    @abstractmethod
    def subscribe(self, subscriber: EntityControllerSubscriber) -> None:
        pass

    @abstractmethod
    def unsubscribe(self, subscriber: EntityControllerSubscriber) -> None:
        pass
