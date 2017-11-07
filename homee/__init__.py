"""
Support for Homee

For more details about this component, please refer to the documentation at
https://home-assistant.io/components/homee/
"""
import logging
from collections import defaultdict

import voluptuous as vol

from requests.exceptions import RequestException

from homeassistant.util.dt import utc_from_timestamp
from homeassistant.util import (convert, slugify)
from homeassistant.helpers import discovery
from homeassistant.helpers import config_validation as cv
from homeassistant.const import (
    ATTR_ARMED, ATTR_BATTERY_LEVEL, ATTR_LAST_TRIP_TIME, ATTR_TRIPPED,
    EVENT_HOMEASSISTANT_STOP)
from homeassistant.helpers.entity import Entity
from custom_components.homee.util import get_attr_by_type

REQUIREMENTS = ['https://github.com/twendt/pyhomee/archive/master.zip#pyhomee==0.0.2']

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'homee'

HOMEE_CUBE = None

CONF_CUBE = 'cube'
CONF_USERNAME = 'username'
CONF_PASSWORD = 'password'

HOMEE_ID_FORMAT = '{}_{}_{}_{}'

HOMEE_NODES = {}
HOMEE_ATTRIBUTES = defaultdict(list)

HOMEE_IMPORT_GROUP = 'HASS'

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_CUBE): cv.string,
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
    }),
}, extra=vol.ALLOW_EXTRA)

HOMEE_COMPONENTS = [
    'sensor', 'switch', 'light', 'cover'
]

SERVICE_PLAY_HOMEEGRAM = 'play_homeegram'
SERVICE_DESCRIPTIONS = {
    "play_homeegram": {
        "description": "Play Homeegram",
        "fields": {
            "homeegram_id": {
                "description": "The homeegram id",
                "example": "27",
            },
        },
    },
}

# pylint: disable=unused-argument, too-many-function-args
def setup(hass, base_config):
    """Set up for Vera devices."""
    global HOMEE_CUBE
    from pyhomee import HomeeCube
    from pyhomee import const

    def stop_subscription(event):
        """Shutdown Homee subscriptions and subscription thread on exit."""
        _LOGGER.info("Shutting down subscriptions")
        HOMEE_CUBE.stop()

    def play_homeegram(call):
        id = call.data.get("homeegram_id")
        HOMEE_CUBE.play_homeegram(id)
    

    config = base_config.get(DOMAIN)

    # Get Homee specific configuration.
    hostname = config.get(CONF_CUBE)
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)

    # Initialize the Homee Cube
    HOMEE_CUBE = HomeeCube(hostname, username, password)
    hass.bus.listen_once(EVENT_HOMEASSISTANT_STOP, stop_subscription)

    hass.services.register(DOMAIN, SERVICE_PLAY_HOMEEGRAM, play_homeegram,
                      description=SERVICE_DESCRIPTIONS.get(SERVICE_PLAY_HOMEEGRAM))

    try:
        all_nodes = HOMEE_CUBE.get_nodes()
    except RequestException:
        # There was a network related error connecting to the Vera controller.
        _LOGGER.exception("Error communicating with Homee")
        return False

    group = HOMEE_CUBE.get_group_by_name(HOMEE_IMPORT_GROUP)
    if group:
        group_node_ids = HOMEE_CUBE.get_group_node_ids(group.id)
        nodes = [ node for node in all_nodes if node.id in group_node_ids ]
    else:
        nodes = all_nodes

    for node in nodes:
        if node.id == -1:
            continue
        HOMEE_NODES[node.id] = node
        node_type = map_homee_node(node)
        for attribute in node.attributes:
            if attribute.type == const.SWITCH:
                _LOGGER.info("Node type: %s", node_type)
                HOMEE_ATTRIBUTES[node_type].append(attribute)
            elif attribute.type == const.COVER_POSITION:
                HOMEE_ATTRIBUTES[node_type].append(attribute)
            else:
                HOMEE_ATTRIBUTES['sensor'].append(attribute)

    for component in HOMEE_COMPONENTS:
        discovery.load_platform(hass, component, DOMAIN, {}, base_config)

    return True

def map_homee_node(node):
    """Map homee nodes to Home Assistant types."""
    from pyhomee import const
    attr_types = [ attr.type for attr in node.attributes ]
    if const.BRIGHTNESS in attr_types and const.SWITCH in attr_types:
        return 'light'
    if const.SWITCH in attr_types:
        return 'switch'
    if const.COVER_POSITION in attr_types:
        return 'cover'
#    if isinstance(vera_device, veraApi.VeraThermostat):
#        return 'climate'
#    if isinstance(vera_device, veraApi.VeraCurtain):
#        return 'cover'
    return 'sensor'

class HomeeDevice(Entity):
    """Representation of a Homee device entity."""

    def __init__(self, homee_node, homee_attribute, cube):
        """Initialize the device."""
        self.homee_node = homee_node
        self.homee_attribute = homee_attribute
        self.cube = cube

        self._name = self.homee_node.name
        _LOGGER.info(self.homee_attribute.id)
        # Append device id to prevent name clashes in HA.
        self.homee_id = HOMEE_ID_FORMAT.format(
            slugify(self._name), self.homee_node.id, self.homee_attribute.id, self.homee_attribute.type)

        self.cube.register(self.homee_node, self._update_callback)

    def _update_callback(self, attribute):
        """Update the state."""
        self.update_state(attribute)
        self.schedule_update_ha_state()

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def should_poll(self):
        """Get polling requirement from vera device."""
        return 

    @property
    def device_state_attributes(self):
        """Return the state attributes of the device."""
        attr = {}

        return attr

