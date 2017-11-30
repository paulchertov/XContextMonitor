"""
Module with tasks for crawling pages
classes:
    CheckUrls - task for checking URLS of one client
"""
from typing import Dict, List

from PyQt5.QtCore import QThread, pyqtSignal

from tasks.crawling.crawler import SiteCrawler


class CheckUrls(QThread):
    """
    Crawling task for checking all provided urls
    (generally all pages of one client)
    :emits got_url(url, status_code, warnings): emits when
    one particular page is parsed
        url - url of parsed page
        status_code - status code of parsed page as string
        warnings - all warnings as single string
    """
    got_url = pyqtSignal(str, str, str)

    def __init__(self, pages_by_login: Dict[str, List[str]]):
        """
        :param pages_by_login: dictionary where 
            keys - clients logins
            values - lists of urls belonging to one client
        """
        super().__init__()
        self.crawlers = [
            iter(SiteCrawler(self, pages))
            for login, pages in pages_by_login.items()
        ]

    def run(self):
        while self.crawlers:
            crawler = self.crawlers.pop(0)
            try:
                url, answer, warnings = crawler.__next__()
            except StopIteration:
                pass
            else:
                self.got_url.emit(url, answer, warnings)
                self.crawlers.append(crawler)
