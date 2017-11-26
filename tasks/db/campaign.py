"""
Module with DB tasks for working with campaigns tables in db
Classes: 
    GetCampaignsByLoginToken - gets all campaigns grouped by login and token
"""

from typing import List

from PyQt5.QtCore import pyqtSignal

from model.alchemy.campaign import YandexCampaign
from model.api_items.yandex import YaAPIDirectCampaign
from tasks.db.common import PQDBTask


class SaveCampaignsFromAPI(PQDBTask):
    """
    DB Task that updates db with all campaigns from 
    provided YaAPIDirectCampaign list
    """

    def __init__(self, campaigns: List[YaAPIDirectCampaign]):
        super().__init__()
        self.campaigns = campaigns

    def run(self):
        try:
            YandexCampaign.update_from_api(
                self.session,
                self.clients
            )
        except Exception as e:
            self.error_occurred.emit(e)


class GetCampaignsByLoginToken(PQDBTask):
    """
    DB task that gets all campaigns grouped by login and token
    :emits got_campaigns: dictionary with
        keys - tuple of (login, token)
        values - lists of int ids of campaigns
    """
    got_campaigns = pyqtSignal(dict)

    def run(self):
        try:
            self.got_campaigns.emit(
                YandexCampaign.by_login_and_token(self.session)
            )
        except Exception as e:
            self.error_occurred.emit(e)
