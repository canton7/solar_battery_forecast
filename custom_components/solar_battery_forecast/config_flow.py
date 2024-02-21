from .const import DOMAIN
from .flow.flow_handler import FlowHandler


class CustomFlowHandler(FlowHandler, domain=DOMAIN):
    pass
