"""
Tests for the SQLite-to-PostgreSQL migration script.

These tests validate argument parsing and the helper functions without
requiring real database connections.
"""
from unittest.mock import MagicMock, patch

import pytest

from scripts.migrate_from_sqlite import build_parser, main, parse_sqlite_datetime


# Override the autouse setup_db fixture from conftest.py so these sync tests
# don't attempt to connect to the async test database.
@pytest.fixture(autouse=True)
def setup_db():
    yield


# ── parse_sqlite_datetime tests ──


class TestParseSqliteDatetime:
    def test_datetime_with_microseconds(self):
        result = parse_sqlite_datetime("2024-03-15 14:30:45.123456")
        assert result == "2024-03-15T14:30:45.123456+03:00"

    def test_datetime_without_microseconds(self):
        result = parse_sqlite_datetime("2024-03-15 14:30:45")
        assert result == "2024-03-15T14:30:45+03:00"

    def test_date_only(self):
        result = parse_sqlite_datetime("2024-03-15")
        assert result == "2024-03-15T00:00:00+03:00"

    def test_none_returns_none(self):
        assert parse_sqlite_datetime(None) is None

    def test_unparseable_returned_as_is(self):
        assert parse_sqlite_datetime("not-a-date") == "not-a-date"


# ── Argument parser tests ──


class TestBuildParser:
    def test_both_args_required(self):
        parser = build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args([])

    def test_missing_pg_arg(self):
        parser = build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["--sqlite", "test.db"])

    def test_missing_sqlite_arg(self):
        parser = build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["--pg", "postgresql://localhost/db"])

    def test_valid_args(self):
        parser = build_parser()
        args = parser.parse_args(["--sqlite", "/tmp/test.db", "--pg", "postgresql://u:p@localhost/db"])
        assert args.sqlite == "/tmp/test.db"
        assert args.pg == "postgresql://u:p@localhost/db"


# ── Main function tests ──


class TestMain:
    @patch("scripts.migrate_from_sqlite.migrate")
    def test_main_calls_migrate_with_parsed_args(self, mock_migrate: MagicMock):
        main(["--sqlite", "/data/old.db", "--pg", "postgresql://localhost/medtracker"])
        mock_migrate.assert_called_once_with("/data/old.db", "postgresql://localhost/medtracker")

    @patch("scripts.migrate_from_sqlite.migrate", side_effect=RuntimeError("No users found"))
    def test_main_propagates_errors(self, mock_migrate: MagicMock):
        with pytest.raises(RuntimeError, match="No users found"):
            main(["--sqlite", "x.db", "--pg", "postgresql://localhost/db"])
