
from rapidfuzz import process, fuzz


# Illustrative sample data for development only.
# These aliases are not a substitute for verified medicine records.
MEDICINE_ALIASES = {
    "paracetamol": "PARACETAMOL",
    "acetaminophen": "PARACETAMOL",
    "cetirizine": "CETIRIZINE",
    "vitamin c": "VITAMIN C",
    "ascorbic acid": "VITAMIN C",
}

# The keys are the names users can search.
KNOWN_NAMES = list(MEDICINE_ALIASES.keys())


def normalize_medicine_name(name: str) -> dict:
    """Match a user-provided name against known aliases."""

    query = name.strip().lower()

    if not query:
        return {
            "input": name,
            "matched": None,
            "status": "empty_input",
        }

    # First, check for an exact alias match.
    if query in MEDICINE_ALIASES:
        return {
            "input": name,
            "matched": MEDICINE_ALIASES[query],
            "matched_alias": query,
            "status": "exact_match",
        }

    # Otherwise, look for a close spelling match.
    result = process.extractOne(
        query,
        KNOWN_NAMES,
        scorer=fuzz.ratio,
    )

    if result is None:
        return {
            "input": name,
            "matched": None,
            "status": "no_match",
        }

    alias, score, _ = result

    # Conservative threshold for this demonstration.
    if score >= 90:
        return {
            "input": name,
            "matched": MEDICINE_ALIASES[alias],
            "matched_alias": alias,
            "similarity": round(score, 2),
            "status": "fuzzy_match",
        }

    return {
        "input": name,
        "matched": None,
        "status": "needs_clarification",
    }
