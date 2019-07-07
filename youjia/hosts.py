"""
Copyright 2019 Vincent Qiu
Email: nov30th@gmail.com
Description:
莱特 LaiTe (laitecn) host cache in HA
Notice:
"""


from typing import Dict

from . import YouJiaClient

YOUJIA_HOSTS = {}  # type: Dict[str,YouJiaClient]


def get_host(host_name: str) -> YouJiaClient:
    return YOUJIA_HOSTS[host_name]
