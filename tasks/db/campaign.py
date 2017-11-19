"""
Module with DB tasks for working with campaigns tables in db
Classes: 
    GetCampaignsByLoginToken - gets all campaigns grouped by login and token
"""

from PyQt5.QtCore import pyqtSignal
from model.alchemy.campaign import YandexCampaign

from tasks.db.common import PQDBTask


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
