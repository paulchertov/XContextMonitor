"""

"""


from PyQt5.QtCore import QThread, pyqtSignal
from sqlalchemy.orm import scoped_session, sessionmaker

from model.alchemy.common import engine


class PQDBTask(QThread):
    """
    Abstract class for DB task
    signals: error_occurred(Exception) - emits Exception that occurred
    """
    error_occurred = pyqtSignal(Exception)

    def __init__(self):
        super().__init__()
        self.__session_factory = sessionmaker(bind=engine)
        self.__Session = scoped_session(self.__session_factory)
        self.__session = None

    def __del__(self):
        self.__Session.remove()

    @property
    def session(self):
        if not self.session:
            self.__session = self.__Session()
        return self.__session