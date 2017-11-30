"""
Module with DB tasks for working with campaigns tables in db
Classes: 
    SaveAdGroupsFromAPI - saves provided YaAPIDirectAdGroup list
    to db
    GetAllAdGroups - gets all ad groups from db
"""

from typing import List

from PyQt5.QtCore import pyqtSignal

from model.alchemy.ad_group import YandexAdGroup
from model.api_items.yandex import YaAPIDirectAdGroup
from tasks.db.common import PQDBTask


def all_ad_groups(session)->List[YaAPIDirectAdGroup]:
    """
    Internal function for getting all ad groups from db
    :param session: db session
    :return: list of all ad groups in db
    """
    return YaAPIDirectAdGroup.from_db_items(session.query(YandexAdGroup).all())


class SaveAdGroupsFromAPI(PQDBTask):
    """
    DB Task that updates db with all ad groups from 
    provided YaAPIDirectAdGroup list
    """

    def __init__(self, ad_groups: List[YaAPIDirectAdGroup]):
        super().__init__()
        self.ad_groups = ad_groups

    def run(self):
        try:
            YandexAdGroup.update_from_api(
                self.session,
                self.ad_groups
            )
        except Exception as e:
            self.error_occurred.emit(e)


class GetAllAdGroups(PQDBTask):
    """
    DB task that gets all ad groups from DB 
    :emits got_clients: - list of YaAPIAdGroup
    """
    got_ad_groups = pyqtSignal(list)

    def run(self):
        try:
            self.got_ad_groups.emit(
                YandexAdGroup.all_ad_groups(self.session)
            )
        except Exception as e:
            self.error_occurred.emit(e)
