from homeassistant.components.sensor import SensorEntity
from homeassistant.const import Platform

from ..brains.battery_model import ActionType
from .entity_controller import EntityController
from .entity_mixin import EntityMixin


class CurrentActionSensor(EntityMixin, SensorEntity):
    def __init__(self, controller: EntityController) -> None:
        self._controller = controller

        self._key = "current_action"
        self._attr_name = "Current Action"
        self.entity_id = self._get_entity_id(Platform.SENSOR)

    def _update(self) -> None:
        # Calculate these once, then cache
        current_action = self._controller.state.current_action
        if current_action is None:
            self._attr_native_value = None
            self._attr_extra_state_attributes = {}
        else:
            if current_action.action_type == ActionType.CHARGE:
                charge_text = "Charge"
                charge_attr = "charge"
            elif current_action.action_type == ActionType.DISCHARGE:
                charge_text = "Disharge"
                charge_attr = "discharge"
            elif current_action.action_type == ActionType.SELF_USE:
                charge_text = "Self Use"
                charge_attr = "self_use"

            min_soc = round(current_action.min_soc * 100)
            max_soc = round(current_action.max_soc * 100)

            self._attr_native_value = f"{charge_text} (Min: {min_soc}%, Max: {max_soc}%)"
            self._attr_extra_state_attributes = {"action": charge_attr, "min_soc": min_soc, "max_soc": max_soc}
