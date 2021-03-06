from typing import List


class YaApiException(Exception):
    """
    Exception generated by Yandex Direct API
    """
    pass


class YaApiOneException(Exception):
    """
    Single exception, generated by Yandex Direct API
    'get' method
    """
    def __init__(self, code: int, detail: str):
        message: str = "Yandex direct API error, code: {}, text: {}".format(
            code, detail
        )
        super().__init__(message)


class YaApiExceptions(YaApiException):
    """
    Multiple exceptions generated by Yandex Direct API 
    action methods: 'suspend', 'delete', 'add' etc.
    """
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
    """
    Multiple warnings generated by Yandex Direct API 
    action methods: 'suspend', 'delete', 'add' etc.
    Attention: does not belongs to Exception class
    """
    def __init__(self, payload: List):
        self.message: str = "Api responded with several warnings:"
        template: str = \
            "\nYandex direct API warning, code: {}, name: {}, details: {}"
        for warning in payload:
            self.message += template.format(
                warning["Code"], warning["Message"], warning["Details"]
            )


class YaApiNoUnits(YaApiException):
    """
    Exception raised then no API units left, so 
    request cannot be sent
    """
    pass
