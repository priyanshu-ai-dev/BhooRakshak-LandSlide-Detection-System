#!/usr/bin/env python3
"""
ingestion/import_nasa_glc.py — NASA Global Landslide Catalog (GLC/COOLR) importer.

PURPOSE
-------
Reads the NASA GLC CSV export, filters to the Northeast India (NER) bounding box,
validates each record, and upserts into the `landslide_events` table.

The import is IDEMPOTENT: re-running the script with the same CSV will not create
duplicate records (uses ON CONFLICT (id) DO NOTHING).

DATA SOURCE
-----------
    Name    : NASA Global Landslide Catalog (GLC/COOLR)
    URL     : https://catalog.data.gov/dataset/global-landslide-catalog-export
    License : U.S. Government public domain work. Attribution requested.
    Citation:
        Kirschbaum, D.B. et al. (2010) Natural Hazards 52(3):561-575
            doi:10.1007/s11069-009-9401-4
        Kirschbaum, D.B. et al. (2015) Geomorphology
            doi:10.1016/j.geomorph.2015.03.016

DOWNLOAD
--------
    1. Visit https://catalog.data.gov/dataset/global-landslide-catalog-export
    2. Download the CSV export (look for "Global_Landslide_Catalog_Export.csv"
       or similar — the filename may vary by export date).
    3. Save it to:  ingestion/data/Global_Landslide_Catalog_Export.csv
       (or supply a path with --csv-file)

USAGE
-----
    # From the project root:
    python ingestion/import_nasa_glc.py

    # With a custom CSV path and database URL:
    python ingestion/import_nasa_glc.py \\
        --csv-file /path/to/Global_Landslide_Catalog_Export.csv \\
        --database-url "postgresql://postgres:secret@localhost:5432/ner_landslide"

    # Dry run (validate only, no DB writes):
    python ingestion/import_nasa_glc.py --dry-run

NER BOUNDING BOX
----------------
    West  :  88.0 °E
    East  :  98.0 °E   (covers Arunachal Pradesh eastern tip)
    South :  21.0 °N
    North :  30.0 °N
    States: Assam, Meghalaya, Manipur, Mizoram, Nagaland,
            Arunachal Pradesh, Tripura, Sikkim
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# NER bounding box — inclusive
# ---------------------------------------------------------------------------
NER_BBOX = {
    "lon_min": 88.0,
    "lon_max": 98.0,
    "lat_min": 21.0,
    "lat_max": 30.0,
}

DEFAULT_CSV_PATH = Path(__file__).parent / "data" / "Global_Landslide_Catalog_Export.csv"
SOURCE_SLUG = "nasa-glc"

# Accepted landslide_size values (normalise raw CSV strings to these)
SIZE_MAP: dict[str, str] = {
    "catastrophic":  "catastrophic",
    "very large":    "very_large",
    "very_large":    "very_large",
    "large":         "large",
    "medium":        "medium",
    "small":         "small",
    "":              "unknown",
}


# ---------------------------------------------------------------------------
# Row dataclass
# ---------------------------------------------------------------------------
@dataclass
class LandslideRecord:
    id:                    int
    geom_wkt:              str          # WKT for ST_GeomFromText
    event_date:            Optional[date]
    event_date_raw:        str
    event_title:           str
    location_description:  str
    country_name:          str
    country_code:          str
    admin_division_name:   str
    landslide_type:        str
    landslide_size:        str
    trigger:               str
    fatalities:            Optional[int]
    injuries:              Optional[int]
    source_link:           str


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

class ValidationError(Exception):
    pass


def parse_float(value: str, field_name: str) -> float:
    try:
        return float(value)
    except (ValueError, TypeError):
        raise ValidationError(f"Invalid float for {field_name!r}: {value!r}")


def parse_int_or_none(value: str) -> Optional[int]:
    stripped = value.strip()
    if not stripped:
        return None
    try:
        return int(float(stripped))
    except (ValueError, TypeError):
        return None


def parse_date_or_none(value: str) -> Optional[date]:
    """Try several common date formats from the GLC CSV."""
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%m/%d/%Y"):
        try:
            return date.fromisoformat(value.strip()[:10]) if fmt == "%Y-%m-%d" \
                else __import__("datetime").datetime.strptime(value.strip(), fmt).date()
        except (ValueError, AttributeError):
            continue
    return None


def normalise_size(raw: str) -> str:
    return SIZE_MAP.get(raw.strip().lower(), "unknown")


def is_within_ner(lon: float, lat: float) -> bool:
    return (
        NER_BBOX["lon_min"] <= lon <= NER_BBOX["lon_max"]
        and NER_BBOX["lat_min"] <= lat <= NER_BBOX["lat_max"]
    )


def validate_record(row: dict[str, str]) -> LandslideRecord:
    """Parse, validate, and return a LandslideRecord or raise ValidationError."""
    # --- event_id ---
    raw_id = row.get("id", "").strip()
    if not raw_id:
        raise ValidationError("Missing 'id'")
    try:
        event_id = int(float(raw_id))
    except (ValueError, TypeError):
        raise ValidationError(f"Non-numeric id: {raw_id!r}")

    # --- coordinates ---
    lat = parse_float(row.get("latitude", ""), "latitude")
    lon = parse_float(row.get("longitude", ""), "longitude")

    if not (-90 <= lat <= 90):
        raise ValidationError(f"Latitude out of range: {lat}")
    if not (-180 <= lon <= 180):
        raise ValidationError(f"Longitude out of range: {lon}")
    if not is_within_ner(lon, lat):
        # Not a validation error — just outside our bbox; caller handles silently
        raise _OutsideBboxError()

    geom_wkt = f"POINT({lon} {lat})"

    # --- dates ---
    raw_date = row.get("event_date", "").strip()
    parsed_date = parse_date_or_none(raw_date)

    # --- classifications ---
    landslide_type = (row.get("landslide_type") or "").strip().lower().replace(" ", "_")
    landslide_size = normalise_size(row.get("landslide_size") or "")
    trigger        = (row.get("trigger") or "").strip().lower().replace(" ", "_")

    return LandslideRecord(
        id                   = event_id,
        geom_wkt             = geom_wkt,
        event_date           = parsed_date,
        event_date_raw       = raw_date,
        event_title          = (row.get("event_title") or "").strip(),
        location_description = (row.get("location_description") or "").strip(),
        country_name         = (row.get("country_name") or "").strip(),
        country_code         = (row.get("country_code") or "").strip()[:2].upper(),
        admin_division_name  = (row.get("admin_division_name") or "").strip(),
        landslide_type       = landslide_type,
        landslide_size       = landslide_size,
        trigger              = trigger,
        fatalities           = parse_int_or_none(row.get("fatalities") or ""),
        injuries             = parse_int_or_none(row.get("injuries") or ""),
        source_link          = (row.get("source_link") or "").strip(),
    )


class _OutsideBboxError(Exception):
    """Sentinel: record is outside NER bounding box (not a data error)."""


# ---------------------------------------------------------------------------
# Database upsert
# ---------------------------------------------------------------------------

INSERT_SQL = """
INSERT INTO landslide_events (
    id, geom, source_dataset_slug,
    event_date, event_date_raw, event_title, location_description,
    country_name, country_code, admin_division_name,
    landslide_type, landslide_size, trigger,
    fatalities, injuries, source_link
) VALUES (
    %(id)s,
    ST_GeomFromText(%(geom_wkt)s, 4326),
    %(source_slug)s,
    %(event_date)s, %(event_date_raw)s, %(event_title)s, %(location_description)s,
    %(country_name)s, %(country_code)s, %(admin_division_name)s,
    %(landslide_type)s, %(landslide_size)s, %(trigger)s,
    %(fatalities)s, %(injuries)s, %(source_link)s
)
ON CONFLICT (id) DO NOTHING;
"""


@dataclass
class ImportStats:
    total_rows:       int = 0
    outside_bbox:     int = 0
    validation_errors: list[str] = field(default_factory=list)
    inserted:         int = 0
    skipped_existing: int = 0


def run_import(
    csv_path: Path,
    database_url: str,
    dry_run: bool = False,
) -> ImportStats:
    import psycopg2  # type: ignore[import]

    stats = ImportStats()
    records: list[LandslideRecord] = []

    # ── 1. Parse and validate CSV ─────────────────────────────────────────
    print(f"[import] Reading {csv_path} …")
    with csv_path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):  # row 1 = header
            stats.total_rows += 1
            try:
                record = validate_record(row)
                records.append(record)
            except _OutsideBboxError:
                stats.outside_bbox += 1
            except ValidationError as exc:
                stats.validation_errors.append(f"Row {i}: {exc}")

    print(
        f"[import] Parsed {stats.total_rows} rows | "
        f"In NER bbox: {len(records)} | "
        f"Outside bbox: {stats.outside_bbox} | "
        f"Validation errors: {len(stats.validation_errors)}"
    )

    if stats.validation_errors:
        print("[import] VALIDATION ERRORS (rows discarded):")
        for err in stats.validation_errors:
            print(f"  ⚠  {err}")

    if dry_run:
        print("[import] DRY RUN — no database writes performed.")
        return stats

    if not records:
        print("[import] No records to insert. Done.")
        return stats

    # ── 2. Connect and upsert ─────────────────────────────────────────────
    print(f"[import] Connecting to database …")
    conn = psycopg2.connect(database_url)
    conn.autocommit = False
    cur = conn.cursor()

    try:
        for rec in records:
            params = {
                "id":                   rec.id,
                "geom_wkt":             rec.geom_wkt,
                "source_slug":          SOURCE_SLUG,
                "event_date":           rec.event_date,
                "event_date_raw":       rec.event_date_raw,
                "event_title":          rec.event_title,
                "location_description": rec.location_description,
                "country_name":         rec.country_name,
                "country_code":         rec.country_code,
                "admin_division_name":  rec.admin_division_name,
                "landslide_type":       rec.landslide_type,
                "landslide_size":       rec.landslide_size,
                "trigger":              rec.trigger,
                "fatalities":           rec.fatalities,
                "injuries":             rec.injuries,
                "source_link":          rec.source_link,
            }
            cur.execute(INSERT_SQL, params)
            if cur.rowcount == 1:
                stats.inserted += 1
            else:
                stats.skipped_existing += 1

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

    return stats


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Import NASA Global Landslide Catalog (NER subset) into PostGIS."
    )
    parser.add_argument(
        "--csv-file",
        type=Path,
        default=DEFAULT_CSV_PATH,
        help=f"Path to the NASA GLC CSV export (default: {DEFAULT_CSV_PATH})",
    )
    parser.add_argument(
        "--database-url",
        default=os.getenv("DATABASE_URL", "postgresql://postgres:ner_dev_secret@localhost:5432/ner_landslide"),
        help="PostgreSQL connection URL (default: reads DATABASE_URL env var)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and validate the CSV without writing to the database.",
    )

    args = parser.parse_args()

    if not args.csv_file.exists():
        print(f"[import] ERROR: CSV file not found: {args.csv_file}")
        print()
        print("  Please download the NASA GLC CSV from:")
        print("  https://catalog.data.gov/dataset/global-landslide-catalog-export")
        print(f"  and save it to: {DEFAULT_CSV_PATH}")
        print()
        print("  Or supply a custom path with --csv-file /path/to/file.csv")
        sys.exit(1)

    print("=" * 60)
    print("  NASA Global Landslide Catalog — NER India Import")
    print("  HISTORICAL EVENT INVENTORY — NOT a live warning system")
    print("=" * 60)
    print(f"  CSV   : {args.csv_file}")
    print(f"  DB    : {args.database_url.split('@')[-1]}")  # hide credentials
    print(f"  NER   : lon [{NER_BBOX['lon_min']}–{NER_BBOX['lon_max']}]  "
          f"lat [{NER_BBOX['lat_min']}–{NER_BBOX['lat_max']}]")
    print(f"  Mode  : {'DRY RUN' if args.dry_run else 'LIVE'}")
    print("=" * 60)

    stats = run_import(args.csv_file, args.database_url, dry_run=args.dry_run)

    print()
    print("── Import Summary ─────────────────────────────────────")
    print(f"  Total CSV rows read   : {stats.total_rows}")
    print(f"  Outside NER bbox      : {stats.outside_bbox}")
    print(f"  Validation errors     : {len(stats.validation_errors)}")
    print(f"  Inserted              : {stats.inserted}")
    print(f"  Skipped (existing)    : {stats.skipped_existing}")
    print("───────────────────────────────────────────────────────")
    print()
    print("Citation:")
    print("  Kirschbaum et al. (2010) doi:10.1007/s11069-009-9401-4")
    print("  Kirschbaum et al. (2015) doi:10.1016/j.geomorph.2015.03.016")
    print()


if __name__ == "__main__":
    main()
