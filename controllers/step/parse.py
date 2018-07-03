from PyQt5.QtCore import pyqtSlot, pyqtSignal

from controllers.step.common import TaskChainStep
from tasks.crawling.tasks import CheckUrls
from tasks.db.link import SaveParsedLink, AggregateParsedLinks


class ParseStep(TaskChainStep):
    finished = pyqtSignal(list)

    @pyqtSlot(dict)
    def start(self, links_by_login):
        """

        :param links_by_login:
        :return:
        """
        self.reset_bar.emit(
            "Проверяем страницы",
            sum(
                [len(campaigns) for campaigns in links_by_login.values()]
            )
        )
        self.start_task(
            CheckUrls(links_by_login),
            {
                "got_url": self.save_parsed_link,
                "finished": self.got_all_links
            }
        )

    @pyqtSlot()
    def got_all_links(self):
        """
        Handler that fires after all pages was parsed
        It awaits all tasks and then gets from DB resulting data
        and emits it up
        :return: None
        """
        self.await()
        self.start_task(
            AggregateParsedLinks(),
            {"got_links": self.finished}
        )

    @pyqtSlot(str, str, str)
    def save_parsed_link(self, url, status, warning):
        """
        Handler that fires after single page was parsed
        It saves page and increments progressbar
        :return: None
        """
        self.start_task(
            SaveParsedLink(url, status, warning),
            {"finished": self.increment_bar}
        )