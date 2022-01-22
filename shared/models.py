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
        fields_database_types = {
            "ad_group_id": ("bigint",),
            "campaign_id": ("bigint",),
        }

    def _get_roas(
        self,
        *,
        ad_group_id: int = None,
        campaign_id: int = None,
        limit=10,
    ):
        """

        Get ROAS
        """

        if (ad_group_id or campaign_id) is None:
            raise ValueError("Expecting 'ad_group_id' or 'campaign_id'")

        if ad_group_id:
            typ = "ad_group_id"
            val = ad_group_id

        if campaign_id:
            typ = "campaign_id"
            val = campaign_id

        manager = self.manager()

        query = (
            f"SELECT * FROM {self.get_table_name()}"
            f"WHERE {typ}=%s AND conversion_value > 0 AND cost > 0"
            "ORDER BY conversion_value / cost DESC LIMIT %s"
        )
        query_args = (val, limit)
        search_terms = manager.query(query, query_args)

        return search_terms

    def get_roas_by_adgroup(self, adgroup: AdGroup, /, limit=10):
        return self._get_roas(ad_group_id=adgroup.ad_group_id)

    def get_roas_by_campaign(self, campaign: Campaign, /, limit=10):
        return self._get_roas(campaign_id=campaign.campaign_id)
