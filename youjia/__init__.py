"""
Copyright 2019 Vincent Qiu
Email: nov30th@gmail.com
Description:
Supports for 莱特 LaiTe Devices (laitecn) in Home assistant
Supports for 右家(YouJia) Devices on LaiTe Bus
Installation:
Put all files to [config folder]/custom_components/
Notice:
"""

import logging
from .YouJiaClient import *

DOMAIN = "youjia"
_LOGGER = logging.getLogger(__name__)


def setup(hass, config):
    _LOGGER.info("Starting YouJia components loading...")

    is_first_platform = True
    # global YOUJIA_HOSTS  # type: Dict[str, YouJiaClient]

    for value in config[DOMAIN]:
        if is_first_platform:
            if value['platform'] != 'host':
                _LOGGER.error("Host platform must be the first of all platforms in section!")
                break
            is_first_platform = False
            youjia_host = YouJiaClient(value['name'],
                                                          value['host'],
                                                          value['port'],
                                                          str(value['device_id']).lower(),
                                                          '',
                                                          '',
                                                          value['contorl_delay'])
            YOUJIA_HOSTS[value['name']] = youjia_host
        if value['platform'] == 'switch':
            hass.helpers.discovery.load_platform('switch', DOMAIN, value, config)
        if value['platform'] == 'light':
            hass.helpers.discovery.load_platform('light', DOMAIN, value, config)

    # load_platform(hass,  'switch', DOMAIN,None, config)
    # hass.async_create_task(
    #     discovery.async_load_platform(
    #         hass, 'switch', DOMAIN, config['switch'], config
    #     )
    # )

    # Return boolean to indicate that initialization was successfully.
    return True
