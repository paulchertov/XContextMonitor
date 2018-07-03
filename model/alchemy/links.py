"""
SQLAlchemy model for links for Yandex and Google API
and link checked by crawler
Classes:
    YandexLinksSet - model for link set from Yandex API
    YandexLink -  model for link from link set from Yandex API
    LinkUrl - model for link checked by crawler
"""
from typing import Tuple, List, Dict

from sqlalchemy import Column, Integer, String, ForeignKey, Sequence
from sqlalchemy.orm import relationship

from settings.config import YA_DIRECT_TOKEN
from model.alchemy.common import Base
from model.alchemy.client import YandexClient
from model.alchemy.campaign import YandexCampaign
from model.alchemy.ad_group import YandexAdGroup
from model.alchemy.ad import YandexAd
from model.gui.links import ParsedLink


class YandexLinksSet(Base):
    """
    DB model for Yandex API link set
    Class methods:
        update_from_api - gets data from API answer and saves to db
    """
    __tablename__ = "ya_links_sets"
    id = Column(Integer, primary_key=True)
    ads = relationship("YandexAd", backref="links_set")
    links = relationship("YandexLink", backref="links_set")

    @classmethod
    def by_login_token(cls, session)->Dict[Tuple[str, str], List[str]]:
        """
        Return all link sets grouped by client login
        :param session: SQLAlchemy session
        :return: None
        """
        sets = session \
            .query(
                YandexLinksSet.id,
                YandexClient.login,
                YandexClient.token
            ) \
            .join(YandexAd) \
            .join(YandexAdGroup) \
            .join(YandexCampaign) \
            .join(YandexClient)

        sets_by_login_token = {}
        for set_id, login, token in sets:
            key = (login, token or YA_DIRECT_TOKEN)
            if key in sets_by_login_token:
                sets_by_login_token[key].append(set_id)
            else:
                sets_by_login_token[key] = [set_id]

        return sets_by_login_token

    @classmethod
    def update_from_api(cls, session, ads: List):
        """
        Saves all link sets from provided YaAPIDirectAd list to db
        :param ads: list of YaAPIDirectAds
        :param session: SQLAlchemy session
        :return: None
        """
        new_links_sets = {
            ad.links_set for ad in ads if ad.links_set
        }
        existing_links_sets = {
            id[0]
            for id in session.query(YandexLinksSet.id).all()
        }
        ids_to_add = new_links_sets - existing_links_sets

        db_links_sets = [
            YandexLinksSet(id=id)
            for id in ids_to_add
        ]

        session.bulk_save_objects(db_links_sets)
        session.commit()


class YandexLink(Base):
    """
    DB model for Yandex API link
    Class methods:
        update_from_api - gets data from YaAPIDirectLinksSet list and
        saves sets to db
    """
    __tablename__ = "ya_links"
    id = Column(Integer, Sequence('ya_links_id_seq'), primary_key=True)
    set_id = Column(String, ForeignKey("ya_links_sets.id"))
    url = Column(String)

    @classmethod
    def update_from_api(cls, session, links_sets: List):
        """
        Saves all links from provided YaAPIDirectLinksSet list
        to database
        :param session: SQLAlchemy session 
        :param links_sets: List of YaAPILinksSets
        :return: None
        """
        db_links = [
            YandexLink(url=link, set_id=links_set.id)
            for links_set in links_sets
            for link in links_set.links
        ]
        session.bulk_save_objects(db_links)
        session.commit()


class LinkUrl(Base):
    """
    DB model for parsed link
    Class methods:
        aggregate_links - maps all links by some criteria
        by_logins - gets all links grouped by login
    """
    __tablename__ = "link_urls"
    url = Column(String, primary_key=True)
    status = Column(String)
    warning_text = Column(String)

    @classmethod
    def from_response(cls, session, url: str, status: str, warning: str):
        """
        Creates single entity from provided data
        :param session: SQLAlchemy session
        :param url: url of parsed page
        :param status: status code of page
        :param warning: warning text to be displayed
        :return: None
        """
        session.add(
            LinkUrl(url=url, status=status, warning_text=warning)
        )
        session.commit()

    @classmethod
    def by_login(cls, session)->Dict[Tuple[str, str], List[str]]:
        """
        Return all possible links grouped by client login
        :param session: SQLAlchemy session
        :return: dictionary with 
            keys - login: token pair
            values - lists of links
        """
        main_links_query = session \
            .query(
                YandexAd.url,
                YandexCampaign.client_login,
                YandexClient.token
            ) \
            .join(YandexAdGroup) \
            .join(YandexCampaign) \
            .join(YandexClient)
        additional_links_query = session \
            .query(
                YandexLink.url,
                YandexCampaign.client_login,
                YandexClient.token
            ) \
            .join(YandexLinksSet) \
            .join(YandexAd) \
            .join(YandexAdGroup) \
            .join(YandexCampaign)
        links_query = main_links_query.union(additional_links_query)
        links_by_logins = {}
        all_links = []

        for link, login, token in links_query.all():
            if link is not None and link not in all_links:
                all_links.append(link)
                if login in links_by_logins:
                    links_by_logins[login].append(link)
                else:
                    links_by_logins[login] = [link]
        return links_by_logins

    @classmethod
    def aggregate_links(cls, session, criteria, kind: str)-> List[ParsedLink]:
        """
        Gets all links by some criteria
        :param session: SQLAlchemy session
        :param criteria: SQLAlchemy criteria for query
        :param kind: type of produced GUI model
        :return: List of ParsedLink item (both from additional links
        and ads main links matching provided criteria
        """

        # defining columns for resulting query
        result_columns = (
            LinkUrl.status,
            LinkUrl.url,
            YandexCampaign.client_login,
            YandexCampaign.id,
            YandexAdGroup.id,
            YandexAd.id,
            LinkUrl.warning_text
        )

        # gettings wrong main links in ads
        wrong_ads = session \
            .query(
                *result_columns
            ) \
            .filter(criteria) \
            .join(YandexAd, YandexAd.url == LinkUrl.url) \
            .join(YandexAdGroup) \
            .join(YandexCampaign)

        # getting wrong additional links in ads
        wrong_additional_links = session \
            .query(
                *result_columns
            ) \
            .filter(criteria) \
            .join(YandexLink, YandexLink.url == LinkUrl.url) \
            .join(YandexLinksSet) \
            .join(YandexAd) \
            .join(YandexAdGroup) \
            .join(YandexCampaign)

        # merging results
        wrong_urls = wrong_ads.union(wrong_additional_links)

        return [
            ParsedLink(
                    status=status,
                    url=url,
                    login=login,
                    campaign=campaign,
                    group=group,
                    ad=ad,
                    comment=comment,
					kind=kind
            )
            for status, url, login, campaign, group, ad, comment in wrong_urls.all()
        ]
