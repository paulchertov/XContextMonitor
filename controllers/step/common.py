"""
Module contains class common to all task steps:
    TaskChainStep -
"""
from typing import Dict, List, Callable

from PyQt5.QtCore import QObject, QThread, pyqtSlot, pyqtSignal


class TaskChainStep(QObject):
    """
    Object, containing tasks grouped by common purpose
    fields:
        - error - is everything okay or error occurred somewhere among threads
        from thread pool
    methods:
        - start task - start provided thread, connecting it error_occurred
        to self occurred_error signal, and ads thread to self threads pool
        - await - await until all threads from thread pool are finished
        - raise_error - handle occurred error
    """
    error_occurred = pyqtSignal(Exception)
    reset_bar = pyqtSignal(str, int)
    increment_bar = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.error: bool = False
        self.__active_threads: List[QThread] = []

    def start_task(self, task: QThread, handlers: Dict[str, Callable]):
        """
        Start provided task connecting provided functions to corresponding
        signals, adding thread to thread pool, and connecting self error
        handling to task
        :param task: thread that need to be started
        :param handlers: dictionary of signal: handler pairs
        :return: None
        """
        self.__active_threads.append(task)
        for handler_name, handler in handlers.items():
            task.__getattr__(handler_name).connect(handler)
        task.error_occurred.connect(self.raise_error)

        def remove():
            """
            Handler for removing thread
            :return: None
            """
            self.__active_threads.remove(task)

        task.finished.connect(remove)
        task.start()

    def await(self):
        """
        Await until all threads from thread pool are finished
        :return:
        """
        for thread in self.__active_threads:
            thread.wait()

    def raise_error(self, err: Exception):
        """
        Set self error state to true and emit error occured signal
        :param err: error occurred
        :return: None
        """
        self.error = True
        self.error_occurred.emit(err)
