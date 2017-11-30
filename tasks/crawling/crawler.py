"""
Module with crawler, checking landing pages
classes:
    SiteCrawler - crawler checking all provided urls
"""

from typing import List
from random import randint
from requests import Session
from tasks.crawling.agents import get_user_agent


def get_warnings(response)->str:
    """
    Inner function that gets all warnings for url
    :param response: requests.response of corresponding page
    :return: string of all warnings
    """
    warnings = ""
    warnings += get_redir_warning(response)
    return warnings


def get_redir_warning(response):
    """
    Inner function that if redirects was returns warning about
    redirect with redirects history
    in -status -> target url format
    empty string otherwise
    :param response: requests.response of corresponding page
    :return: warning string about how redirects was handled if was
    else - empty string
    """
    if response.history:
        warning = "\n Было перенаправлено:"
        for path in response.history:
            warning += f"-{path.status_code} -> {path.url};"
        return warning
    return ""


class SiteCrawler:
    """
    Crawler for crawling single clients urls
    generally should be used as iterator
    """
    def __init__(self, thread, urls: List[str]):
        self.__thread = thread
        # thread in which crawler runs

        self.__session: Session
        # request session (stores cookies)

        self.__session_expires_after: int
        # requests left till starting new session

        self.new_session()
        self.__urls = urls

    def new_session(self):
        """
        Creating new session with random user agent
        and defining how much requests it will last
        :return: None
        """
        self.__session = Session()
        self.__session.headers.update(
            {
                'user-agent': get_user_agent(),
                'accept-language': "ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4"
            }
        )
        self.__session_expires_after = randint(1, 10)

    def __iter__(self):
        while self.__urls:
            self.__thread.msleep(randint(300, 1000))
            if not self.__session_expires_after:
                self.__session.close()
                self.new_session()
            url = self.__urls.pop(0)
            try:
                response = self.__session.get(url, allow_redirects=True)
                yield url, str(response.status_code), get_warnings(response)
            except Exception as e:
                yield url, str(e), ""
            self.__session_expires_after -= 1

        self.__session.close()

    @property
    def empty(self):
        return not self.__urls

    def close(self):
        self.__session.close()
