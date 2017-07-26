import json
import re
from typing import Pattern, List, Dict, Tuple, Optional, ClassVar
from collections import namedtuple

from requests import post

from settings.config import YA_DIRECT_URL, YA_DIRECT_TOKEN
from services.ads_api.errors import YaApiException, YaApiExceptions,\
    YaApiWarnings


YaApiUnits = namedtuple("YaApiUnits", "spent remains total")


YaApiGetResponse = Tuple[
    YaApiUnits,               # units spent for request/remained/total
    List[Dict],               # result items
    Optional[int],            # limited by (last item on page)
    Optional[YaApiException]  # error that occurred
]


YaApiActionResponse = Tuple[
    YaApiUnits,                 # units spent for request/remained/total
    Optional[YaApiExceptions],  # errors that occurred
    Optional[YaApiWarnings]     # warnings returned by request
]


units_regexp: Pattern = re.compile(
    "([0-9]+)/([0-9]+)/([0-9]+)"
)  # regexp for extracting units


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
    Lowest level Yandex Direct API request, just sends request and returns
    raw content
    :param service_url: url part of API service
    :param method_name: API method name 
    :param params: API request params payload
    :return: Units (spend for request/available/total) and
    response payload (parsed json) 
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


def ya_api_get_request(service_url: str, result_name: str,
                       params: Dict)->YaApiGetResponse:
    """
    Low level Yandex Direct API request with 'get' method
    :param service_url: url part of API service 
    :param result_name: key in response dictionary that contains resulting
    items
    :param params: API request params payload
    :return: Units (spend for request/available/total), 
    resulting items, last item if other pages available, error
    """
    units, response = ya_api_request(service_url, 'get', params)

    result = response["result"].get(result_name, [])\
        if "result" in response else []

    if "error" in response:
        error = YaApiException(
            "Yandex direct API error, code: {}, text: {}".format(
                response["error"]["error_code"],
                response["error"]["error_detail"]
            )
        )
    else:
        error = None
    return units, result, response.get("LimitedBy", None), error


def ya_api_action_request(service_url: str, method_name: str,
                          params: Dict)->YaApiActionResponse:
    """
    Low level Yandex Direct API request for action methods: 
    add, update, delete and other
    :param service_url: url part of API service
    :param method_name: API method name
    :param params: API request params payload
    :return: Units (spend for request/available/total), 
    errors, warnings
    """
    units, response = ya_api_request(service_url, method_name, params)

    result = response["result"]
    errors = YaApiExceptions(result["Errors"]) if "Errors" in result else None
    warnings = YaApiWarnings(result["Errors"]) if "Errors" in result else None

    return units, errors, warnings
