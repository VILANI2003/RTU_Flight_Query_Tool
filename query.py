"""Running queries against the flight database."""

import math

VALID_FIELDS = {
    "flight_id",
    "origin",
    "destination",
    "departure_datetime",
    "arrival_datetime",
    "price"   
}

STRING_FILTERS = {
    "flight_id",
    "origin",
    "destination",
}

def run_query(db: list[dict], query: dict) -> dict:
    """Return one response entry for one query object."""

    if not isinstance(query, dict):
        return {
            "query": query,
            "error": "INVALID_QUERY",
            "matches": []
        }

    allowed_keys = STRING_FILTERS | {
        "departure_datetime",
        "arrival_datetime",
        "price",
        "min_price",
        "sort_by",
        "order",
        "limit"
    }

    if not set(query.keys()).issubset(allowed_keys):
        return {
            "query": query,
            "error": "INVALID_QUERY",
            "matches": []
        }
    

    for key in ("departure_datetime", "arrival_datetime"):
        if key in query and not isinstance(query[key], str):
            return {
                "query": query,
                "error": "INVALID_QUERY",
                "matches": []
            } 

   
    #Check string filters
    for key in STRING_FILTERS:
        if key in query and not isinstance(query[key], str):
            return {
                "query": query,
                "error": "INVALID_QUERY",
                "matches": []
            }

    #Check price filters
    for key in ("price", "min_price"):
        if key in query:
            value = query[key]

            if (
                isinstance(value, bool)
                or not isinstance(value, (int,float))
                or not math.isfinite(value)
            ):

                return {
                    "query": query,
                    "error": "INVALID_QUERY",
                    "matches": []
                }

    # Check sorting
    if "sort_by" in  query:
        if (
            not isinstance(query["sort_by"], str)
            or query["sort_by"] not in VALID_FIELDS
        ):
            return {
                "query": query,
                "error": "INVALID_QUERY",
                "matches": []
            }
        
    if "order" in query:
        if(
            "sort_by" not in query
            or query["order"] not in ("asc", "desc")
        ):

            return {
                "query": query,
                "error": "INVALID_QUERY",
                "matches": []
            }

    #Check limits.
    if "limit" in query:
        limit = query["limit"]

        if (
            isinstance(limit, bool)
            or not isinstance(limit, int)
            or limit < 0
        ):
            return{
                "query": query,
                "error": "INVALID_QUERY",
                "matches": []
            }
    # filter the matching flights.
    matches = []

    for flight in db:
        if any(
            flight[key] != query[key]
            for key in STRING_FILTERS
            if key in query
        ):
            continue

        if (
            "departure_datetime" in query
            and flight["departure_datetime"] < query["departure_datetime"]
        ):
            continue

        if (
            "arrival_datetime" in query
            and flight["arrival_datetime"] > query["arrival_datetime"]
        ):
            continue

        if "price" in query and flight["price"] > query["price"]:
            continue

        if "min_price" in query and flight["price"] < query["min_price"]:
            continue

        matches.append(flight)

    # Sort matching flights
    if "sort_by" in query:
        sort_key = query["sort_by"]
        reverse = query.get("order", "asc") == "desc"

        matches.sort(
            key=lambda flight: flight[sort_key],
            reverse=reverse
        )
        
    #Apply limit
    if "limit" in query:
        matches = matches[:query["limit"]]

    return {
        "query": query,
        "matches": matches
    }

def run_queries(db: list[dict], queries: dict | list) -> list[dict]:
    """Accept one query object or a list of them; always return a list."""

    if isinstance(queries, dict):
        queries = [queries]

    if not isinstance(queries, list):
        return [{
            "query": queries,
            "error": "INVALID_QUERY",
            "matches": []
        }]
    return [run_query(db, query) for query in queries]