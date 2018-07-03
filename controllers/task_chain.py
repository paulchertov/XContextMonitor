"""
Module with single task chain controller of the app
classes:
    PQTaskChainController - controller that handles all API calls,
    DB interactions to save API results and displays progress bar
"""

from typing import Tuple, List, Dict, Callable, Optional

from PyQt5.QtCore import QObject, QThread, pyqtSlot, pyqtSignal

from controllers.common import WithViewMixin
from controllers.step.common import TaskChainStep
from controllers.step.client import ClientStep
from controllers.step.campaign import CampaignStep
from controllers.step.ad_group import AdGroupStep
from controllers.step.ad import AdStep
from controllers.step.link import LinkStep
from controllers.step.parse import ParseStep


class PQTaskChainController(QObject, WithViewMixin):
    """
    Controller for task steps. Each step output is connected to next step input
    sots:
        reset_bar - resets progress bar to zero state
        increment bar - increments progress bar counter

    other signals:
        output_message - provides current state message to display
        error_occurred - emits Exception occured
    """
    gui_name = "task_chain"

    error_occurred = pyqtSignal(Exception)
    output_message = pyqtSignal(str)
    finished = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.install_gui()
        self.set_styles()

        self.clients_step = ClientStep()
        self.campaigns_step = CampaignStep()
        self.ad_groups_step = AdGroupStep()
        self.ad_step = AdStep()
        self.link_step = LinkStep()
        self.parse_step = ParseStep()

        self.connect_signals(self.clients_step, self.campaigns_step)
        self.connect_signals(self.campaigns_step, self.ad_groups_step)
        self.connect_signals(self.ad_groups_step, self.ad_step)
        self.connect_signals(self.ad_step, self.link_step)
        self.connect_signals(self.link_step, self.parse_step)
        self.connect_signals(self.parse_step)

    @pyqtSlot()
    def start(self):
        """
        Slot that starts whole chain of tasks
        :return: None
        """
        self.clients_step.start()

    def connect_signals(self, step: TaskChainStep,
                        next_step: Optional[TaskChainStep] = None):
        """
        Connects signals to provided step:
            - connects error_occurred to self error_occurred
            - connects steps finished to next steps start
        :param step:
        :param next_step:
        :return:
        """
        step.error_occurred.connect(self.error_occurred)
        step.increment_bar.connect(self.increment_bar)
        step.reset_bar.connect(self.reset_bar)
        if next_step is None:
            step.finished.connect(self.finished)
        else:
            step.finished.connect(next_step.start)

    @pyqtSlot(str, int)
    def reset_bar(self, message: str, max_val: int):
        self.output_message.emit("Ждем...")
        self.sender().await()
        self.output_message.emit(message)
        self.view.progress_bar.setMaximum(max_val)
        self.view.progress_bar.setValue(0)

    @pyqtSlot()
    def increment_bar(self):
        self.view.progress_bar.setValue(self.view.progress_bar.value() + 1)

