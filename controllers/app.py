from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import pyqtSlot

from controllers.common import WithViewMixin

from tasks.db.main import InitDB
from tasks.api.yandex_tasks import GetDirectClients
from tasks.db.client import LoadClients, SaveClientsFromAPI, SaveAllClientsToJSON
from settings.config import YA_DIRECT_TOKEN


class AppWidget(QMainWindow, WithViewMixin):
    gui_name = "main"

    def __init__(self):
        super().__init__()
        self.install_gui()
        task = InitDB()
        task.finished.connect(self.db_initialized)
        task.error_occurred.connect(self.error)
        task.run()

    def db_initialized(self):
        print("ok")
        self.view.test_button.clicked.connect(self.test_get)
        self.view.show()

    @pyqtSlot(Exception)
    def error(self, err):
        self.view.error_output.setText(str(err))

    def test_get(self):
        print("get")
        task = GetDirectClients(YA_DIRECT_TOKEN)
        task.got_clients.connect(self.got_clients)
        task.error_occurred.connect(self.error)
        task.run()

    def got_clients(self, clients):
        print("save")
        print(clients)
        task = SaveClientsFromAPI(clients)
        task.finished.connect(self.saved_clients)
        task.error_occurred.connect(self.error)
        task.run()

    def saved_clients(self):
        print("save to json")
        task = SaveAllClientsToJSON()
        task.error_occurred.connect(self.error)
        task.run()


    def test_load(self):
        task = LoadClients()
        task.got_clients.connect(self.loaded_clients)
        task.error_occurred.connect(self.loaded_clients)
        task.run()

    def loaded_clients(self, clients):
        print("loaded clients")
        print(clients)

