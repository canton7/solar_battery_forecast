from homeassistant.core import HomeAssistant


class Controller:
    def __init__(self, hass: HomeAssistant) -> None:
        self._hass = hass

    def unload(self) -> None:
        pass
