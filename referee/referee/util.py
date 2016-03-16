# -*- coding: utf-8 -*-

import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError, Timeout, ConnectionError
import json

from .logger import log


def notify(url, data=dict()):
    try:
        log.info("Sending request to {}".format(url))
        req = requests.post(url, data=data)
        req.raise_for_status()
        data = json.loads(req.text)
        return data
    except (HTTPError, ConnectionError, Timeout):
        raise


def transform_list(l):
    """Converts list to list of tuples
    """
    if len(l) <= 1:
        raise Exception
    it = iter(l)
    return zip(it, it)
