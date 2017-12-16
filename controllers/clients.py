import datetime
from typing import List

from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QSpacerItem, QSizePolicy, QInputDialog, QLineEdit

from settings.config import YA_DIRECT_TOKEN
from controllers.common import WithViewMixin, clear_items
from controllers.client import PQClientController
from model.api_items.yandex import YaAPIDirectClient
from model.gui.client import PQClientModel
from tasks.db.client import AddClient, SaveAllClientsToJSON, SaveClientsFromAPI,\
    LoadClients, UpdateClientsFromGUI
from tasks.api.yandex_tasks import GetDirectClients


class PQClientsController(QObject, WithViewMixin):
    """
    signals:
        error_occured - something gone wrong, emits Exception
        go_next - all client modifications nave been made, parent need to move
        to another controller
    """
    gui_name = "clients"
    go_next = pyqtSignal()
    error_occurred = pyqtSignal(Exception)

    def __init__(self):
        super().__init__()
        self.install_gui()
        self.set_styles()
        self.__model: List[PQClientModel] = []
        self.view.start_button.clicked.connect(self.parse)
        self.view.add_one_button.clicked.connect(self.add_yandex_client)
        self.view.refresh_button.clicked.connect(self.refresh)

        self.view.setEnabled(False)

        def initiated(clients: List[YaAPIDirectClient]):
            """
            Handler that fires after clients was loaded
            and updates current model with loaded data
            :param clients: clients loaded from JSON
            :return: None
            """
            self.view.setEnabled(True)
            self.model = clients

        task = LoadClients()
        task.got_clients.connect(initiated)
        task.error_occurred.connect(self.error_occurred)
        task.run()

    @pyqtSlot()
    def refresh(self):
        """
        Refresh button handler. 
        :return: None
        """

        def saved_clients_to_db(clients):
            """
            Handler that fires after clients was saved
            to db and updates model with actual clients
            :param clients: clients loaded from JSON
            :return: None
            """
            self.view.setEnabled(True)
            self.model = clients

        def got_clients_from_api(clients):
            """
            Handler that fires after clients was loaded
            and updates db with result 
            :param clients: clients loaded from JSON
            :return: None
            """
            task = SaveClientsFromAPI(clients)
            task.got_clients.connect(saved_clients_to_db)
            task.error_occurred.connect(self.error_occurred)
            task.run()
        self.view.setEnabled(False)
        task = GetDirectClients(YA_DIRECT_TOKEN)
        task.got_clients.connect(got_clients_from_api)
        task.error_occurred.connect(self.error_occurred)
        task.run()

    @pyqtSlot()
    def parse(self):
        """
        Start button handler. Finish clients edit and move to next view
        :return: None
        """
        def to_json():
            task = SaveAllClientsToJSON()
            task.finished.connect(self.go_next)
            task.error_occurred.connect(self.error_occurred)
            task.run()

        task = UpdateClientsFromGUI(self.__model)
        task.got_clients.connect(to_json)
        task.error_occurred.connect(self.error_occurred)
        task.run()

    @pyqtSlot()
    def add_yandex_client(self):
        """
        Add client button handler. Adds new Yandex client
        :return: None 
        """
        login, ok = QInputDialog.getText(
            self.view, "Логин нового клиента", "Логин нового клиента:",
            QLineEdit.Normal,
            ""
        )  # asking user to provide login
        if not ok or login == "":
            return
        token, ok = QInputDialog.getText(
            self.view,
            "Токен",
            "https://oauth.yandex.ru/authorize?response_type=token&client_id=96cd64223edb44918fa817d932c6b9af"
            + "\n чего пишут?",
            QLineEdit.Normal,
            ""
        )  # asking user to provide token
        if not ok or token == "":
            return

        def added_client(all_clients: List[YaAPIDirectClient]):
            """
            handler of all 
            :param all_clients: all clients list
            :return: None
            """
            self.view.setEnabled(True)
            self.model = all_clients

        self.view.setEnabled(False)
        task = AddClient(
            YaAPIDirectClient(
                login=login,
                token=token,
                set_active=True,
                timestamp=datetime.datetime.now()
            )
        )
        task.got_clients.connect(added_client)
        task.error_occurred.connect(self.error_occurred)
        task.run()

    @pyqtSlot()
    def redraw(self):
        """
        refresh widget to reflex actual model
        :return: None
        """
        clear_items(self.view.items_layout)
        for client in self.__model:
            client = PQClientController(client)
            client.model.updated.connect(self.redraw)
            self.view.items_layout.addWidget(client.view)
            self.view.scroll_area.ensureWidgetVisible(client.view)
        self.view.items_layout.addItem(  # adding spacer for correct alignment
            QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )

    @property
    def model(self)->List[YaAPIDirectClient]:
        return [client.model for client in self.__model]

    @model.setter
    def model(self, val: List[YaAPIDirectClient]):
        self.__model = [PQClientModel(item) for item in val]
        self.redraw()
