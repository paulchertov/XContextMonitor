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
from controllers.task_chain import PQTaskChainController
from controllers.result import PQResultController


class AppWidget(QMainWindow, WithViewMixin):
    """
    Main window of application
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
        self.task_chain: PQTaskChainController = None
        self.result: PQResultController = None

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
        self.install_controllers()

    def display(self):
        """
        Displays app
        :return: None
        """
        self.setCentralWidget(self.view)
        self.setGeometry(200, 200, 800, 600)
        self.show()

    def install_controllers(self):
        """
        Install clients widget, task_chain widget and result widget
        after DB was properly initialized.
        :return: None
        """
        self.clients = PQClientsController()
        self.clients.go_next.connect(self.start)
        self.clients.error_occurred.connect(self.error)

        self.task_chain = PQTaskChainController()
        self.task_chain.output_message.connect(self.display_message)
        self.task_chain.error_occurred.connect(self.error)
        self.task_chain.finished.connect(self.show_result)

        self.result = PQResultController()

        self.view.work_area.addWidget(self.clients.view)
        self.view.work_area.addWidget(self.task_chain.view)
        self.view.work_area.addWidget(self.result.view)
        self.view.work_area.setCurrentWidget(self.clients.view)

    @pyqtSlot()
    def start(self):
        """
        Handler that starts parsing process
        :return: None
        """
        self.view.work_area.setCurrentWidget(self.task_chain.view)
        self.task_chain.start()

    @pyqtSlot(list)
    def show_result(self, links):
        self.view.work_area.setCurrentWidget(self.result.view)
        self.result.model = links

    @pyqtSlot(Exception)
    def error(self, err):
        """
        Handler of errors
        :param err: Exception raised
        :return: None
        """
        self.view.error_output.setText(str(err))
        raise err

    @pyqtSlot(str)
    def display_message(self, message: str):
        """
        Handler for displaying info messages
        :return: None
        """
        self.view.output.setText(message)
