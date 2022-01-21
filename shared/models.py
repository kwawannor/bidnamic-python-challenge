import datetime

from core import database


class AdGroup(database.Model):
    ad_group_id: str
    campaign_id: str
    alias: str
    status: str


class Campaign(database.Model):
    campaign_id: str
    structure_value: str
    status: str


class SearchTerm(database.Model):
    date: datetime.date
    ad_group_id: str
    campaign_id: str
    clicks: int
    cost: float
    conversion_value: int
    conversions: int
    search_term: str
