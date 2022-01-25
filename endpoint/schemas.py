from core import schema


class SearchResultSchema(schema.Schema):

    ad_group = schema.IntegerField(name="ad_group_id")
    campaign = schema.IntegerField(name="campaign_id")
    clicks = schema.IntegerField()
    conversion_value = schema.DecimalField()
    cost = schema.DecimalField()
    search_term = schema.StringField()
    date = schema.DateField()
