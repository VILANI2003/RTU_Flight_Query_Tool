"""Reading CSV files into flight records and error messages."""
import csv
import os

from validator import validate_row, to_record

def parse_files(paths: list[str], airports: set[str]) -> tuple[list[dict], list[str]]:
    """Process the CSV files in the order given."""

    records = []
    errors = []
    seen_flights = set()

    for path in paths:
        filename = os.path.basename(path)

        with open(path, "r", encoding="utf-8", newline="") as file:
            reader = csv.reader(file)

            #skips the header
            next(reader, None)

            for fields in reader:
                line_number = reader.line_num

                #skip empty lines
                if not fields or all(field.strip() == "" for field in fields):
                            continue
            
                #skip comments
                if fields[0].strip().startswith('#'):
                   continue
            
                #Validates the flight row.
                error_code = validate_row(fields, airports)
            
                if error_code is not None:
                    errors.append(
                        f"{filename}:{line_number}: {error_code} | Invalid flight row"
                    )
            
                    continue
                # create a record about a flight.
                record = to_record(fields)
            
                #check for duplicate flights
                duplicate_key = (
                    record["flight_id"],
                    record["departure_datetime"]
                )
                        
                if duplicate_key in seen_flights:
                    errors.append(
                        f"{filename}:{line_number}: DUPLICATE_FLIGHT | Duplicate flight"
                    )
            
                    continue
            
                seen_flights.add(duplicate_key)
                records.append(record)
                
    return records,errors
                

            

