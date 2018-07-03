from typing import List, Tuple

from PyQt5.QtCore import pyqtSlot, pyqtSignal

from controllers.step.common import TaskChainStep
from model.api_items.yandex import YaAPIDirectCampaign
from tasks.api.yandex_tasks import GetDirectCampaigns
from tasks.db.campaign import GetCampaignsByLoginToken, SaveCampaignsFromAPI


class CampaignStep(TaskChainStep):
    """
    Step for:
        - getting campaigns from api for each client
        - saving campaigns from API to DB
        - getting all campaigns and emitting them for the next step
    """
    finished = pyqtSignal(dict)

    @pyqtSlot(list)
    def start(self, login_token_pairs: List[Tuple[str, str]]):
        """
        Start step
        :return: None
        """
        self.reset_bar.emit(
            "Запрашиваем кампании из Директа",
            len(login_token_pairs)
        )
        self.start_task(
            GetDirectCampaigns(login_token_pairs),
            {
                "got_campaigns": self.save_campaigns,
                "finished": self.got_all_campaigns
            }
        )

    def next_step(self, campaigns):
        """
        Handler that fires after all campaigns has been acquired from DB
        It simply emits the result
        :return: None
        """
        self.finished.emit(campaigns)

    def got_all_campaigns(self):
        """
        Handler that fires after all campaigns was acquired from API
        it awaits after all campaigns are saved and gets all data for the
        next step
        :return: None
        """
        self.await()
        self.start_task(
            GetCampaignsByLoginToken(),
            {"got_campaigns": self.next_step}
        )

    def save_campaigns(self, campaigns: List[YaAPIDirectCampaign]):
        """
        Handler that fires each time campaigns was acquired from API
        I saves provided campaigns to DB
        :param campaigns: List of campaigns from API
        :return: None
        """
        self.increment_bar.emit()
        self.start_task(SaveCampaignsFromAPI(campaigns), {})
