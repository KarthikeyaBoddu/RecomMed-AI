
import csv

import pytest

from app.core.ddinter_loader import (
    DDInterDataError,
    load_interactions,
)


def create_csv(path, rows, columns=None):
    columns = columns or [
        "DDInterID_A",
        "Drug_A",
        "DDInterID_B",
        "Drug_B",
        "Level",
    ]

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def test_loads_interaction_record(tmp_path):
    path = tmp_path / "sample.csv"
    create_csv(
        path,
        [{
            "DDInterID_A": "DDInter600",
            "Drug_A": "Doxylamine",
            "DDInterID_B": "DDInter1497",
            "Drug_B": "Potassium chloride",
            "Level": "Major",
        }],
    )

    records = load_interactions([path])

    assert len(records) == 1
    assert records[0]["drug_a"]["name"] == "Doxylamine"
    assert records[0]["drug_b"]["name"] == "Potassium chloride"
    assert records[0]["level"] == "Major"
    assert records[0]["source"]["license"] == "CC BY-NC-SA 4.0"


def test_rejects_missing_file(tmp_path):
    with pytest.raises(DDInterDataError, match="not found"):
        load_interactions([tmp_path / "missing.csv"])


def test_rejects_missing_columns(tmp_path):
    path = tmp_path / "bad.csv"
    create_csv(
        path,
        [],
        columns=["Drug_A", "Drug_B"],
    )

    with pytest.raises(DDInterDataError, match="missing required columns"):
        load_interactions([path])


def test_deduplicates_identical_records(tmp_path):
    path = tmp_path / "duplicates.csv"
    row = {
        "DDInterID_A": "DDInter600",
        "Drug_A": "Doxylamine",
        "DDInterID_B": "DDInter1497",
        "Drug_B": "Potassium chloride",
        "Level": "Major",
    }
    create_csv(path, [row, row])

    records = load_interactions([path])

    assert len(records) == 1


def test_rejects_empty_input_list():
    with pytest.raises(DDInterDataError, match="No DDInter CSV"):
        load_interactions([])
