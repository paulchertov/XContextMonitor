"""
Module with single main controller of the whole app
classes:
    AppWidget - Main controller that handles global application state
"""


from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import pyqtSlot

from controllers.common import WithViewMixin

from tasks.db.main import InitDB
from controllers.clients import PQClientsController


class AppWidget(QMainWindow, WithViewMixin):
    gui_name = "main"

    def __init__(self):
        super().__init__()
        self.install_gui()

        self.clients: PQClientsController = None

        task = InitDB()
        task.finished.connect(self.db_initialized)
        task.error_occurred.connect(self.error)
        task.run()

    @pyqtSlot()
    def db_initialized(self):
        self.display()
        self.install_clients_widget()


    def display(self):
        self.setCentralWidget(self.view)
        self.setGeometry(200, 200, 800, 600)
        self.show()

    def install_clients_widget(self):
        print("ok")
        self.clients = PQClientsController()
        self.clients.go_next.connect(self.ok)
        self.clients.error_occurred.connect(self.error)
        self.view.work_area.addWidget(self.clients.view)
        self.view.work_area.setCurrentWidget(self.clients.view)
        print("ok")

    def ok(self):
        print("ok")

    @pyqtSlot(Exception)
    def error(self, err):
        self.view.error_output.setText(str(err))
        raise err

