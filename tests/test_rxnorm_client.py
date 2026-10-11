
from unittest.mock import Mock, patch

from app.core.rxnorm_client import search_medicine


@patch("app.core.rxnorm_client.requests.get")
def test_search_medicine_returns_candidates(mock_get):
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "approximateGroup": {
            "candidate": [
                {
                    "rxcui": "161",
                    "name": "Example medicine",
                    "score": "100",
                }
            ]
        }
    }
    mock_get.return_value = mock_response

    result = search_medicine("Example medicine")

    assert result["status"] == "success"
    assert result["results"][0]["rxcui"] == "161"


def test_empty_search_does_not_call_api():
    result = search_medicine("")

    assert result["status"] == "empty_input"
    assert result["results"] == []



@patch("app.core.rxnorm_client.requests.get")
def test_get_medicine_details(mock_get):
    from app.core.rxnorm_client import get_medicine_details

    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "properties": {
            "rxcui": "20610",
            "name": "cetirizine",
            "tty": "IN",
        }
    }
    mock_get.return_value = mock_response

    result = get_medicine_details("20610")

    assert result["status"] == "success"
    assert result["name"] == "cetirizine"
    assert result["term_type"] == "IN"


def test_get_medicine_details_rejects_invalid_id():
    from app.core.rxnorm_client import get_medicine_details

    result = get_medicine_details("abc")

    assert result["status"] == "invalid_rxcui"
