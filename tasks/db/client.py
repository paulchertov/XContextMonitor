"""
Module with DB tasks for working with clients tables
in db
Classes:
    SaveClientsFromAPI - updates db with all clients from 
    provided YaAPIDirectClient list
    SaveAllClientsToJSON - saves db clients to JSON
    LoadClients - updates db with all clients, saved to json
    and then gets all clients from db
    GetClients - updates db with all clients, saved to json
    and then gets all clients from db
    AddClient - adds one client
    and then gets all clients from db
"""

from typing import List

from PyQt5.QtCore import pyqtSignal

from model.alchemy.client import YandexClient
from model.api_items.yandex import YaAPIDirectClient
from model.gui.client import PQClientModel
from tasks.db.common import PQDBTask


def all_clients(session)->List[YaAPIDirectClient]:
    """
    Internal function for getting all clients from db
    :param session: db session
    :return: list of all clients in db
    """
    return YaAPIDirectClient.from_db_items(
        session.query(YandexClient).all()
    )


class SaveClientsFromAPI(PQDBTask):
    """
    DB Task that updates db with all clients from 
    provided YaAPIDirectClient list
    :emits got_clients: - list of all YaAPIDirectClient
    """
    got_clients = pyqtSignal(list)

    def __init__(self, clients: List[YaAPIDirectClient]):
        super().__init__()
        self.clients = clients

    def run(self):
        try:
            YandexClient.update_from_api(
                self.session,
                self.clients
            )
            self.got_clients.emit(all_clients(self.session))
        except Exception as e:
            self.error_occurred.emit(e)


class LoadClients(PQDBTask):
    """
    DB Task that updates db with all clients, saved to json
    and then gets all clients from db
    :emits got_clients: - list of all YaAPIDirectClient
    """
    got_clients = pyqtSignal(list)

    def run(self):
        try:
            YandexClient.load_json(self.session)
            self.got_clients.emit(all_clients(self.session))
        except Exception as e:
            self.error_occurred.emit(e)


class SaveAllClientsToJSON(PQDBTask):
    """
    DB Task that saves all db clients to JSON
    :emits got_clients: - list of all YaAPIDirectClient
    """
    got_clients = pyqtSignal(list)

    def run(self):
        try:
            YandexClient.save_json(self.session)
            self.got_clients.emit(all_clients(self.session))
        except Exception as e:
            self.error_occurred.emit(e)


class GetClients(PQDBTask):
    """
    DB task that gets all clients from DB 
    :emits got_clients: - list of all YaAPIDirectClient
    """
    got_clients = pyqtSignal(list)

    def run(self):
        try:
            self.got_clients.emit(all_clients(self.session))
        except Exception as e:
            self.error_occurred.emit(e)


class AddClient(PQDBTask):
    """
    DB task that adds one client
    and then gets all clients from db
    :emits got_clients: - list of YaAPIDirectClient
    """
    got_clients = pyqtSignal(list)

    def __init__(self, client: YaAPIDirectClient):
        """
        :param client: client that will be added to DB
        """
        super().__init__()
        self.client = client

    def run(self):
        try:
            YandexClient.add_single(self.session, self.client)
            self.got_clients.emit(all_clients(self.session))
        except Exception as e:
            self.error_occurred.emit(e)


class UpdateClientsFromGUI(PQDBTask):
    """
    DB task that updates model after changes made in GUI
    """
    got_clients = pyqtSignal(list)

    def __init__(self, clients: List[PQClientModel]):
        """
        :param clients: list of PQClientModel 
        """
        super().__init__()
        self.clients = clients

    def run(self):
        try:
            ya_clients = [
                x.model for x in self.clients if x.source == "yandex"
            ]
            YandexClient.update_from_gui(self.session, ya_clients)
            self.got_clients.emit(all_clients(self.session))
        except Exception as e:
            self.error_occurred.emit(e)