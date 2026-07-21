from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

DATABASE_PATH = Path("data/indicators.sqlite")


def get_connection(database_path: Path = DATABASE_PATH) -> sqlite3.Connection:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database(database_path: Path = DATABASE_PATH) -> None:
    with get_connection(database_path) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS indicators (
                country_code TEXT NOT NULL,
                country_name TEXT NOT NULL,
                indicator_code TEXT NOT NULL,
                indicator_name TEXT NOT NULL,
                year INTEGER NOT NULL,
                value REAL NOT NULL,
                source TEXT NOT NULL,
                collected_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (country_code, indicator_code, year)
            )
            """)
        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_indicators_filter
            ON indicators (indicator_code, country_code, year)
            """)


def upsert_indicators(frame: pd.DataFrame, database_path: Path = DATABASE_PATH) -> int:
    if frame.empty:
        return 0

    initialize_database(database_path)
    rows = frame[
        [
            "country_code",
            "country_name",
            "indicator_code",
            "indicator_name",
            "year",
            "value",
            "source",
        ]
    ].itertuples(index=False, name=None)

    with get_connection(database_path) as connection:
        connection.executemany(
            """
            INSERT INTO indicators (
                country_code,
                country_name,
                indicator_code,
                indicator_name,
                year,
                value,
                source
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(country_code, indicator_code, year) DO UPDATE SET
                country_name = excluded.country_name,
                indicator_name = excluded.indicator_name,
                value = excluded.value,
                source = excluded.source,
                collected_at = CURRENT_TIMESTAMP
            """,
            list(rows),
        )
        return connection.total_changes
