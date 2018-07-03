from typing import List

from PyQt5.QtCore import pyqtSlot, pyqtSignal

from settings.config import YA_DIRECT_TOKEN
from controllers.step.common import TaskChainStep
from model.api_items.yandex import YaAPIDirectClient
from tasks.db.client import GetClients


class ClientStep(TaskChainStep):
    """
    Step for getting clients from DB amd emitteng them for the next step
    """
    finished = pyqtSignal(list)

    @pyqtSlot()
    def start(self):
        """
        Start step
        :return: None
        """
        self.start_task(
            GetClients(),
            {"got_clients": self.parse_clients}
        )

    def parse_clients(self, clients: List[YaAPIDirectClient]):
        """
        Handler that fires after clients was aquired from DB.
        It munges data to form of login+token pairs and emits the result
        :param clients: List of clients from DB
        :return: None
        """
        self.await()
        self.finished.emit(
            [
                (client.login, client.token or YA_DIRECT_TOKEN)
                for client in clients
                if client.set_active
            ]
        )
