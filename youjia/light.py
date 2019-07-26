"""
Copyright 2019 Vincent Qiu
Email: nov30th@gmail.com
Description:
Supports for 莱特 LaiTe Switch (laitecn) in Home assistant
"""

from homeassistant.components.light import Light, SUPPORT_BRIGHTNESS, ATTR_BRIGHTNESS
from homeassistant.helpers.typing import ConfigType, HomeAssistantType
from .YouJiaClient import *

MAX_HA_BRIGHT = 255

BRIGHT_END = 0xF0

BRIGHT_START = 0x25

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = 'YouJia Brightness Light'
SWITCH_STATUS_CHECKING_THREAD = {}  # type: Dict[threading.Thread]


def check_names(value):
    for index, name in value.items():
        if not isinstance(index, int) or not isinstance(name, str):
            _LOGGER.error("Names error in " + DEFAULT_NAME)
            return None
    return value


def auto_checking_switch_state(youjia_host: YouJiaClient, laite_device_id: str):
    while True:
        time.sleep(3)
        youjia_host.send_str_command("{}8686860f".format(laite_device_id.lower()))


async def async_setup_platform(hass: HomeAssistantType,
                               config: ConfigType,
                               async_add_entities,
                               discovery_info=None) -> None:
    """Initialize Light Switch platform."""
    _LOGGER.info("Startup Youjia platform configuration.")

    if (discovery_info is not None and config is None) or len(config) == 0:
        config = discovery_info

    if config is None:
        return

    if discovery_info is None:
        return

    if config['names'] is None:
        return

    for index, name in config['names'].items():
        entry_id = "{0}{1:0>2}".format(config['entity_id'], index)
        _LOGGER.info("Adding brightness light {} of {} into HA.".format(name, entry_id))
        async_add_entities([YoujiaX160(name,
                                       entry_id,
                                       config['entity_id'],
                                       index,
                                       config['total_solts'],
                                       config['host_name']
                                       )], True)
    if config['auto'] is True:
        thread = threading.Thread(target=auto_checking_switch_state,
                                  args=(get_host(config['host_name']), config['entity_id']))
        thread.daemon = True
        SWITCH_STATUS_CHECKING_THREAD[config['name']] = thread
        thread.start()


class YoujiaX160(Light):
    """Represents a Switch as a Light."""

    @property
    def supported_features(self):
        return SUPPORT_BRIGHTNESS

    def __init__(self,
                 name: str,
                 switch_entity_id: str,
                 laite_device_id: str,
                 solt: int,
                 total_solts: int,
                 host_name: str,
                 ) -> None:
        _LOGGER.debug("Adding brightness light {} of {}".format(name, switch_entity_id))
        self._name = name  # type: str
        self._switch_entity_id = switch_entity_id.lower()  # type: str
        self._switch_entity_solt = solt  # type: int
        self._dest_device_id = laite_device_id.lower()  # type: str
        self._is_on = False  # type: bool
        self._available = False  # type: bool
        self._async_unsub_state_changed = None
        self._host_class = get_host(host_name)
        self._host_class.add_str_receiver(self.on_str_command_received)
        self._brightness = 0
        self._total_solts = total_solts

    def on_str_command_received(self, message):
        if self._switch_entity_solt > 99:
            return
        char_0f_pos = 2 * 5 + self._total_solts * 6
        if len(message) < char_0f_pos + 2:
            return
        if (len(message) > 2 * 5) and message[char_0f_pos:char_0f_pos + 2] == '0f':
            # Current Device Status Message
            if message[:10] != self._dest_device_id:
                return
            if len(message) >= (2 * 5 + 2 + (self._switch_entity_solt + 1) * 3):
                # Verified device message length
                status_message_position = 2 * 5 - 1 + self._switch_entity_solt * 6 + 1
                status_message = message[status_message_position:status_message_position + 6]
                _LOGGER.warn("status message:{}".format(status_message))
                if status_message[:2] == '00':
                    # reply message or toggle message
                    self._brightness = int('0x' + status_message[2:4], 16) / 100.0 * MAX_HA_BRIGHT
                    self._is_on = True if status_message[4:6] == '01' else False
                    self.async_write_ha_state()

    def turn_off(self, **kwargs) -> None:
        self.send_command_off(self._dest_device_id, self._switch_entity_solt)
        _LOGGER.debug("sent brightness light {}.{} command off.".format(self._dest_device_id, self._switch_entity_solt))

    def turn_on(self, **kwargs) -> None:
        brightness = kwargs.get(ATTR_BRIGHTNESS, MAX_HA_BRIGHT)
        brightness_range = BRIGHT_START - BRIGHT_END
        machine_brightness = int(brightness_range * (brightness * 1.0 / MAX_HA_BRIGHT) + BRIGHT_END)
        if self._brightness == 0:
            self._brightness = BRIGHT_END
        self.send_command_on(self._dest_device_id, self._switch_entity_solt, machine_brightness)
        _LOGGER.debug("sent brightness light {}.{} command on.".format(self._dest_device_id, self._switch_entity_solt))

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    @property
    def is_on(self) -> bool:
        """Return true if light switch is on."""
        return self._is_on

    @property
    def available(self) -> bool:
        """Return true if light switch is on."""
        return True

    @property
    def should_poll(self) -> bool:
        """No polling needed for a light switch."""
        return False

    def send_command_on(self, device_id: str, solt: int, brightness: int):
        _LOGGER.warn("brightness:{}".format(brightness))
        self._brightness = brightness
        request_message = "{0}".format(device_id)
        empty_str = "ff0000"
        start_pos = 0
        while start_pos < solt:
            request_message += empty_str
            start_pos += 1
        request_message += "ff{:02x}01".format(brightness)
        while start_pos < self._total_solts - 1:
            request_message += empty_str
            start_pos += 1
        request_message += '0f'
        _LOGGER.warn("command on brightness light command: %s", request_message)
        self._host_class.send_str_command(request_message)

    def send_command_off(self, device_id: str, solt: int):
        request_message = "{0}".format(device_id)
        empty_str = "ff0000"
        start_pos = 0
        while start_pos < solt:
            request_message += empty_str
            start_pos += 1
        request_message += "000001"
        while start_pos < self._total_solts - 1:
            request_message += empty_str
            start_pos += 1
        request_message += '0f'
        _LOGGER.warn("command on brightness light command: %s", request_message)
        self._host_class.send_str_command(request_message)

    @property
    def brightness(self):
        """Return the brightness of this light between 0..255."""
        return self._brightness
