"""
Module with DB tasks for working with clients tables
in db
Classes:
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
from tasks.db.common import PQDBTask


def all_clients(session)->List[YaAPIDirectClient]:
    """
    Internal function for getting all clients from db
    :param session: db session
    :return: list of all clients in db
    """
    return [
        YaAPIDirectClient(
            login=client.login,
            token=client.token,
            timestamp=client.timestamp,
            is_active=client.set_active
        )
        for client in session.query(YandexClient).all()
    ]


class LoadClients(PQDBTask):
    """
    DB Task that updates db with all clients, saved to json
    and then gets all clients from db
    :emits got_clients: - list of YaAPIDirectClient
    """
    got_clients = pyqtSignal(list)

    def run(self):
        try:
            YandexClient.load_json(self.session)
            self.got_clients.emit(all_clients(self.session))
        except Exception as e:
            self.error_occurred.emit(e)


class GetClients(PQDBTask):
    """
    DB task that gets all clients from DB 
    and then gets all clients from db
    :emits got_clients: - list of YaAPIDirectClient
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
