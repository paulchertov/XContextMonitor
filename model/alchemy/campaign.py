"""
SQLAlchemy model for campaign items for Yandex and Google API
Classes:
    YandexCampaign - model for campaign got from Yandex API
    GoogleCampaign - model for campaign got from Google API
    CampaignsList - data type of campaign ids list
    GroupedCampaigns - data type of campaigns grouped by (login, token) pairs
"""
from typing import Dict, List

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from model.alchemy.common import Base, LoginTokenPair
from model.alchemy.client import YandexClient
from settings.config import YA_DIRECT_TOKEN


CampaignsList = List[int]

# Dict where keys: are (login, token tuple)
# values: are lists of campaigns ids
GroupedCampaigns = Dict[LoginTokenPair, CampaignsList]


class YandexCampaign(Base):
    """
    DB model for Yandex API campaign
    Class methods:
        update_from_api - gets data from API answer and saves to db
        by_login_and_token - gets campaigns grouped by (login, token) pairs
    """
    __tablename__ = "ya_campaigns"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    client_login = Column(String, ForeignKey("ya_clients.login"))
    ad_groups = relationship("YandexAdGroup", backref="campaign")

    @classmethod
    def by_login_and_token(cls, session)->GroupedCampaigns:
        """
        returns campaigns grouped by (login, token) pairs
        :param session: SQLAlchemy session
        :return: GroupedCampaigns of all campaigns
        """
        campaigns = session.\
            query(YandexCampaign, YandexClient.token)\
            .join(YandexClient)\
            .all()

        campaigns_by_login: GroupedCampaigns = {}
        for campaign, token in campaigns:
            key: LoginTokenPair = (
                campaign.client_login,
                token or YA_DIRECT_TOKEN
            )
            if key in campaigns_by_login:
                campaigns_by_login[key].append(campaign.id)
            else:
                campaigns_by_login[key] = [campaign.id]
        return campaigns_by_login

    @classmethod
    def update_from_api(cls, session, campaigns: List):
        """
        Parses provided Yandex API campaigns items and saves all
        campaigns to db
        :param campaigns: List of YaAPIDirectCampaign items
        :param session: SQLAlchemy session
        :return: None
        """
        db_campaigns = [
            YandexCampaign(
                id=campaign.id,
                name=campaign.name,
                client_login=campaign.client_login
            )
            for campaign in campaigns
        ]
        session.bulk_save_objects(db_campaigns)
        session.commit()
