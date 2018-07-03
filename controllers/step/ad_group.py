from typing import Dict, List, Tuple, Optional

from PyQt5.QtCore import pyqtSlot, pyqtSignal

from model.alchemy.campaign import GroupedCampaigns
from controllers.step.common import TaskChainStep
from tasks.api.yandex_tasks import GetDirectAdGroups
from tasks.db.ad_group import SaveAdGroupsFromAPI


class AdGroupStep(TaskChainStep):
    """
    Step for:
        - getting clients from db
        - getting campaigns from api for each client
        - saving campaigns from API to DB
    """
    finished = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.campaigns_by_login_token: Optional[GroupedCampaigns] = None

    @pyqtSlot(dict)
    def start(self, campaigns_by_login_token):
        self.campaigns_by_login_token = campaigns_by_login_token
        self.reset_bar.emit(
            "Загружаем группы объявлений",
            len(campaigns_by_login_token)
        )

        self.start_task(
            GetDirectAdGroups(campaigns_by_login_token),
            {
                "got_ad_groups": self.save_ad_groups,
                "got_client": self.increment_bar,
                "finished": self.next_step
            }
        )

    def save_ad_groups(self, ad_groups):
        """
        Handler that fires after ad groups was acquired from API
        Saves API answer to db
        :param ad_groups: API answer
        :return: None
        """
        self.start_task(
            SaveAdGroupsFromAPI(ad_groups),
            {}
        )

    def next_step(self):
        """
        Handler that fires after all ad groups was acquired from API
        Await all saving tasks and go to the next step
        :return: None
        """
        self.await()
        self.finished.emit(self.campaigns_by_login_token)