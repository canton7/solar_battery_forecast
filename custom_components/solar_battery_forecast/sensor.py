from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .controller import Controller
from .entities.battery_forecast_sensors import BatteryForecastSensor
from .entities.battery_forecast_sensors import InitialBatteryForecastSensor
from .entities.current_action_sensor import CurrentActionSensor
from .entities.load_forecast_sensors import InitialLoadForecastSensor
from .entities.load_forecast_sensors import LoadForecastSensor


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_devices: AddEntitiesCallback) -> None:
    controller: Controller = hass.data[DOMAIN][entry.entry_id]["controller"]

    async_add_devices(
        [
            LoadForecastSensor(controller),
            InitialLoadForecastSensor(controller),
            CurrentActionSensor(controller),
            BatteryForecastSensor(controller),
            InitialBatteryForecastSensor(controller),
        ]
    )
