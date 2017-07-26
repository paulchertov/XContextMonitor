from typing import List
import json


class YaApiException(Exception):
    pass


class YaApiOneException(Exception):
    def __init__(self, code: int, detail: str):
        message = "Yandex direct API error, code: {}, text: {}".format(
            code, detail
        )
        super().__init__(message)


class YaApiExceptions(YaApiException):
    def __init__(self, payload: List):
        message: str = "Api responded with several errors:"
        template: str = \
            "\nYandex direct API error, code: {}, name: {}, details: {}"
        for error in payload:
            message += template.format(
                error["Code"], error["Message"], error["Details"]
            )
        super().__init__(message)


class YaApiWarnings:
    def __init__(self, payload: List):
        self.message: str = "Api responded with several warnings:"
        template: str = \
            "\nYandex direct API warning, code: {}, name: {}, details: {}"
        for warning in payload:
            self.message += template.format(
                warning["Code"], warning["Message"], warning["Details"]
            )
