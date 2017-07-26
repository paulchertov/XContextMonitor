import json
import re
from typing import Pattern, List, Dict, Tuple, Optional, ClassVar
from collections import namedtuple

from requests import post

from settings.config import YA_DIRECT_URL, YA_DIRECT_TOKEN
from services.ads_api.errors import YaApiException, YaApiExceptions,\
    YaApiWarnings


YaApiUnits = namedtuple("YaApiUnits", "spent remains total")


units_regexp: ClassVar[Pattern] = re.compile(
    "([0-9]+)/([0-9]+)/([0-9]+)"
)


def ya_parse_units(text: str)-> YaApiUnits:
    """
    Parses Api units from their string representation
    as 10/1000/100000 to YaApiUnits named tuple
    :param text: text representation of Api units
    :return: units spent for request/units remained/units total
    """
    matches = units_regexp.match(text).groups()
    return YaApiUnits(
        spent=matches[0],
        remains=matches[1],
        total=matches[2]
    )


def ya_api_request(service_url: str, method_name: str,
                   params: Dict)->Tuple[YaApiUnits, Dict]:
    """
    :param service_url: url part of Yandex Direct API
    service
    :param method_name: Yandex Direct API method name 
    :param params: Yandex Direct API request params payload
    :return: Units (spend for request/available/total) and
    response payload
    """
    url = "{}/{}".format(YA_DIRECT_URL, service_url)
    headers = {"Authorization": "Bearer {}".format(YA_DIRECT_TOKEN)}
    data = {
        "method": method_name,
        "params": params
    }
    response = post(url=url, headers=headers, json=data)
    units = ya_parse_units(response.headers["Units"])
    return units, json.loads(response.text)
