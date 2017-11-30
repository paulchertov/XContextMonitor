from PyQt5.QtWidgets import QMainWindow

from controllers.common import WithViewMixin
from tasks.api.yandex_tasks import GetDirectClients
from tasks.db.client import LoadClients


class AppWidget(QMainWindow, WithViewMixin):
    gui_name = "main"

    def __init__(self):
        super().__init__()
        self.install_gui()
        self.view.test_button.clicked.connect(self.test_it)
        self.view.show()

    def test_it(self):
        task = GetDirectClients()
        task.finished.connect(self.loaded_clients)
        task.error_occurred.connect(self.loaded_clients)
        task.run()

    def loaded_clients(self, clients):
        print("")
        print(clients)