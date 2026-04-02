"""
Standalone CLI script to migrate data from the legacy Django/SQLite database
to the new FastAPI/PostgreSQL database.

Usage:
    python scripts/migrate_from_sqlite.py \
        --sqlite ../db.sqlite3 \
        --pg postgresql://user:pass@localhost/medtracker
"""
import argparse
import sqlite3
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple

try:
    import psycopg2
except ModuleNotFoundError:  # psycopg2 removed in Python 3.14 migration; only needed if running the script
    psycopg2 = None  # type: ignore[assignment]

KYIV_TZ_OFFSET = "+03:00"

# Reference tables: (sqlite_table, pg_table)
REFERENCE_TABLES = [
    ("core_position", "position"),
    ("core_procedure", "procedure"),
    ("core_clinic", "clinic"),
    ("core_city", "city"),
]

ALL_PG_TABLES = ["city", "clinic", "procedure", "position", "visit", "treatment", "user"]


def parse_sqlite_datetime(value: Optional[str]) -> Optional[str]:
    """Parse SQLite datetime string and return ISO format with timezone for PostgreSQL."""
    if value is None:
        return None
    # SQLite stores as "YYYY-MM-DD HH:MM:SS.ffffff" or "YYYY-MM-DD HH:MM:SS"
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(value, fmt)
            return dt.isoformat() + KYIV_TZ_OFFSET
        except ValueError:
            continue
    # If nothing matched, return as-is and let PostgreSQL handle it
    return value


def migrate(sqlite_path: str, pg_dsn: str) -> None:
    """Run the full migration from SQLite to PostgreSQL."""
    # Open SQLite in read-only mode
    sqlite_uri = f"file:{sqlite_path}?mode=ro"
    sqlite_conn = sqlite3.connect(sqlite_uri, uri=True)
    sqlite_conn.row_factory = sqlite3.Row

    pg_conn = psycopg2.connect(pg_dsn)
    summary: Dict[str, int] = {}

    try:
        with pg_conn:
            cur = pg_conn.cursor()

            # ── Step 0: Clean up existing data (allows re-running) ──
            for table in ["treatment", "visit"] + [t[1] for t in REFERENCE_TABLES] + ["user"]:
                cur.execute(f'DELETE FROM "{table}"')
            print("Cleaned existing PostgreSQL data")

            # ── Step A: Migrate ALL users from SQLite auth_user ──
            user_rows = sqlite_conn.execute(
                "SELECT id, username, password, is_active, date_joined FROM auth_user ORDER BY id"
            ).fetchall()
            if not user_rows:
                raise RuntimeError("No users found in SQLite auth_user table")

            for u in user_rows:
                cur.execute(
                    """
                    INSERT INTO "user" (id, username, password_hash, is_active, created, updated)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        u["id"],
                        u["username"],
                        u["password"],  # Django PBKDF2 hash, preserved as-is
                        bool(u["is_active"]),
                        parse_sqlite_datetime(u["date_joined"]),
                        parse_sqlite_datetime(u["date_joined"]),
                    ),
                )
                print(f"Migrated user: {u['username']} (id={u['id']})")

            summary["user"] = len(user_rows)

            # ── Step C: Migrate reference tables ──
            for sqlite_table, pg_table in REFERENCE_TABLES:
                rows = sqlite_conn.execute(
                    f"SELECT id, name, created, updated FROM {sqlite_table} ORDER BY id"
                ).fetchall()

                for r in rows:
                    cur.execute(
                        f"""
                        INSERT INTO "{pg_table}" (id, name, created, updated)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (
                            r["id"],
                            r["name"],
                            parse_sqlite_datetime(r["created"]),
                            parse_sqlite_datetime(r["updated"]),
                        ),
                    )

                summary[pg_table] = len(rows)
                print(f"Migrated {len(rows)} rows into '{pg_table}'")

            # ── Step D: Migrate visits (preserve original user_id) ──
            visit_rows = sqlite_conn.execute(
                """
                SELECT id, user_id, date, position_id, doctor, procedure_id,
                       procedure_details, clinic_id, city_id, document,
                       link, comment, created, updated
                FROM core_visit ORDER BY id
                """
            ).fetchall()

            for v in visit_rows:
                cur.execute(
                    """
                    INSERT INTO visit (id, user_id, date, position_id, doctor,
                                       procedure_id, procedure_details, clinic_id,
                                       city_id, document, link, comment,
                                       created, updated)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        v["id"],
                        v["user_id"] or 1,  # assign orphaned visits to first user
                        parse_sqlite_datetime(v["date"]),
                        v["position_id"],
                        v["doctor"],
                        v["procedure_id"],
                        v["procedure_details"],
                        v["clinic_id"],
                        v["city_id"],
                        v["document"],
                        v["link"],
                        v["comment"],
                        parse_sqlite_datetime(v["created"]),
                        parse_sqlite_datetime(v["updated"]),
                    ),
                )

            summary["visit"] = len(visit_rows)
            print(f"Migrated {len(visit_rows)} rows into 'visit'")

            # ── Step E: Migrate treatments ──
            treatment_rows = sqlite_conn.execute(
                """
                SELECT id, user_id, date_start, name, days, receipt, created, updated
                FROM core_treatment ORDER BY id
                """
            ).fetchall()

            for t in treatment_rows:
                cur.execute(
                    """
                    INSERT INTO treatment (id, user_id, date_start, name, days,
                                           receipt, created, updated)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        t["id"],
                        t["user_id"],
                        parse_sqlite_datetime(t["date_start"]),
                        t["name"],
                        t["days"],
                        t["receipt"],
                        parse_sqlite_datetime(t["created"]),
                        parse_sqlite_datetime(t["updated"]),
                    ),
                )

            summary["treatment"] = len(treatment_rows)
            print(f"Migrated {len(treatment_rows)} rows into 'treatment'")

            # ── Step F: Reset PostgreSQL sequences ──
            for pg_table in ALL_PG_TABLES:
                seq_name = f"{pg_table}_id_seq"
                cur.execute(
                    f"""
                    SELECT setval('{seq_name}',
                                  COALESCE((SELECT MAX(id) FROM "{pg_table}"), 0) + 1,
                                  false)
                    """
                )
            print("Reset all sequences")

        # Transaction committed automatically by the `with pg_conn:` block
        print("\n=== Migration Summary ===")
        for table, count in summary.items():
            print(f"  {table}: {count} rows")
        print("Migration completed successfully.")

    except Exception:
        pg_conn.rollback()
        print("Migration FAILED — transaction rolled back.", file=sys.stderr)
        raise
    finally:
        sqlite_conn.close()
        pg_conn.close()


def build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser."""
    parser = argparse.ArgumentParser(
        description="Migrate medical records from SQLite (Django) to PostgreSQL (FastAPI)"
    )
    parser.add_argument(
        "--sqlite",
        required=True,
        help="Path to the SQLite database file",
    )
    parser.add_argument(
        "--pg",
        required=True,
        help="PostgreSQL connection string (e.g., postgresql://user:pass@localhost/medtracker)",
    )
    return parser


def main(args: Optional[List[str]] = None) -> None:
    """Entry point: parse arguments and run migration."""
    parser = build_parser()
    parsed = parser.parse_args(args)
    migrate(parsed.sqlite, parsed.pg)


if __name__ == "__main__":
    main()
