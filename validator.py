"""Row validation: airport list loading, single-row checks, record building."""

import re
import math
from datetime import datetime


def load_airports(path: str) -> set[str]:
    """Read an airport codes from a file"""

    airports = set()

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            code = line.strip()

            if code and not code.startswith("#"):
                airports.add(code)

    return airports


def validate_row(fields: list[str], airports: set[str]) -> str | None:
    """Validate one flight row and return the first error code."""

    if len(fields) != 6:
        return "WRONG_FIELD_COUNT"

    fields = [field.strip() for field in fields]

    flight_id, origin, destination, departure, arrival, price = fields

    #Check 2: Missing fields.
    if any(field == "" for field in fields):
        return "MISSING_FIELD"

    #Check 3: Flight ID must contain ASCII letters or digits
    if not re.fullmatch(r"[A-Za-z0-9]{2,8}", flight_id):
        return "INVALID_FLIGHT_ID"

    #Chrck4: Valid Passport
    if not re.fullmatch(r"[A-Z]{3}", origin) or origin not in airports:
        return "INVALID_ORIGIN"

    #Check 5: Valid Destination
    if not re.fullmatch(r"[A-Z]{3}", destination) or destination not in airports:
        return "INVALID_DESTINATION"

    #Check 6: Origin and Destination can't be the same.
    if origin == destination:
        return "SAME_ORIGIN_DESTINATION"

    #check 7: Valide departure date and time
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}", departure):
        return "INVALID_DEPARTURE"

    try:
        departure_time = datetime.strptime(departure, "%Y-%m-%d %H:%M")
    except ValueError:
        return "INVALID_DEPARTURE"

    #Check 8: Valid arrival date and time
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}", arrival):
        return "INVALID_ARRIVAL"

    try:
        arrival_time = datetime.strptime(arrival, "%Y-%m-%d %H:%M")
    except ValueError:
        return "INVALID_ARRIVAL"

    #Check 9: Arrival should be after the departure
    if arrival_time <= departure_time:
        return "ARRIVAL_NOT_AFTER_DEPARTURE"

    try:
        flight_price = float(price)
    except ValueError:
        return "INVALID_PRICE"

    if not math.isfinite(flight_price):
        return "INVALID_PRICE"

    #Check 11: Priceshould be positive
    if flight_price <= 0:
        return "NON_POSITIVE_PRICE"

    #All checks passed
    return None

def to_record(fields: list[str]) -> dict:
    """Turn a valid row into a flight record dictionary."""

    fields = [field.strip() for field in fields]

    return {
        "flight_id": fields[0],
        "origin": fields[1],
        "destination": fields[2],
        "departure_datetime": fields[3],
        "arrival_datetime": fields[4],
        "price": float(fields[5])
    }