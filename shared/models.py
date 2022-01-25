import typing as t

import datetime
import decimal

from core import database


class AdGroup(database.Model):
    ad_group_id: int
    campaign_id: int
    alias: str
    status: str

    class Meta(database.Model.Meta):
        fields_database_types = {
            "ad_group_id": ("bigint",),
            "campaign_id": ("bigint",),
        }


class Campaign(database.Model):
    campaign_id: int
    structure_value: str
    status: str

    class Meta(database.Model.Meta):
        fields_database_types = {
            "campaign_id": ("bigint",),
        }


class SearchTermManager(database.Manager):
    def _get_roas(
        self,
        *,
        adgroups: t.List[AdGroup] = None,
        campaigns: t.List[Campaign] = None,
        limit=1,
    ):
        """

        Get ROAS
        """

        if (adgroups or campaigns) is None:
            raise ValueError("Expecting 'adgroups' or 'campaigns'")

        if adgroups:
            field = "ad_group_id"
            field_value = tuple(_.ad_group_id for _ in adgroups)

        if campaigns:
            field = "campaign_id"
            field_value = tuple(_.campaign_id for _ in campaigns)

        query_args = (field_value, limit)

        query = (
            f"SELECT * FROM {self.get_table_name()} "
            f"WHERE {field} IN %s AND conversion_value > 0 AND cost > 0 "
            "ORDER BY conversion_value / cost DESC LIMIT %s"
        )

        query_args = (field_value, limit)
        search_terms = self.query(query, query_args)

        return search_terms

    def get_roas_by_adgroup(
        self,
        adgroups: t.List[AdGroup],
        limit,
    ):
        return self._get_roas(adgroups=adgroups, limit=limit)

    def get_roas_by_campaign(
        self,
        campaigns: t.List[Campaign],
        limit,
    ):
        return self._get_roas(campaigns=campaigns, limit=limit)


class SearchTerm(database.Model):
    date: datetime.date
    ad_group_id: int
    campaign_id: int
    clicks: int
    cost: decimal.Decimal
    conversion_value: decimal.Decimal
    conversions: int
    search_term: str

    class Meta(database.Model.Meta):
        manager = SearchTermManager
        fields_database_types = {
            "ad_group_id": ("bigint",),
            "campaign_id": ("bigint",),
        }
