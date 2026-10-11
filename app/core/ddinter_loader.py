
import csv
from pathlib import Path
from typing import Any

REQUIRED_COLUMNS = {
    "DDInterID_A",
    "Drug_A",
    "DDInterID_B",
    "Drug_B",
    "Level",
}

SOURCE_NAME = "DDInter"
SOURCE_LICENSE = "CC BY-NC-SA 4.0"
SOURCE_URL = "https://ddinter.scbdd.com/"


class DDInterDataError(ValueError):
    """Raised when DDInter input data is missing or malformed."""


def load_interactions(csv_paths: list[str | Path]) -> list[dict[str, Any]]:
    """
    Load DDInter CSV files into normalized interaction records.

    This function only loads the files provided by the caller.
    It does not download data or assume the dataset is complete.
    """
    if not csv_paths:
        raise DDInterDataError("No DDInter CSV files were provided.")

    records: dict[str, dict[str, Any]] = {}

    for csv_path in csv_paths:
        path = Path(csv_path)

        if not path.is_file():
            raise DDInterDataError(f"DDInter file not found: {path}")

        with path.open("r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)

            if reader.fieldnames is None:
                raise DDInterDataError(f"CSV has no header: {path}")

            missing = REQUIRED_COLUMNS - set(reader.fieldnames)
            if missing:
                raise DDInterDataError(
                    f"{path.name} is missing required columns: "
                    f"{', '.join(sorted(missing))}"
                )

            for line_number, row in enumerate(reader, start=2):
                drug_a_id = (row["DDInterID_A"] or "").strip()
                drug_a_name = (row["Drug_A"] or "").strip()
                drug_b_id = (row["DDInterID_B"] or "").strip()
                drug_b_name = (row["Drug_B"] or "").strip()
                level = (row["Level"] or "").strip()

                if not all(
                    [drug_a_id, drug_a_name, drug_b_id, drug_b_name, level]
                ):
                    raise DDInterDataError(
                        f"Empty required value in {path.name}, "
                        f"line {line_number}"
                    )

                record_id = f"{drug_a_id}_{drug_b_id}_{level}"

                record = {
                    "record_id": record_id,
                    "drug_a": {
                        "ddinter_id": drug_a_id,
                        "name": drug_a_name,
                    },
                    "drug_b": {
                        "ddinter_id": drug_b_id,
                        "name": drug_b_name,
                    },
                    "level": level,
                    "source": {
                        "name": SOURCE_NAME,
                        "url": SOURCE_URL,
                        "license": SOURCE_LICENSE,
                    },
                }

                existing = records.get(record_id)

                if existing is not None and existing != record:
                    raise DDInterDataError(
                        f"Conflicting duplicate record: {record_id}"
                    )

                records[record_id] = record

    return list(records.values())
