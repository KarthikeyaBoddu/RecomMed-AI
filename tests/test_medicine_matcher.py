
from app.core.medicine_matcher import normalize_medicine_name


def test_exact_match():
    result = normalize_medicine_name("cetirizine")
    assert result["matched"] == "CETIRIZINE"
    assert result["status"] == "exact_match"


def test_alias_match():
    result = normalize_medicine_name("ascorbic acid")
    assert result["matched"] == "VITAMIN C"


def test_empty_input():
    result = normalize_medicine_name("   ")
    assert result["status"] == "empty_input"


def test_unknown_name_needs_clarification():
    result = normalize_medicine_name("unknown medicine xyz")
    assert result["status"] == "needs_clarification"
