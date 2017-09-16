import json
import re
from typing import Pattern, List, Dict, Tuple, Optional, ClassVar
from collections import namedtuple

from requests import post

from settings.config import YA_DIRECT_URL
from services.tasks.yandex_api.errors import YaApiException, YaApiExceptions,\
    YaApiWarnings


YaApiUnits = namedtuple("YaApiUnits", "spent remains total")


YaApiGetResponse = Tuple[
    YaApiUnits,               # units spent for request/remained/total
    List[Dict],               # result items
    Optional[int],            # limited by (last item on page)
    Optional[YaApiException]  # error that occurred
]


YaApiGetAllResponse = Tuple[
    YaApiUnits,               # units spent for request/remained/total
    List[Dict],               # result items
    Optional[YaApiException]  # error that occurred
]

YaApiActionResponse = Tuple[
    YaApiUnits,                 # units spent for request/remained/total
    Optional[YaApiExceptions],  # errors that occurred
    Optional[YaApiWarnings],    # warnings returned by request
    Dict                        # result item(s)
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
        spent=int(matches[0]),
        remains=int(matches[1]),
        total=int(matches[2])
    )


def ya_api_request(service_url: str, method_name: str, params: Dict,
                   token: str, login: Optional[str]=None)\
        ->Tuple[YaApiUnits, Dict]:
    """
    Lowest level Yandex Direct API request, just sends request and returns
    raw content
    :param service_url: url part of API service
    :param method_name: API method name 
    :param login: client login for all requests except 'agencyclients'
    :param params: API request params payload
    :return: Units (spend for request/available/total) and
    response payload (parsed json) 
    """
    url = "{}/{}".format(YA_DIRECT_URL, service_url)

    headers = {"Authorization": "Bearer {}".format(token)}
    if login:
        headers["Client-Login"] = login

    data = {
        "method": method_name,
        "params": params
    }

    response = post(url=url, headers=headers, json=data)
    if "Units" in response.headers:
        units = ya_parse_units(response.headers["Units"])
    else:
        units = None
    return units, json.loads(response.text)


def ya_api_get_request(service_url: str, result_name: str,
                       params: Dict, token: str, login: Optional[str]=None)\
        ->YaApiGetResponse:
    """
    Low level Yandex Direct API request with 'get' method
    :param service_url: url part of API service 
    :param result_name: key in response dictionary that contains resulting
    items
    :param params: API request params payload
    :param login: client login for all requests except 'agencyclients'
    :return: Units (spend for request/available/total), 
    resulting items, last item if other pages available, error
    """
    units, response = ya_api_request(service_url, 'get', params, token, login)

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
                          params: Dict, token: str, login: str)\
        ->YaApiActionResponse:
    """
    Low level Yandex Direct API request for action methods: 
    add, update, delete and other
    :param service_url: url part of API service
    :param method_name: API method name
    :param params: API request params payload
    :param login: client login for all requests except 'agencyclients'
    :return: Units (spend for request/available/total), 
    errors, warnings
    """
    units, response = ya_api_request(
        service_url, method_name, params, token, login
    )

    result = response["result"] if "result" in response else None
    errors = YaApiExceptions(response["Errors"]) if "Errors" in result else None
    warnings = YaApiWarnings(response["Warnings"]) if "Warnings" in result else None

    return units, errors, warnings, result


def ya_api_get_all(service_url: str, result_name: str,
                   params: Dict, token: str, login: Optional[str]=None)\
        ->YaApiGetAllResponse:
    """
    Low level bunch of Yandex Direct API requests with 'get' method
    extracting all items. Sends multiple requests if response paged
    :param service_url: url part of API service 
    :param result_name: key in response dictionary that contains resulting
    items
    :param params: API request params payload
    :param login: client login for all requests except 'agencyclients'
    :return: Units (spend for request/available/total), 
    resulting items, error 
    """
    units, items, limited, error = ya_api_get_request(
        service_url, result_name, params, token, login
    )
    result = items
    if error:
        return units, items, error

    if limited:
        params = params.copy()

    while limited:
        params["Page"] = {
            "Limit": 10_000,
            "Offset": limited
        }
        units, items, limited, error = ya_api_get_request(
            service_url, result_name, params
        )
        if error:
            return units, items, error
        result += items

    return units, items, error
