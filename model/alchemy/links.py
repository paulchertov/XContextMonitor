"""
SQLAlchemy model for links for Yandex and Google API
and link checked by crawler
Classes:
    YandexLinksSet - model for link set from Yandex API
    YandexLink -  model for link from link set from Yandex API
    LinkUrl - model for link checked by crawler
"""
from typing import List

from sqlalchemy import Column, Integer, String, ForeignKey, Sequence
from sqlalchemy.orm import relationship

from model.alchemy.common import Base
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
        aggregate_links - maps all 
    """
    __tablename__ = "link_urls"
    url = Column(String, primary_key=True)
    status = Column(String)
    warning_text = Column(String)

    @classmethod
    def aggregate_links(cls, session, criteria)-> List[ParsedLink]:
        """
        Gets all links by some criteria
        :param session: SQLAlchemy session
        :param criteria: SQLAlchemy criteria for query
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
                    comment=comment
            )
            for status, url, login, campaign, group, ad, comment in wrong_urls.all()
        ]
