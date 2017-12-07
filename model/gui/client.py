"""
ViewModel for client (Yandex or Google)
contains single class PQClientModel
"""

from datetime import datetime
from typing import Union

from PyQt5.QtCore import QObject, pyqtSignal

from model.api_items.yandex import YaAPIDirectClient


class PQClientModel(QObject):
    """
    ViewModel for API client item (Google or Yandex)
    properties:
        login: campaign login
        timestamp: datetime of last update from API
        source: Yandex or Google
        set_active: was checkbox checked on GUI (should be processed or not)
    signals:
        updated: emitted when any field was updated
    """
    updated = pyqtSignal()

    def __init__(self, model: Union[YaAPIDirectClient, None]):
        """
        :param model: YaAPIDirectClient or GoogleAPIAdwordsClient(not implemented yet)
        """
        super().__init__()
        self.__model: Union[YaAPIDirectClient, None] = model

    @property
    def source(self)->str:
        if isinstance(self.model, YaAPIDirectClient):
            return "Yandex Direct"
        else:
            return ""

    @property
    def model(self)->Union[YaAPIDirectClient, None]:
        return self.__model

    @model.setter
    def model(self, val: Union[YaAPIDirectClient, None]):
        self.__model = val
        self.updated.emit()

    @property
    def login(self)->str:
        return self.model.login

    @login.setter
    def login(self, val: str):
        self.model.login = val
        self.updated.emit()

    @property
    def timestamp(self)->datetime:
        return self.model.timestamp

    @timestamp.setter
    def timestamp(self, val: datetime):
        self.model.timestamp = val
        self.updated.emit()

    @property
    def is_active(self)->bool:
        return self.model.is_active

    @is_active.setter
    def is_active(self, val: bool):
        self.model.is_active = val
        self.updated.emit()
