"""
SQLAlchemy model for ad items for Yandex and Google API
Classes:
    YandexAd - model for ad got from Yandex API
    GoogleAd - model for ad got from Google API
"""
from typing import List

from sqlalchemy import Column, Integer, String, ForeignKey

from model.alchemy.common import Base


class YandexAd(Base):
    """
    DB model for Yandex API ad
    Class methods:
        update_from_api - saves to db list of YaAPIDirectAd items
    """
    __tablename__ = "ya_ads"
    id = Column(Integer, primary_key=True)
    url = Column(String, nullable=True)
    group_id = Column(Integer, ForeignKey("ya_ad_groups.id"))
    links_set_id = Column(Integer, ForeignKey("ya_links_sets.id"))

    @classmethod
    def update_from_api(cls, session, ads: List):
        """
        Gets YaAPIDirectAd list and saves all
        ads to db. IMPORTANT: should be called after updating all
        link sets
        :param session: SQLAlchemy session
        :param ads: list of ads from Yandex API
        :return: None
        """
        db_ads = [
            YandexAd(
                id=ad.id,
                group_id=ad.group_id,
                url=ad.url,
                links_set_id=ad.links_set
            )
            for ad in ads
        ]
        session.bulk_save_objects(db_ads)
        session.commit()

