from typing import List, Dict, Tuple
from collections import namedtuple

from PyQt5.QtCore import QThread, pyqtSignal

from services.tasks.yandex_utils import YaApiUnits, \
    ya_api_get_request, ya_api_get_all, ya_api_action_request
from services.tasks.errors import YaApiException


# TODO: Move to model
YaAPIDirectClient = namedtuple("YaAPIDirectClient", "id login")
YaAPIDirectCampaign = namedtuple("YaAPIDirectCampaign", "id name client_login")
YaAPIDirectAdGroup = namedtuple("YaAPIDirectAdGroup", "id name campaign_id")
YaAPIDirectAd = namedtuple("YaAPIDirectAd", "id group_id url links_set")
YaAPIDirectLinkSet = namedtuple("YaAPIDirectLinkSe", "id links")


class GetDirectClients(QThread):
    """
    Cmd call that gets all agency clients from Yandex Direct API
    And emits:
    Remained Yandex API units
    Clients if everything is ok
    Error otherwise
    """
    got_clients = pyqtSignal(list)
    got_units = pyqtSignal(YaApiUnits)
    error_occurred = pyqtSignal(Exception)

    def __init__(self, token: str):
        """
        :param token: str token to Yandex Direct API 
        """
        super().__init__()
        self.token = token

    def run(self):
        try:
            params = {
                # ignoring archived clients
                "SelectionCriteria": {"Archived": "NO"},
                # getting only id and logins
                "FieldNames": ["ClientId", "Login"]
            }
            units, clients, _, err = ya_api_get_request(
                "agencyclients", "Clients", params, self.token
            )
            if units:
                self.got_units.emit(units)

            if err:
                self.error_occurred.emit(err)

            if clients:
                clients = [
                    YaAPIDirectClient(id=client["ClientId"],
                                      login=client["Login"])
                    for client in clients
                ]
                self.got_clients.emit(clients)
        except Exception as e:
            self.error_occurred.emit(e)


class GetDirectCampaigns(QThread):
    """
    Cmd call that gets all campaigns of target client 
    from Yandex Direct API
    And emits:
    Remained Yandex API units
    Campaigns if everything is ok
    Error otherwise
    """
    got_campaigns = pyqtSignal(list)
    got_units = pyqtSignal(YaApiUnits)
    error_occurred = pyqtSignal(YaApiException)

    def __init__(self, data: List[Tuple[str, str]]):
        """
        :param data: list of tuples (login, token)
        """
        super().__init__()
        self.data = data

    def run(self):
        for login, token in self.data:
            params = {
                "SelectionCriteria":
                    {
                        # only text campaigns
                        "Types":
                            ["TEXT_CAMPAIGN"],
                        # all Types except archived
                        "States":
                            ["CONVERTED", "ENDED", "OFF", "ON", "SUSPENDED"],
                        # all Statuses except archived
                        "Statuses":
                            ["ACCEPTED", "DRAFT", "MODERATION", "REJECTED"],
                    },
                "FieldNames": ["Id", "Name"]
            }
            units, campaigns, err = ya_api_get_all(
                "campaigns", "Campaigns", params, token, login
            )
            if units:
                self.got_units.emit(units)

            # TODO: move to models method
            if campaigns:
                campaigns = [
                    YaAPIDirectCampaign(
                        id=campaign["Id"],
                        name=campaign["Name"],
                        client_login=login
                    )
                    for campaign in campaigns
                ]
                self.got_campaigns.emit(campaigns)

            if err:
                self.error_occurred.emit(err)
            self.sleep(1)


class GetDirectAdGroups(QThread):
    """
    Cmd call that gets all ad groups by login and
    token from Yandex Direct API
    And emits:
    Remained Yandex API units
    Empty signal when one of the clients campaigns got
    Ad groups if everything is ok
    Error otherwise
    """
    got_ad_groups = pyqtSignal(list)
    got_units = pyqtSignal(YaApiUnits)
    got_client = pyqtSignal()
    error_occurred = pyqtSignal(Exception)

    def __init__(self, data: Dict[Tuple[str, str], List[int]]):
        """
        :param data: dictionary with 
            keys: tuple of (login, token)
            values: campaigns ids lists
        """
        super().__init__()
        self.data: Dict[Tuple[str, str], List[int]] = data

    def run(self):
        try:
            for (login, token), campaigns in self.data.items():
                campaigns_packs = []
                # api can not return more than 10 campaigns per call
                # TODO: move to separate function
                while len(campaigns) > 10:
                    campaigns_packs.append(campaigns[:10])
                    campaigns = campaigns[10:]
                campaigns_packs.append(campaigns)

                for campaigns_pack in campaigns_packs:
                    params = {
                        "SelectionCriteria":
                            {
                                # only for provided campaigns
                                "CampaignIds": campaigns_pack,
                                # only text ads
                                "Types": ["TEXT_AD_GROUP"]
                            },
                        "FieldNames": ["Id", "Name", "CampaignId", "Type"]
                    }
                    units, ad_groups, err = ya_api_get_all(
                        "adgroups", "AdGroups", params, token, login
                    )
                    if units:
                        self.got_units.emit(units)

                    # TODO: move to models method
                    if ad_groups:
                        ad_groups = [
                            YaAPIDirectAdGroup(
                                id=ad_group["Id"],
                                name=ad_group["Name"],
                                campaign_id=ad_group["CampaignId"]
                            )
                            for ad_group in ad_groups
                        ]
                        self.got_ad_groups.emit(ad_groups)

                    if err:
                        self.error_occurred.emit(err)
                        break
                    self.sleep(1)
                self.got_client.emit()
        except Exception as err:
            self.error_occurred.emit(err)


class GetDirectAds(QThread):
    """
    Cmd call that gets all ads by login and token 
    from Yandex Direct API
    And emits:
    Remained Yandex API units
    Empty signal when one of the clients campaigns got
    Ad groups if everything is ok
    Error otherwise
    """
    got_ads = pyqtSignal(str, list)
    got_units = pyqtSignal(YaApiUnits)
    got_client = pyqtSignal()
    error_occurred = pyqtSignal(Exception)

    def __init__(self, data: Dict[Tuple[str, str], List[int]]):
        """
        :param data: dictionary with 
            keys: tuple of (login, token)
            values: campaigns ids lists
        """
        super().__init__()
        self.data: Dict[Tuple[str, str], List[int]] = data

    def run(self):
        try:
            for login, campaigns in self.data.items():
                campaigns_packs = []
                # TODO: move to separate function
                # api can not return more than 10 campaigns per call
                while len(campaigns) > 10:
                    campaigns_packs.append(campaigns[:10])
                    campaigns = campaigns[10:]
                campaigns_packs.append(campaigns)
                for campaigns_pack in campaigns_packs:
                    params = {
                        "SelectionCriteria":
                            {
                                "CampaignIds": campaigns_pack
                            },
                        "FieldNames": ["Id", "CampaignId", "AdGroupId"],
                        "TextAdFieldNames": ["Href", "SitelinkSetId"]
                    }
                    units, ads, err = ya_api_get_all(
                        "ads", "Ads", params, login[1], login[0]
                    )
                    if units:
                        self.got_units.emit(units)

                    # TODO: move to models method
                    if ads:
                        ads = [
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
                        self.got_ads.emit(login[0], ads)

                    if err:
                        self.error_occurred.emit(err)
                        break
                    self.sleep(1)
                self.got_client.emit()
        except Exception as err:
            self.error_occurred.emit(err)


class GetDirectLinks(QThread):
    """
    Cmd call that gets all links grouped by 
    login and token from Yandex Direct API
    And emits:
    Remained Yandex API units
    Empty signal when one of the clients campaigns got
    Ad groups if everything is ok
    Error otherwise
    """
    got_links = pyqtSignal(list)
    got_units = pyqtSignal(YaApiUnits)
    got_client = pyqtSignal()
    error_occurred = pyqtSignal(Exception)

    def __init__(self, data: Dict[Tuple[str, str], List[int]]):
        super().__init__()
        self.data: Dict[Tuple[str, str], List[int]] = data

    def run(self):
        try:
            for (login, token), links_sets in self.data.items():
                links_sets_packs = []
                # TODO: move to separate function
                # no more than 10 000 linksets can be returned per call
                while len(links_sets) > 10_000:
                    links_sets_packs.append(links_sets[:10_000])
                    links_sets = links_sets[10_000:]
                links_sets_packs.append(links_sets)

                for links_sets_pack in links_sets_packs:
                    params = {
                        "SelectionCriteria":
                            {
                                "Ids": links_sets_pack
                            },
                        "FieldNames": ["Id", "Sitelinks"]
                    }
                    units, sets, err = ya_api_get_all(
                        "sitelinks", "SitelinksSets", params, login[1], login[0]
                    )
                    if units:
                        self.got_units.emit(units)

                    # TODO: move to models method
                    if sets:
                        sets = [
                            YaAPIDirectLinkSet(
                                id=links_set["Id"],
                                links=[
                                    link["Href"] for link in links_set["Sitelinks"]
                                    if "Href" in link
                                ] if "Sitelinks" in links_set else []
                            )
                            for links_set in sets
                        ]
                        self.got_links.emit(sets)

                    if err:
                        self.error_occurred.emit(err)
                        break
                    self.sleep(1)
                self.got_client.emit()
        except Exception as err:
            self.error_occurred.emit(err)
