import typing as t

from flask import abort
from flask import current_app


from shared.models import Campaign
from shared.models import AdGroup
from shared.models import SearchTerm


def search(by: str, value: str) -> t.List:
    if by not in ("structure_value", "alias"):
        raise ValueError(f"Unexpected value {by}.")

    search_limit = current_app.config["ROAS_SEARCH_LIMIT"]

    if by == "structure_value":
        manager = SearchTerm.manager(current_app.database)
        return manager.get_roas_by_campaign(
            get_campaigns(value),
            limit=search_limit,
        )

    else:
        manager = SearchTerm.manager(current_app.database)
        return manager.get_roas_by_adgroup(
            get_adgroups(value),
            limit=search_limit,
        )


def get_campaigns(structure_value: str) -> t.List[Campaign]:
    campaigns = Campaign.manager(current_app.database).find(
        structure_value=structure_value,
    )
    if not campaigns:
        abort(404)

    return campaigns


def get_adgroups(alias: str) -> t.List[AdGroup]:
    adgroups = AdGroup.manager(current_app.database).find(alias=alias)
    if not adgroups:
        abort(404)

    return adgroups
