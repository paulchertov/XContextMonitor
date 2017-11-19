"""
Tasks (QT Threads) that work with Yandex API
Classes:
    GetDirectClients - Yandex API request that gets all agency clients
    GetDirectCampaigns - Yandex API request that gets all campaigns for
    each (login, token) pairs
    GetDirectAdGroups - Yandex API request that gets all by provided
    (login, token) pairs
    GetDirectAds - Yandex API request that gets all by provided
    (login, token) pairs
"""

from typing import List, Dict, Tuple

from PyQt5.QtCore import QThread, pyqtSignal

from model.api_items.yandex import YaAPIDirectClient, YaAPIDirectCampaign, \
    YaAPIDirectAdGroup, YaAPIDirectAd, YaAPIDirectLinksSet
from tasks.api.errors import YaApiException
from tasks.api.yandex_utils import YaApiUnits, \
    ya_api_get_request, ya_api_get_all


def split_by_n(items: List, n: int)->List[List]:
    """
    function for internal use that
    splits list to lists with no more than n items length
    :param items: list to be splitted
    :param n: maximum length of sublist
    :return: sublists of n or less length
    """
    item_packs = []
    while len(items) > n:
        item_packs.append(items[:n])
        items = items[n:]
    item_packs.append(items)
    return item_packs


class GetDirectClients(QThread):
    """
    Yandex API request that gets all agency 
    clients from Yandex Direct API
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
                "SelectionCriteria": {"Archived": "NO"},
                "FieldNames": ["Login"]
            }
            units, clients, _, err = ya_api_get_request(
                "agencyclients", "Clients", params, self.token
            )
            if units:
                self.got_units.emit(units)

            if err:
                self.error_occurred.emit(err)
            clients = YaAPIDirectClient.from_api_answer(self.token, clients)
            if clients:
                self.got_clients.emit(clients)
        except Exception as e:
            self.error_occurred.emit(e)


class GetDirectCampaigns(QThread):
    """
    Yandex API request that gets all campaigns of target client 
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
                        "Types": ["TEXT_CAMPAIGN"],
                        "States":
                            ["CONVERTED", "ENDED", "OFF", "ON", "SUSPENDED"],
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

            campaigns = YaAPIDirectCampaign.from_api_answer(login, campaigns)
            if campaigns:
                self.got_campaigns.emit(campaigns)

            if err:
                self.error_occurred.emit(err)
            self.sleep(1)


class GetDirectAdGroups(QThread):
    """
    Yandex API request that gets all ad groups by login and
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
                # api can not return more than 10 campaigns per call
                campaigns_packs = split_by_n(campaigns, 10)

                for campaigns_pack in campaigns_packs:
                    params = {
                        "SelectionCriteria":
                            {
                                "CampaignIds": campaigns_pack,
                                "Types": ["TEXT_AD_GROUP"]
                            },
                        "FieldNames": ["Id", "Name", "CampaignId", "Type"]
                    }
                    units, ad_groups, err = ya_api_get_all(
                        "adgroups", "AdGroups", params, token, login
                    )
                    if units:
                        self.got_units.emit(units)

                    ad_groups = YaAPIDirectAdGroup.from_api_answer(ad_groups)
                    if ad_groups:
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
    Yandex API request that gets all ads by login and token 
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
            for (login, token), campaigns in self.data.items():
                campaigns_packs = split_by_n(campaigns, 10)
                # api can not return more than 10 campaigns per call

                for campaigns_pack in campaigns_packs:
                    params = {
                        "SelectionCriteria": {"CampaignIds": campaigns_pack},
                        "FieldNames": ["Id", "CampaignId", "AdGroupId"],
                        "TextAdFieldNames": ["Href", "SitelinkSetId"]
                    }
                    units, ads, err = ya_api_get_all(
                        "ads", "Ads", params, token, login
                    )

                    if units:
                        self.got_units.emit(units)

                    ads = YaAPIDirectAd.from_api_answer(ads)
                    if ads:
                        self.got_ads.emit(login, ads)

                    if err:
                        self.error_occurred.emit(err)
                        break
                    self.sleep(1)
                self.got_client.emit()
        except Exception as err:
            self.error_occurred.emit(err)


class GetDirectLinks(QThread):
    """
    Yandex API request call that gets all links grouped by 
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
        """
        :param data: dictionary with 
            keys: tuple of (login, token)
            values: links sets ids lists
        """
        super().__init__()
        self.data: Dict[Tuple[str, str], List[int]] = data

    def run(self):
        try:
            for (login, token), links_sets in self.data.items():
                # no more than 10 000 linksets can be returned per call
                links_sets_packs = split_by_n(links_sets, 10_000)

                for links_sets_pack in links_sets_packs:
                    params = {
                        "SelectionCriteria": {"Ids": links_sets_pack},
                        "FieldNames": ["Id", "Sitelinks"]
                    }
                    units, sets, err = ya_api_get_all(
                        "sitelinks", "SitelinksSets", params, token, login
                    )
                    if units:
                        self.got_units.emit(units)

                    sets = YaAPIDirectLinksSet.from_api_answer(sets)
                    if sets:
                        self.got_links.emit(sets)

                    if err:
                        self.error_occurred.emit(err)
                        break
                    self.sleep(1)
                self.got_client.emit()
        except Exception as err:
            self.error_occurred.emit(err)
