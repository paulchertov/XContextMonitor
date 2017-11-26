"""
SQLAlchemy model for ad group items for Yandex and Google API
Classes:
    YandexAdGroup - model for ad group got from Yandex API
    GoogleAdGroup - model for ad group got from Google API
"""
from typing import List

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from model.alchemy.common import Base


class YandexAdGroup(Base):
    """
    DB model for Yandex API campaign
    Class methods:
        update_from_api - saves to db list of YaAPIDirectAdGroup
    """
    __tablename__ = "ya_ad_groups"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    ads = relationship("YandexAd", backref="group")
    campaign_id = Column(Integer, ForeignKey("ya_campaigns.id"))

    @classmethod
    def update_from_api(cls, session, groups: List):
        """
        Parses provided YaAPIDirectAdGroup and saves all
        ad groups to db
        :param groups: list of YaAPIDirectAdGroup
        :param session: SQLAlchemy session
        :return: None
        """
        db_groups = [
            YandexAdGroup(
                id=group.id,
                name=group.name,
                campaign_id=group.campaign_id
            )
            for group in groups
        ]
        session.bulk_save_objects(db_groups)
        session.commit()