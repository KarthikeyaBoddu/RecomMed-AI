
import requests

RXNORM_BASE_URL = "https://rxnav.nlm.nih.gov/REST"

def search_medicine(name: str) -> dict:
    """Search RxNorm and return unique, named medicine concepts."""

    name = name.strip()

    if not name:
        return {
            "query": name,
            "results": [],
            "status": "empty_input",
        }

    try:
        response = requests.get(
            f"{RXNORM_BASE_URL}/approximateTerm.json",
            params={"term": name, "maxEntries": 10},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        candidates = (
            data.get("approximateGroup", {})
            .get("candidate", [])
        )

        # Deduplicate by RxNorm concept ID.
        unique = {}

        for candidate in candidates:
            rxcui = candidate.get("rxcui")
            if not rxcui:
                continue

            if rxcui not in unique:
                unique[rxcui] = {
                    "rxcui": rxcui,
                    "name": candidate.get("name"),
                    "score": candidate.get("score"),
                }
            elif not unique[rxcui].get("name") and candidate.get("name"):
                unique[rxcui]["name"] = candidate["name"]

        # Resolve missing names using the RxNorm concept endpoint.
        for rxcui, candidate in unique.items():
            if not candidate["name"]:
                try:
                    detail_response = requests.get(
                        f"{RXNORM_BASE_URL}/rxcui/{rxcui}/properties.json",
                        timeout=10,
                    )
                    detail_response.raise_for_status()

                    properties = (
                        detail_response.json()
                        .get("properties", {})
                    )
                    candidate["name"] = properties.get("name")
                except requests.RequestException:
                    pass

        results = [
            candidate
            for candidate in unique.values()
            if candidate["name"]
        ]

        return {
            "query": name,
            "results": results,
            "status": "success" if results else "no_match",
        }

    except (requests.RequestException, ValueError):
        return {
            "query": name,
            "results": [],
            "status": "service_unavailable",
        }


def get_ingredients(rxcui: str) -> dict:
    """Retrieve ingredient concepts associated with an RxNorm concept."""

    if not rxcui.strip().isdigit():
        return {
            "rxcui": rxcui,
            "ingredients": [],
            "status": "invalid_rxcui",
        }

    try:
        response = requests.get(
            f"{RXNORM_BASE_URL}/rxcui/{rxcui}/related.json",
            params={"tty": "IN"},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        groups = data.get("relatedGroup", {}).get("conceptGroup", [])
        ingredients = []
        seen = set()

        for group in groups:
            for concept in group.get("conceptProperties", []):
                ingredient_id = concept.get("rxcui")
                ingredient_name = concept.get("name")

                if ingredient_id and ingredient_id not in seen:
                    seen.add(ingredient_id)
                    ingredients.append({
                        "rxcui": ingredient_id,
                        "name": ingredient_name,
                    })

        return {
            "rxcui": rxcui,
            "ingredients": ingredients,
            "status": "success" if ingredients else "no_ingredients_found",
        }

    except (requests.RequestException, ValueError):
        return {
            "rxcui": rxcui,
            "ingredients": [],
            "status": "service_unavailable",
        }


def get_medicine_details(rxcui: str) -> dict:
    """Retrieve basic identity information for an RxNorm concept."""

    if not rxcui.isdigit():
        return {
            "rxcui": rxcui,
            "status": "invalid_rxcui",
        }

    try:
        response = requests.get(
            f"{RXNORM_BASE_URL}/rxcui/{rxcui}/properties.json",
            timeout=10,
        )
        response.raise_for_status()

        properties = response.json().get("properties")

        if not properties:
            return {
                "rxcui": rxcui,
                "status": "no_concept_found",
            }

        return {
            "rxcui": properties.get("rxcui"),
            "name": properties.get("name"),
            "term_type": properties.get("tty"),
            "status": "success",
        }

    except (requests.RequestException, ValueError):
        return {
            "rxcui": rxcui,
            "status": "service_unavailable",
        }

