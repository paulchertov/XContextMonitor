"""
Module with Yandex API items wrappers - ViewModels for transporting data 
between Yandex API tasks and main thread and between main thread and
database thread and for using as model for view (gui)
Classes:
    YaAPIDirectClient - wrapper for client
    YaAPIDirectCampaign - wrapper for campaign
    YaAPIDirectAdGroup - wrapper for group of ads
    YaAPIDirectAd - wrapper for ad
    YaAPIDirectLinksSet - wrapper for set of links
"""


from typing import Optional, List
from datetime import datetime


class YaAPIDirectClient:
    """
    Simple wrapper for client item from Yandex Direct API
    fields:
        token - API token for client
        login - login in Yandex Direct
    classmethods:
        from_api_answer - create bunch of items from API answer
    """
    def __init__(self, login: str, token: str,
                 timestamp: datetime, is_active: bool):
        """
        :param token: token of Yandex API
        :param login: client login
        :param timestamp: datetime when data was obtained from API
        :param is_active: is item was set active on the last session in GUI
        """
        self.token = token
        self.login = login
        self.timestamp = timestamp
        self.is_active = is_active

    @classmethod
    def from_api_answer(cls, token: str, clients: Optional[List])-> List:
        """
        Creates multiple clients from API answer list
        :param token: token of Yandex API
        :param clients: list of properties returned from Yandex API
        :return: List of YaAPIDirectClients
        """
        if clients:
            return [
                cls(token=token,
                    login=client["Login"],
                    timestamp=datetime.now(),
                    is_active=False)
                for client in clients
            ]
        return []

    @classmethod
    def from_db_items(cls, db_clients):
        return [
            YaAPIDirectClient(
                login=db_client.login,
                token=db_client.token,
                timestamp=db_client.timestamp,
                is_active=db_client.set_active
            )
            for db_client in db_clients
        ]


class YaAPIDirectCampaign:
    """
    Simple wrapper for campaign item from Yandex Direct API
    fields:
        id - campaign id
        name - campaign name
        client_login - login of client to which campaign belongs
    classmethods:
        from_api_answer - create bunch of items from API answer
    """
    def __init__(self, id: int, name: str, client_login: str):
        """
        :param id: campaign id
        :param name: campaign name
        :param client_login: login of client to which campaign belongs
        """
        self.id = id
        self.name = name
        self.client_login = client_login

    @classmethod
    def from_api_answer(cls, login, campaigns: Optional[List])-> List:
        """
        Creates multiple campaigns from API answer list
        :param login: login of client to which campaigns belong
        :param campaigns: list of properties returned from Yandex API
        :return: List of YaAPIDirectCampaigns
        """
        if campaigns:
            return [
                YaAPIDirectCampaign(
                    id=campaign["Id"],
                    name=campaign["Name"],
                    client_login=login
                )
                for campaign in campaigns
            ]
        return []


class YaAPIDirectAdGroup:
    """
    Simple wrapper for ad group item from Yandex Direct API
        fields:
            id - Ad group id
            name - Ad group name
            campaign_id - Id of campaign to which ad group belongs
        classmethods:
            from_api_answer - create bunch of items from API answer
    """
    def __init__(self, id: id, name: str, campaign_id: int):
        """
        :param id: Ad group id
        :param name: Ad group name
        :param campaign_id: Id of campaign to which ad group belongs
        """
        self.id = id
        self.name = name
        self.campaign_id = campaign_id

    @classmethod
    def from_api_answer(cls, ad_groups)-> List:
        """
        Creates multiple ad groups from API answer list
        :param ad_groups: list of properties returned from Yandex API
        :return: List of YaAPIDirectAdGroups
        """
        if ad_groups:
            return [
                YaAPIDirectAdGroup(
                    id=ad_group["Id"],
                    name=ad_group["Name"],
                    campaign_id=ad_group["CampaignId"]
                )
                for ad_group in ad_groups
            ]
        return []

    @classmethod
    def from_db_items(cls, db_groups):
        return [
            YaAPIDirectAdGroup(
                id=db_group.id,
                name=db_group.name,
                campaign_id=db_group.campaign_id
            )
            for db_group in db_groups
        ]


class YaAPIDirectAd:
    """
    Simple wrapper for ad item from Yandex Direct API
    fields:
        id - Ad id
        group_id - Id of ads group to which ad group belongs
        url - Url of ads landing page
        links_set - Id of corresponding links set
    classmethods:
        from_api_answer - create bunch of items from API answer
    """
    def __init__(self, id, group_id, url, links_set):
        """
        :param id: Ad id 
        :param group_id: Id of ads group to which ad group belongs
        :param url: Url of ads landing page
        :param links_set: Id of corresponding links set
        """
        self.id = id
        self.group_id = group_id
        self.url = url
        self.links_set = links_set

    @classmethod
    def from_api_answer(cls, ads)-> List:
        """
        Creates multiple ads from API answer list
        :param ads: list of properties returned from Yandex API
        :return: List of YaAPIDirectAds
        """
        if ads:
            return [
                YaAPIDirectAd(
                    id=ad["Id"],
                    group_id=ad["AdGroupId"],
                    links_set=ad["TextAd"].get("SitelinkSetId", None)
                    if "TextAd" in ad else None,
                    url=ad["TextAd"].get("Href", None)
                    if "TextAd" in ad else None
                )
                for ad in ads
            ]
        return []


class YaAPIDirectLinksSet:
    """
    Simple wrapper for links set item from Yandex Direct API
    fields:
        id - Links set id
        links - List of urls to which links reference
    classmethods:
        from_api_answer - create bunch of items from API answer
    """
    def __init__(self, id: int, links: List):
        """
        :param id: Links set id
        :param links: List of urls to which links reference
        """
        self.id = id
        self.links = links

    @classmethod
    def from_api_answer(cls, sets: List)-> List:
        """
        Creates multiple ads from API answer list
        :param sets: list of properties returned from Yandex API
        :return: List of YaAPIDirectLinksSets
        """
        if sets:
            return [
                YaAPIDirectLinksSet(
                    id=links_set["Id"],
                    links=[
                        link["Href"] for link in links_set["Sitelinks"]
                        if "Href" in link
                    ] if "Sitelinks" in links_set else []
                )
                for links_set in sets
            ]
        return []
