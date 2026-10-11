
from pathlib import Path

import pytest

from app.core.interaction_checker import InteractionChecker


DB_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "raw"
    / "ddinter"
    / "ddi_index.sqlite"
)


@pytest.fixture
def checker():
    if not DB_PATH.is_file():
        pytest.skip("Local interaction database is not available")
    return InteractionChecker(DB_PATH)


def test_known_pair_returns_record(checker):
    result = checker.check(["abacavir", "naltrexone"])

    assert result["status"] == "records_found"
    assert len(result["results"]) == 1
    assert result["results"][0]["status"] == "record_found"
    assert result["results"][0]["level"] == "Moderate"


def test_pair_order_does_not_matter(checker):
    forward = checker.check(["abacavir", "naltrexone"])
    reverse = checker.check(["naltrexone", "abacavir"])

    assert forward["results"][0]["status"] == "record_found"
    assert reverse["results"][0]["status"] == "record_found"
    assert forward["results"][0]["level"] == reverse["results"][0]["level"]


def test_unknown_medicine_is_unresolved(checker):
    result = checker.check(["medicine-name-that-does-not-exist", "abacavir"])

    assert result["status"] == "incomplete"
    assert result["results"][0]["status"] == "unresolved"


def test_empty_input_is_rejected(checker):
    result = checker.check([])

    assert result["status"] == "invalid_input"


def test_duplicate_names_are_deduplicated(checker):
    result = checker.check(["abacavir", "ABACAVIR"])

    assert result["medicines"] == ["abacavir"]
    assert result["results"] == []
