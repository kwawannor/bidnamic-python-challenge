import typing as t

from flask import abort

from shared.models import Campaign
from shared.models import AdGroup
from shared.models import SearchTerm


def search(by: str) -> t.List:
    if by not in ("structure_value", "alias"):
        raise ValueError(f"Unexpected value {by}.")

    if by == "structure_value":
        campaign = Campaign.manager().get(structure_value=by)
        if not campaign:
            abort(404)

        return SearchTerm.get_roas_by_campaign(campaign, limit=10)

    else:
        adgroup = AdGroup.manager().get(alias=by)
        if not adgroup:
            abort(404)

        return SearchTerm.get_roas_by_adgroup(adgroup, limit=10)
