"""
Gui wrapper for client (Yandex or Google)
contains single class PQClientMdel
"""

from datetime import datetime
from typing import Union

from PyQt5.QtCore import QObject, pyqtSignal

from model.alchemy.client import YandexClient


class PQClientModel(QObject):
    """
    GUI wrapper for API client item (Google or Yandex)
    properties:
        login: campaign login
        timestamp: datetime of last update from API
        source: Yandex or Google
        set_active: was checkbox checked on GUI (should be processed or not)
    signals:
        updated: emitted when any field was updated
    """
    updated = pyqtSignal()

    def __init__(self, model: Union[YandexClient, None]):
        """
        :param model: YandexClient or GoogleClient(not implemented yet)
        """
        super().__init__()
        self.persistent: Union[YandexClient, None] = model

    @property
    def source(self)->str:
        if isinstance(self.persistent, YandexClient):
            return "Yandex Direct"
        else:
            return ""

    @property
    def login(self)->str:
        return self.persistent.login

    @login.setter
    def login(self, val: str):
        self.persistent.login = val
        self.updated.emit()

    @property
    def timestamp(self)->datetime:
        return self.persistent.timestamp

    @timestamp.setter
    def timestamp(self, val: datetime):
        self.persistent.timestamp = val
        self.updated.emit()

    @property
    def set_active(self)->bool:
        return self.persistent.set_active

    @set_active.setter
    def set_active(self, val: bool):
        self.persistent.set_active = val
        self.updated.emit()