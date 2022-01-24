from datetime import date

from unittest import mock

from shared.models import Campaign
from shared.models import SearchTerm


@mock.patch("endpoint.crud.get_campaigns")
@mock.patch.object(SearchTerm, "manager")
def test_search_by_campaign(mock_manager, mock_get_campaigns, testclient):
    class Manager:
        get_roas_by_campaign = mock.Mock(
            return_value=[
                SearchTerm(
                    date=date(2020, 11, 9),
                    ad_group_id=61228310066,
                    campaign_id=1578411800,
                    clicks=2,
                    cost=0.28,
                    conversion_value=2,
                    conversions=0,
                    search_term="nike kawa infant slide",
                ),
                SearchTerm(
                    date=date(2021, 12, 9),
                    ad_group_id=81713176441,
                    campaign_id=1578411800,
                    clicks=2,
                    cost=0.11,
                    conversion_value=2,
                    conversions=0,
                    search_term="nike hat pink",
                ),
            ]
        )

    mock_manager.return_value = Manager

    response = testclient.get("/search?term=structure_value&value=nike")
    response_data = response.get_json()
    response_results = response_data["results"]

    assert mock_get_campaigns.called_with("nike")
    assert Manager.get_roas_by_campaign.call_args.kwargs == {
        "limit": testclient.testapp.config["ROAS_SEARCH_LIMIT"],
    }

    assert response_results[0]["ad_group"] == 61228310066
    assert response_results[0]["campaign"] == 1578411800
    assert response_results[0]["clicks"] == 2
    assert response_results[0]["cost"] == "0.28"
    assert response_results[0]["conversion_value"] == "2"
    assert response_results[0]["date"] == "2020-11-09"
    assert response_results[0]["search_term"] == "nike kawa infant slide"


@mock.patch("endpoint.crud.get_adgroups")
@mock.patch.object(SearchTerm, "manager")
def test_search_by_adgroup(mock_manager, mock_get_adgroups, testclient):
    class Manager:
        get_roas_by_adgroup = mock.Mock(
            return_value=[
                SearchTerm(
                    date=date(2020, 11, 9),
                    ad_group_id=61228310066,
                    campaign_id=1578411800,
                    clicks=2,
                    cost=0.28,
                    conversion_value=2,
                    conversions=0,
                    search_term="nike kawa infant slide",
                ),
                SearchTerm(
                    date=date(2021, 12, 9),
                    ad_group_id=81713176441,
                    campaign_id=1578411800,
                    clicks=2,
                    cost=0.11,
                    conversion_value=2,
                    conversions=0,
                    search_term="nike hat pink",
                ),
            ]
        )

    mock_manager.return_value = Manager

    response = testclient.get(
        "/search?term=alias&value=Shift - Shopping - GB - venum - LOW - "
        "monkey-ack-robert-comet - 817ce4882dfc499886ca8670ccd5cbf9"
    )
    response_data = response.get_json()
    response_results = response_data["results"]

    assert Manager.get_roas_by_adgroup.call_args.kwargs == {
        "limit": testclient.testapp.config["ROAS_SEARCH_LIMIT"],
    }

    assert response_results[0]["ad_group"] == 61228310066
    assert response_results[0]["campaign"] == 1578411800
    assert response_results[0]["clicks"] == 2
    assert response_results[0]["cost"] == "0.28"
    assert response_results[0]["conversion_value"] == "2"
    assert response_results[0]["date"] == "2020-11-09"
    assert response_results[0]["search_term"] == "nike kawa infant slide"
