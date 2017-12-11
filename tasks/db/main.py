"""
Module containing all tasks that manage DB state
classes:
    InitDB - init task for db
"""

from PyQt5.QtCore import QThread, pyqtSignal

from model.alchemy.common import Base, engine
from model.alchemy.campaign import YandexCampaign
from model.alchemy.ad_group import YandexAdGroup
from model.alchemy.ad import YandexAd
from model.alchemy.links import YandexLink, YandexLinksSet, LinkUrl


class InitDB(QThread):
    """
    Task that initialises database
    """
    error_occurred = pyqtSignal(Exception)

    def run(self):
        try:
            Base.metadata.create_all(engine)
            self.finished.emit()  # does not emits don't know why
        except Exception as e:
            self.error_occurred.emit(e)
