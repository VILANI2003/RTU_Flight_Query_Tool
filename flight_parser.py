"""Flight Schedule Parser and Query Tool - command-line entry point.

Run from the project folder, for example:
    python flight_parser.py -i data/db.csv -a data/airports.txt
"""
import sys
import os
import json
import argparse
import logging


from datetime import datetime

from validator import load_airports
from csv_loader import parse_files
from query import run_queries

STUDENT_ID = "241ADB128"
FIRST_NAME = "Vilani"
LAST_NAME = "Karunasinghege"


def main(argv: list[str] | None = None) -> int:
    """Run the whole program and return the exit code (0, 1 or 2)."""
    parser = argparse.ArgumentParser(
        description="Flight Schedule Parser and Query Tool"
    )

    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("-i", metavar="FILE", help="Parse one CSV file")
    source.add_argument("-d", metavar="FOLDER", help="Parse CSV files from a folder")
    source.add_argument("-j", metavar="FILE", help="parse CSV files from a folder")

    parser.add_argument("-a", metavar="FILE", help="Airport list file")
    parser.add_argument("-o", metavar="FILE", help="Output database Json file")
    parser.add_argument("-q", metavar="FILE", help="Query JSON file")
    parser.add_argument("-r", metavar="FOLDER", default=".", help="Response folder")

    args = parser.parse_args(argv)

    if (args.i or args.d) and not args.a:
        parser.error("-a is required with -i or d")

    if args.j and args.o:
        parser.error("-o cannot be with -j")

    logger = logging.getLogger("flight_parser")
    logger.setLevel(logging.INFO)
    logger.propagate =False

    handler = None

    try:
        if args.j:
            with open(args.j, "r", encoding="utf-8") as file:
                db = json.load(file)

            if not isinstance(db, list) or not all(
                isinstance(flight, dict) for flight in db
            ):
                raise ValueError("Database must be a JSON array of objects")

        else:
            if args.i:
                paths = [args.i]
            else:
                paths = sorted(
                    os.path.join(args.d,name) 
                    for name in os.listdir(args.d)
                    if name.endswith(".csv")
                    and os.path.isfile(os.path.join(args.d, name))
                )

                if not paths:
                    raise ValueError("No CSV files found in the folder")
            airports = load_airports(args.a)

            output_path = args.o if args.o else "db.json"
            log_path = os.path.join(
                os.path.dirname(os.path.abspath(output_path)),
                "errors.log"
            )

            handler = logging.FileHandler(
                log_path, mode="w", encoding="utf-8"

            )
            handler.setFormatter(logging.Formatter(
                "%(asctime)s %(levelname)s %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            ))
            logger.addHandler(handler)

            db, errors = parse_files(paths, airports)

            for error in errors:
                logger.warning(error)

            with open(output_path, "w", encoding="utf-8") as file:
                json.dump(db,file,indent=2)

        if args.q:
            with open(args.q, "r", encoding="utf-8") as file:
                queries = json.load(file)

            if isinstance(queries,dict):
                pass
            elif isinstance(queries, list):
                if not all(isinstance(query, dict)for query in queries):
                    raise ValueError("Queries must be objects")

            else:
                raise ValueError(
                    "Query file must contain an object or an array"
                )

            results = run_queries(db, queries)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            response_name = (
                f"response_{STUDENT_ID}_{FIRST_NAME}_{LAST_NAME}_"
                f"{timestamp}.json"
            )

            response_path = os.path.join(args.r, response_name)

            with open(response_path, "w", encoding="utf-8") as file:
                json.dump(results, file, indent=2)

        return 0
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    finally:
        if handler is not None:
            logger.removeHandler(handler)
            handler.close()

if __name__=="__main__":
    sys.exit(main())
    