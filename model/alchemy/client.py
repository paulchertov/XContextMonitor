"""
SQLAlchemy model for client items for Yandex and Google API
Classes:
    YandexClient - model for client got from Yandex API
    GoogleClient - model for client got from Google API
"""


import json
import math
from datetime import datetime
from os import path
from typing import List

from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.orm import relationship

from model.alchemy.common import Base


class YandexClient(Base):
    """
    ORM model for client got from Yandex API, represents db table ya_clients
    Class fields:
    file_path - path of json file where all options between sessions are stored
    Class methods:
        load_json - loads data from json file and saves them to db
        save_json - saves all clients from db to json file
        update_from_api - parses provided Yandex API clients response and 
        saves all clients to db
        add_single - saves API wrapper item to db
        
    properties:
        login - login of client in Yandex Direcr
        token - token to get access to that client from Yandex API
        timestamp - timestap of last update from API
        set_active - is item was set active on the last session in GUI
        campaigns - all campaigns that belong to this client
    """
    __tablename__ = "ya_clients"
    login = Column(String, primary_key=True)
    token = Column(String)
    timestamp = Column(DateTime, default=datetime.now)
    set_active = Column(Boolean)
    campaigns = relationship("YandexCampaign", backref="client")

    file_path = path.abspath(
        path.join("settings", "clients.json")
    )

    @classmethod
    def load_json(cls, session):
        """
        Loads all saved clients from json and saves them to db
        :param session: SQLAlchemy session
        :return: None
        """
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
            session.commit()

    @classmethod
    def save_json(cls, session):
        """
        Saves all clients from db to json file
        :param session: SQLAlchemy session
        :return: None
        """
        data = [
            {
                "login": client.login,
                "token": client.token,
                "timestamp": math.floor(client.timestamp.timestamp()),
                "set_active": client.set_active
            }
            for client in session.query(YandexClient).all()
        ]
        print(cls.file_path)
        print(data)
        with open(cls.file_path, "w+") as file:
            json.dump(data, file)

    @classmethod
    def update_from_api(cls, session, clients: List):
        """
        Parses provided Yandex API clients response and saves all
        clients to db
        :param clients: list of clients from Yandex API
        :param session: SQLAlchemy session
        :return: None
        """
        persisted_clients_logins = {
            login[0] for login in session.query(YandexClient.login).all()
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
        """
        Saves API wrapper item to db
        :param session: SQLAlchemy session
        :param item: YaAPIDirectClient to save
        :return: created YandexClient 
        """
        session.add(YandexClient(login=item.login, token=item.token))
        session.commit()
        return session.query(YandexClient).get(item.login)
