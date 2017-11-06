"""
Support for Homee sensors.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/sensor.homee/
"""
import logging

from homeassistant.helpers.entity import Entity
from homeassistant.components.switch import ENTITY_ID_FORMAT, SwitchDevice
from homeassistant.const import (STATE_OFF, STATE_ON)
from custom_components.homee import (
    HOMEE_NODES, HOMEE_ATTRIBUTES, HOMEE_CUBE, HomeeDevice)

DEPENDENCIES = ['homee']

_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Perform the setup for Vera controller devices."""
    devices = []
    for attribute in HOMEE_ATTRIBUTES['switch']:
        devices.append(HomeeSwitch(HOMEE_NODES[attribute.node_id], attribute, HOMEE_CUBE))
    add_devices(devices)

class HomeeSwitch(HomeeDevice, SwitchDevice):
    """Representation of a Homee Switch."""

    def __init__(self, homee_node, homee_attribute, cube):
        """Initialize the switch."""
        self._state = homee_attribute.value
        self.attribute_id = homee_attribute.id
        self._temperature_units = None
        HomeeDevice.__init__(self, homee_node, homee_attribute, cube)
        self.entity_id = ENTITY_ID_FORMAT.format(self.homee_id)
        self.update_state(homee_attribute)

    def update_state(self, attribute):
        """Update the state."""
        if self.attribute_id == attribute.id:
            _LOGGER.info("Attribute value: %s", attribute.value)
            if int(attribute.value) == 1:
                self._state = True
            else:
                self._state = False

    def turn_on(self, **kwargs):
        """Turn device on."""
        self.cube.send_node_command(self.homee_node, self.homee_attribute, 1)
        #self._state = STATE_ON
        #self.schedule_update_ha_state()

    def turn_off(self, **kwargs):
        """Turn device off."""
        self.cube.send_node_command(self.homee_node, self.homee_attribute, 0)
        #self._state = STATE_OFF
        #self.schedule_update_ha_state()

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._state

