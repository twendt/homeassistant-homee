"""
Support for Homee sensors.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/sensor.homee/
"""
import logging

from homeassistant.components.light import (
    ATTR_BRIGHTNESS, ATTR_RGB_COLOR, ENTITY_ID_FORMAT,
    SUPPORT_BRIGHTNESS, SUPPORT_RGB_COLOR, Light)
from homeassistant.const import (STATE_OFF, STATE_ON)
from custom_components.homee import (
    HOMEE_NODES, HOMEE_ATTRIBUTES, HOMEE_CUBE, HomeeDevice)
from custom_components.homee.util import get_attr_by_type

DEPENDENCIES = ['homee']

_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Perform the setup for Vera controller devices."""
    devices = []
    for attribute in HOMEE_ATTRIBUTES['light']:
        devices.append(HomeeLight(HOMEE_NODES[attribute.node_id], attribute, HOMEE_CUBE))
    add_devices(devices)

class HomeeLight(HomeeDevice, Light):
    """Representation of a Homee Light."""

    def __init__(self, homee_node, homee_attribute, cube):
        """Initialize the switch."""
        from pyhomee import const
        self._state = homee_attribute.value
        self._color = None
        self.brightness_attr = get_attr_by_type(homee_node, const.BRIGHTNESS)
        if self.brightness_attr:
            self._brightness = self.brightness_attr.value
        else:
            self._brightness = None
        self.attribute_id = homee_attribute.id
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
        elif self.brightness_attr.id == attribute.id:
            self._brightness = (attribute.value /100) *255
            if attribute.value > 0:
                self._state = True
            else:
                self._state = False

    def turn_on(self, **kwargs):
        """Turn device on."""
        #if ATTR_RGB_COLOR in kwargs and self._color:
        #    self.vera_device.set_color(kwargs[ATTR_RGB_COLOR])
        if ATTR_BRIGHTNESS in kwargs and self.brightness_attr:
            self.cube.send_node_command(self.homee_node, self.brightness_attr, (kwargs[ATTR_BRIGHTNESS] / 255)*100)
        else:
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

    @property
    def brightness(self):
        """Return the brightness of the light."""
        return self._brightness

    @property
    def rgb_color(self):
        """Return the color of the light."""
        return self._color

    @property
    def supported_features(self):
        """Flag supported features."""
        if self._color:
            return SUPPORT_BRIGHTNESS | SUPPORT_RGB_COLOR
        return SUPPORT_BRIGHTNESS

