"""
Module with DB tasks for working with ads tables in db
Classes:
    SaveAdsFromAPI - tasks that saves API items to DB
"""

from typing import List

from sqlalchemy import and_
from PyQt5.QtCore import pyqtSignal

from model.alchemy.links import LinkUrl, YandexLinksSet, YandexLink
from model.gui.links import ParsedLink
from tasks.db.common import PQDBTask


class LinkSetsByLoginToken(PQDBTask):
    """
    DB Task that gets links grouped by logins from DB
    and emits the result
    """
    got_sets = pyqtSignal(dict)

    def run(self):
        try:
            self.got_sets.emit(YandexLinksSet.by_login_token(self.session))
        except Exception as e:
            self.error_occurred.emit(e)


class LinksByLogin(PQDBTask):
    """
    DB Task that gets links grouped by login: token pairs from DB
    and emits the result
    """
    got_links = pyqtSignal(dict)

    def run(self):
        try:
            self.got_links.emit(LinkUrl.by_login(self.session))
        except Exception as e:
            self.error_occurred.emit(e)


class SaveLinksFromAPI(PQDBTask):
    """
    DB Task that saves link sets data from API as links in DB
    """
    def __init__(self, link_sets):
        super().__init__()
        self.link_sets = link_sets

    def run(self):
        try:
            YandexLink.update_from_api(self.session, self.link_sets)
        except Exception as e:
            self.error_occurred.emit(e)


class SaveParsedLink(PQDBTask):
    """
    DB Task that saves parsed link to DB
    """

    def __init__(self, url: str, status: str, warning: str):
        super().__init__()
        self.url = url
        self.status = status
        self.warning = warning

    def run(self):
        try:
            LinkUrl.from_response(
                self.session, self.url, self.status, self.warning
            )
        except Exception as e:
            self.error_occurred.emit(e)


class AggregateParsedLinks(PQDBTask):
    """
    DB Task that gets final result: parsed links as GUI model
    """
    got_links = pyqtSignal(list)

    def run(self):
        try:
            errors = LinkUrl.aggregate_links(
                self.session,
                LinkUrl.status != "200",
                "Error"
            )
            warnings = LinkUrl.aggregate_links(
                self.session,
                and_(
                    LinkUrl.status == "200",
                    LinkUrl.warning_text != ""
                ),
                "Warning"
            )
            self.got_links.emit(errors + warnings)
        except Exception as e:
            self.error_occurred.emit(e)
