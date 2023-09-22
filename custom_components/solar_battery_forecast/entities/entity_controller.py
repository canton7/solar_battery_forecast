from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass

import pandas as pd
from homeassistant.config_entries import ConfigEntry


class EntityControllerSubscriber(ABC):
    @abstractmethod
    def controller_updated(self) -> None:
        pass


@dataclass
class EntityControllerState:
    load_today: pd.DataFrame | None = None
    load_forecast: pd.DataFrame | None = None
    initial_load_forecast: pd.DataFrame | None = None
    solar_forecast: pd.DataFrame | None = None
    electricity_rates: pd.DataFrame | None = None


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
