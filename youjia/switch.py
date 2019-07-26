"""
Copyright 2019 Vincent Qiu
Email: nov30th@gmail.com
Description:
Supports for 莱特 LaiTe Switch (laitecn) in Home assistant
"""

import logging
import threading
import time

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.components.light import PLATFORM_SCHEMA
from homeassistant.components.switch import SwitchDevice
from homeassistant.const import (
    CONF_ENTITY_ID, CONF_NAME)
from homeassistant.helpers.typing import ConfigType, HomeAssistantType
from .YouJiaClient import *

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = 'YouJia Switch'
SWITCH_STATUS_CHECKING_THREAD = {}  # type: Dict[threading.Thread]


def check_names(value):
    for index, name in value.items():
        if not isinstance(index, int) or not isinstance(name, str):
            _LOGGER.error("Names error in " + DEFAULT_NAME)
            return None
    return value


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_ENTITY_ID, default=DEFAULT_NAME): cv.string,
    vol.Optional('device_name', default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Required('names'): check_names,
})


def auto_checking_switch_state(youjia_host: YouJiaClient, laite_device_id: str):
    while True:
        time.sleep(10)
        youjia_host.send_str_command("{}8686860F".format(laite_device_id.lower()))


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
        _LOGGER.info("Adding switch {} of {} into HA.".format(name, entry_id))
        async_add_entities([YoujiaX160(name,
                                       entry_id,
                                       config['entity_id'],
                                       index,
                                       config['host_name']
                                       )], True)
    if config['auto'] is True:
        thread = threading.Thread(target=auto_checking_switch_state,
                                  args=(get_host(config['host_name']), config['entity_id']))
        thread.daemon = True
        SWITCH_STATUS_CHECKING_THREAD[config['name']] = thread
        thread.start()


class YoujiaX160(SwitchDevice):
    """Represents a Switch as a Light."""

    def __init__(self,
                 name: str,
                 switch_entity_id: str,
                 laite_device_id: str,
                 solt: int,
                 host_name: str,
                 ) -> None:
        _LOGGER.debug("Adding switch {} of {}".format(name, switch_entity_id))
        self._name = name  # type: str
        self._switch_entity_id = switch_entity_id.lower()  # type: str
        self._switch_entity_solt = solt  # type: int
        self._dest_device_id = laite_device_id.lower()  # type: str
        self._is_on = False  # type: bool
        self._available = False  # type: bool
        self._async_unsub_state_changed = None
        self._host_class = get_host(host_name)
        self._host_class.add_str_receiver(self.on_str_command_received)

    def on_str_command_received(self, message):
        if self._switch_entity_solt > 99:
            return
        _LOGGER.debug("on_str_command_received %s", message)
        if len(message) == len('1aca1008b4000001010101010100000000000000000f'):
            if message[:10] == self._dest_device_id:
                slot_status = message[10 + self._switch_entity_solt * 2: 12 + self._switch_entity_solt * 2]
                if slot_status == '00':  # and self._is_on is True:
                    self._is_on = False
                    self.async_write_ha_state()
                    _LOGGER.debug("Sync status done...")

                if slot_status == '01':  # and self._is_on is False:
                    self._is_on = True
                    self.async_write_ha_state()
                    _LOGGER.debug("Sync status done...")

    def turn_off(self, **kwargs) -> None:
        self.send_command_off(self._dest_device_id, self._switch_entity_solt)
        _LOGGER.debug("sent switch {}.{} command off.".format(self._dest_device_id, self._switch_entity_solt))

    def turn_on(self, **kwargs) -> None:
        self.send_command_on(self._dest_device_id, self._switch_entity_solt)
        _LOGGER.debug("sent switch {}.{} command on.".format(self._dest_device_id, self._switch_entity_solt))

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

    def send_command_on(self, device_id: str, solt: int):
        # request_message = "{}00{:0>2}{}0F".format(device_id, solt, '01')
        request_message = "{0}00{1:0>2}{2}0F".format(device_id, solt, '01')
        if solt > 99:
            self._is_on = True
            self.async_write_ha_state()
            if solt == 100:
                request_message = "{0}017788FF".format(device_id)
            elif solt == 101:
                request_message = "{0}107788FF".format(device_id)
            elif solt == 102:
                request_message = "{0}307788FF".format(device_id)

        _LOGGER.debug("command on switch command: %s", request_message)
        self._host_class.send_str_command(request_message)

    def send_command_off(self, device_id: str, solt: int):
        request_message = "{0}00{1:0>2}{2}0F".format(device_id, solt, '00')
        if solt > 99:
            self._is_on = False
            self.async_write_ha_state()
            if solt == 100:
                request_message = "{0}027788FF".format(device_id)
            elif solt == 101:
                request_message = "{0}207788FF".format(device_id)
            elif solt == 102:
                request_message = "{0}407788FF".format(device_id)

        _LOGGER.debug("command off switch command: %s", request_message)
        self._host_class.send_str_command(request_message)
