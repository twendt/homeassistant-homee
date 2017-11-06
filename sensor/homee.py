"""
Support for Homee sensors.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/sensor.homee/
"""
import logging

from homeassistant.const import (
    TEMP_CELSIUS, TEMP_FAHRENHEIT)
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import ENTITY_ID_FORMAT
from custom_components.homee import (
    HOMEE_NODES, HOMEE_ATTRIBUTES, HOMEE_CUBE, HomeeDevice)

DEPENDENCIES = ['homee']

_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Perform the setup for Vera controller devices."""
    devices = []
    for attribute in HOMEE_ATTRIBUTES['sensor']:
        devices.append(HomeeSensor(HOMEE_NODES[attribute.node_id], attribute, HOMEE_CUBE))
    add_devices(devices)

class HomeeSensor(HomeeDevice, Entity):
    """Representation of a Homee Sensor."""

    def __init__(self, homee_node, homee_attribute, cube):
        """Initialize the sensor."""
        self.current_value = homee_attribute.value
        self.attribute_id = homee_attribute.id
        self._temperature_units = None
        HomeeDevice.__init__(self, homee_node, homee_attribute, cube)
        self.entity_id = ENTITY_ID_FORMAT.format(self.homee_id)
        self.update_state(homee_attribute)

    @property
    def state(self):
        """Return the name of the sensor."""
        return self.current_value

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        pass
#        if self.vera_device.category == "Temperature Sensor":
#            return self._temperature_units
#        elif self.vera_device.category == "Light Sensor":
#            return 'lux'
#        elif self.vera_device.category == "Humidity Sensor":
#            return '%'

    def update_state(self, attribute):
        """Update the state."""
        if self.attribute_id == attribute.id:
            self.current_value = attribute.value
