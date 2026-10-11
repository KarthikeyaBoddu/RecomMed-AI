
import json

import pytest

from app.core.ddinter_mapping import (
    DDInterMappingError,
    load_drug_mappings,
)


def write_json(path, payload):
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_loads_explicit_ddinter_ids(tmp_path):
    path = tmp_path / "drug_data.json"
    write_json(path, {
        "records": [
            {
                "ddinter": 600,
                "drugbank": "DB00366",
                "chembl": "CHEMBL1004",
                "pubchem": "3162",
            }
        ]
    })

    mappings = load_drug_mappings(path)

    assert mappings["DDInter600"]["drugbank"] == "DB00366"
    assert mappings["DDInter600"]["chembl"] == "CHEMBL1004"
    assert mappings["DDInter600"]["pubchem"] == "3162"


def test_empty_external_ids_become_none(tmp_path):
    path = tmp_path / "drug_data.json"
    write_json(path, {
        "records": [{
            "ddinter": 2,
            "drugbank": "",
            "chembl": "",
            "pubchem": "",
        }]
    })

    mapping = load_drug_mappings(path)["DDInter2"]

    assert mapping["drugbank"] is None
    assert mapping["chembl"] is None
    assert mapping["pubchem"] is None


def test_rejects_duplicate_conflicting_ids(tmp_path):
    path = tmp_path / "drug_data.json"
    write_json(path, {
        "records": [
            {"ddinter": 1, "drugbank": "DB00001"},
            {"ddinter": 1, "drugbank": "DB00002"},
        ]
    })

    with pytest.raises(DDInterMappingError, match="Conflicting mappings"):
        load_drug_mappings(path)


def test_rejects_invalid_id(tmp_path):
    path = tmp_path / "drug_data.json"
    write_json(path, {
        "records": [{"ddinter": "600"}]
    })

    with pytest.raises(DDInterMappingError, match="Invalid DDInter ID"):
        load_drug_mappings(path)


def test_rejects_missing_file(tmp_path):
    with pytest.raises(DDInterMappingError, match="not found"):
        load_drug_mappings(tmp_path / "missing.json")
