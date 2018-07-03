from typing import Dict, List, Tuple, Optional

from PyQt5.QtCore import pyqtSlot, pyqtSignal

from controllers.step.common import TaskChainStep
from tasks.api.yandex_tasks import GetDirectAds
from tasks.db.ad import SaveAdsFromAPI
from tasks.db.link import LinkSetsByLoginToken


class AdStep(TaskChainStep):
    finished = pyqtSignal(dict)

    @pyqtSlot(dict)
    def start(self, campaigns_by_login_token):
        self.reset_bar.emit(
            "Загружаем объявления",
            len(campaigns_by_login_token)
        )
        self.start_task(
            GetDirectAds(campaigns_by_login_token),
            {
                "got_ads": self.save_ads,
                "got_client": self.increment_bar,
                "finished": self.got_all_ads
            }
        )

    @pyqtSlot()
    def got_all_ads(self):
        """
        Handler that fires after all ads was acquired from API
        Await all saving tasks and then gets all data needed for next stage
        :return: None
        """
        self.await()
        self.start_task(
            LinkSetsByLoginToken(),
            {"got_sets": self.finished}
        )

    @pyqtSlot(str, list)
    def save_ads(self, _: str, ads: List):
        """
        Handler that fires after ads was acquired from API
        Saves API answer to db
        :param _: login of client to whom links belong (not used)
        :param ads: ads from api
        :return: None
        """
        self.start_task(
            SaveAdsFromAPI(ads),
            {}
        )
