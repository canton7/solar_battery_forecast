from abc import ABC
from abc import abstractmethod

import pandas as pd
from homeassistant.config_entries import ConfigEntry


class EntityControllerSubscriber(ABC):
    @abstractmethod
    def controller_updated(self) -> None:
        pass


class EntityController(ABC):
    @property
    @abstractmethod
    def config_entry(self) -> ConfigEntry:
        pass

    @property
    @abstractmethod
    def load_forecast(self) -> pd.DataFrame | None:
        pass

    @abstractmethod
    def subscribe(self, subscriber: EntityControllerSubscriber) -> None:
        pass

    @abstractmethod
    def unsubscribe(self, subscriber: EntityControllerSubscriber) -> None:
        pass
