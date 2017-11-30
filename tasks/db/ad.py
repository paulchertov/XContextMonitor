"""
Module with DB tasks for working with ads tables in db
Classes: 
    SaveAdsFromAPI - tasks that saves API items to DB
"""

from typing import List

from PyQt5.QtCore import pyqtSignal

from model.alchemy.ad import YandexAd
from model.alchemy.links import YandexLink, YandexLinksSet
from model.api_items.yandex import YaAPIDirectAd
from tasks.db.common import PQDBTask


def all_ads(session)->List[YaAPIDirectAd]:
    """
    Internal function for getting all ads from db
    :param session: db session
    :return: list of all ads in db
    """
    return YaAPIDirectAd.from_db_items(session.query(YandexAd).all())


class SaveAdsFromAPI(PQDBTask):
    """
    DB Task that updates db with all ads from 
    provided YaAPIDirectAdGroup list
    """
    def __init__(self, ads: List[YaAPIDirectAd]):
        super().__init__()
        self.ads = ads

    def run(self):
        try:
            YandexLinksSet.update_from_api(
                self.session, self.ads
            )
            YandexLink.update_from_api(
                self.session, self.ads
            )
            YandexAd.update_from_api(
                self.session,
                self.ads
            )
        except Exception as e:
            self.error_occurred.emit(e)
