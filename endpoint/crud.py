import typing as t

from flask import abort
from flask import current_app


from shared.models import Campaign
from shared.models import AdGroup
from shared.models import SearchTerm


def search(by: str, value: str) -> t.List:
    if by not in ("structure_value", "alias"):
        raise ValueError(f"Unexpected value {by}.")

    if by == "structure_value":
        campaigns = Campaign.manager(current_app.database).find(
            structure_value=value,
        )
        if not campaigns:
            abort(404)

        return SearchTerm.manager(current_app.database).get_roas_by_campaign(
            campaigns, limit=10
        )

    else:
        adgroups = AdGroup.manager(current_app.database).find(alias=value)
        if not adgroups:
            abort(404)

        return SearchTerm.manager(current_app.database).get_roas_by_adgroup(
            adgroups, limit=10
        )
