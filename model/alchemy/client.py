"""
SQLAlchemy model for client items for Yandex and Googl API
Classes:
    YandexClient - model for client got from Yandex API
    GoogleClient - model for client got from Yandex API
"""


import sys
import json
import math
from datetime import datetime, timezone
from os import path

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship

from model.alchemy.common import Base


class YandexClient(Base):
    """
    ORM model for client got from Yandex API, represents db table ya_clients
    Class fields:
    file_path - path of json file where all options between sessions are stored
    Class methods:
        load_json - loads data from json file and saves them to db
    
    
    properties:
        login - login of client in Yandex Direcr
        token - token to get access to that client from Yandex API
        timestamp - timestap of last update from API
        set_active - is item was set active on the last session in GUI
        campaigns - all campaigns that belong to this client
    """
    __tablename__ = "ya_clients"
    login = Column(String)
    token = Column(String)
    timestamp = Column(DateTime, default=datetime.now)
    set_active = Column(Boolean)
    campaigns = relationship("YandexCampaign", backref="client")

    file_path = path.abspath(
        path.join("settings", "clients.json")
    )

    @classmethod
    def load_json(cls, session):

        if not path.isfile(cls.file_path):
            return
        with open(cls.file_path, "r") as file:
            data = [
                YandexClient(
                    login=client["login"],
                    token=client.get("token", None),
                    timestamp=datetime.fromtimestamp(client["timestamp"]),
                    set_active=client["set_active"]
                )
                for client in json.load(file)
            ]
            session.bulk_save_objects(data)

    @classmethod
    def save_json(cls, session):
        data = [
            {
                "login": client.login,
                "token": client.token,
                "timestamp": math.floor(client.timestamp.timestamp()),
                "set_active": client.set_active
            }
            for client in session.query(YandexClient).all()
        ]
        with open(cls.file_path, "w+") as file:
            json.dump(data, file)

    @classmethod
    def update_from_api(cls, session, clients):
        persisted_clients_logins = {
            login for login in session.query(YandexClient.login).all()
        }
        api_clients_logins = {
            client.login for client in clients
        }

        logins_to_add = api_clients_logins - persisted_clients_logins

        for client in clients:
            if client.login in logins_to_add:
                session.add(
                    YandexClient(login=client.login)
                )
            else:
                session.query(YandexClient) \
                    .get(client.login) \
                    .timestamp = datetime.now()
        session.commit()

    @classmethod
    def add_single(cls, session, item):
        session.add(YandexClient(login=item.login, token=item.token))
        session.commit()
        return session.query(YandexClient).get(item.login)
