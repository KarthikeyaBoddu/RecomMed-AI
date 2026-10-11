
import json
from pathlib import Path
from typing import Any


class DDInterMappingError(ValueError):
    """Raised when DDInter mapping data is invalid."""


def load_drug_mappings(
    json_path: str | Path,
) -> dict[str, dict[str, Any]]:
    """
    Load DDInter drug mappings keyed by IDs such as 'DDInter600'.

    The source JSON uses numeric IDs in its 'ddinter' field.
    """
    path = Path(json_path)

    if not path.is_file():
        raise DDInterMappingError(f"Mapping file not found: {path}")

    try:
        with path.open("r", encoding="utf-8") as file:
            payload = json.load(file)
    except (json.JSONDecodeError, OSError) as exc:
        raise DDInterMappingError(
            f"Could not read mapping file: {path}"
        ) from exc

    source_records = payload.get("records") if isinstance(payload, dict) else None

    if not isinstance(source_records, list):
        raise DDInterMappingError(
            "Expected a JSON object containing a 'records' list."
        )

    mappings: dict[str, dict[str, Any]] = {}

    for index, record in enumerate(source_records):
        if not isinstance(record, dict):
            raise DDInterMappingError(
                f"Invalid record at index {index}: expected an object."
            )

        ddinter_id = record.get("ddinter")

        # Reject booleans, strings, zero and negative IDs.
        if (
            isinstance(ddinter_id, bool)
            or not isinstance(ddinter_id, int)
            or ddinter_id <= 0
        ):
            raise DDInterMappingError(
                f"Invalid DDInter ID at index {index}: {ddinter_id!r}"
            )

        key = f"DDInter{ddinter_id}"

        mapping = {
            "ddinter_id": key,
            "drugbank": record.get("drugbank") or None,
            "chembl": record.get("chembl") or None,
            "pubchem": record.get("pubchem") or None,
        }

        if key in mappings:
            if mappings[key] != mapping:
                raise DDInterMappingError(
                    f"Conflicting mappings for {key}."
                )
            continue

        mappings[key] = mapping

    return mappings
