
import sqlite3
from itertools import combinations
from pathlib import Path
from typing import Any


DEFAULT_DB_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "raw"
    / "ddinter"
    / "ddi_index.sqlite"
)


def normalize_name(name: str) -> str:
    """Normalize spacing and case without guessing drug identity."""
    return " ".join(name.strip().casefold().split())


class InteractionChecker:
    def __init__(self, db_path: str | Path = DEFAULT_DB_PATH):
        self.db_path = Path(db_path)

        if not self.db_path.is_file():
            raise FileNotFoundError(
                f"Interaction database not found: {self.db_path}"
            )

    def _connect(self) -> sqlite3.Connection:
        uri = self.db_path.resolve().as_uri() + "?mode=ro"
        connection = sqlite3.connect(uri, uri=True)
        connection.row_factory = sqlite3.Row
        return connection

    def check(self, medicines: list[str]) -> dict[str, Any]:
        """
        Check all unique medicine pairs.

        A missing record is not evidence that a combination is safe.
        """
        if not medicines:
            return {
                "status": "invalid_input",
                "message": "Provide at least one medicine.",
                "medicines": [],
                "results": [],
            }

        cleaned = [name.strip() for name in medicines if name.strip()]

        if not cleaned:
            return {
                "status": "invalid_input",
                "message": "Provide at least one non-empty medicine name.",
                "medicines": [],
                "results": [],
            }

        # Deduplicate case-insensitively while preserving user-facing names.
        unique: dict[str, str] = {}
        for name in cleaned:
            unique.setdefault(normalize_name(name), name)

        names = list(unique.values())
        results = []

        with self._connect() as connection:
            known_names = {
                normalize_name(row["name"]): row["name"]
                for row in connection.execute("SELECT name FROM drugs")
            }

            resolved = {
                name: known_names.get(normalize_name(name))
                for name in names
            }

            for medicine_a, medicine_b in combinations(names, 2):
                canonical_a = resolved[medicine_a]
                canonical_b = resolved[medicine_b]

                if canonical_a is None or canonical_b is None:
                    results.append({
                        "medicine_a": medicine_a,
                        "medicine_b": medicine_b,
                        "status": "unresolved",
                        "message": (
                            "At least one medicine did not exactly match "
                            "a name in the available database."
                        ),
                    })
                    continue

                row = connection.execute(
                    """
                    SELECT drug_a, drug_b, level
                    FROM interactions
                    WHERE (lower(trim(drug_a)) = lower(trim(?))
                           AND lower(trim(drug_b)) = lower(trim(?)))
                       OR (lower(trim(drug_a)) = lower(trim(?))
                           AND lower(trim(drug_b)) = lower(trim(?)))
                    LIMIT 1
                    """,
                    (
                        canonical_a, canonical_b,
                        canonical_b, canonical_a,
                    ),
                ).fetchone()

                if row is None:
                    results.append({
                        "medicine_a": medicine_a,
                        "medicine_b": medicine_b,
                        "status": "no_record_found",
                        "message": (
                            "No matching interaction record was found in "
                            "this database. This does not establish safety."
                        ),
                    })
                else:
                    results.append({
                        "medicine_a": medicine_a,
                        "medicine_b": medicine_b,
                        "status": "record_found",
                        "level": row["level"],
                        "source": "PharmExpert index; DDInter 2.0-derived",
                    })

        if any(item["status"] == "unresolved" for item in results):
            overall_status = "incomplete"
        elif any(item["status"] == "record_found" for item in results):
            overall_status = "records_found"
        else:
            overall_status = "no_records_found"

        return {
            "status": overall_status,
            "medicines": names,
            "database": "ddi_index.sqlite",
            "results": results,
            "disclaimer": (
                "This dataset is not a complete clinical assessment. "
                "A missing record does not mean a combination is safe. "
                "Consult a qualified healthcare professional."
            ),
        }
