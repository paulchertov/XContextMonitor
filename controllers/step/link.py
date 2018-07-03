from typing import Dict, List, Tuple, Optional

from PyQt5.QtCore import pyqtSlot, pyqtSignal

from controllers.step.common import TaskChainStep
from tasks.api.yandex_tasks import GetDirectLinks
from tasks.db.link import LinksByLogin,SaveLinksFromAPI


class LinkStep(TaskChainStep):
    finished = pyqtSignal(dict)

    @pyqtSlot(dict)
    def start(self, sets_by_login_token):
        self.reset_bar.emit(
            "Загружаем ссылки",
            len(sets_by_login_token)
        )
        self.start_task(
            GetDirectLinks(sets_by_login_token),
            {
                "got_links": self.save_links,
                "got_client": self.increment_bar,
                "finished": self.got_all_ads
            }
        )

    @pyqtSlot()
    def got_all_ads(self):
        """
        Handler that fires
        :return: None
        """
        self.await()
        self.start_task(
            LinksByLogin(),
            {"got_links": self.finished}
        )

    @pyqtSlot(list)
    def save_links(self, links: List):
        """
        Handler that fires after links was acquired from API
        Saves API answer to db
        :param ads: links from api
        :return: None
        """
        self.start_task(
            SaveLinksFromAPI(links),
            {}
        )
