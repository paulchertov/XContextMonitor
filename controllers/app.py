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
    """
    Main window of aplication
    slots:
        db_initialized - fire after db was iniialized
        error - error handler: displays provided error
    public methods: 
        display - dispays window
    """
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
        """
        Handler of DB installation
        :return: None
        """
        self.display()
        self.install_clients_widget()

    def display(self):
        """
        Displays app
        :return: Noe
        """
        self.setCentralWidget(self.view)
        self.setGeometry(200, 200, 800, 600)
        self.show()

    def install_clients_widget(self):
        """
        Install clients widget after DB was properly
        initialized.
        :return: None
        """
        self.clients = PQClientsController()
        self.clients.go_next.connect(self.ok)
        self.clients.error_occurred.connect(self.error)
        self.view.work_area.addWidget(self.clients.view)
        self.view.work_area.setCurrentWidget(self.clients.view)

    def ok(self):
        print("ok")

    @pyqtSlot(Exception)
    def error(self, err):
        """
        Handler of error
        :param err: Exception raised
        :return: None
        """
        self.view.error_output.setText(str(err))
        raise err

