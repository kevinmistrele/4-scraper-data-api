from __future__ import annotations

from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, Query
from pydantic import BaseModel

from collector.pipeline import run_collection
from storage import DATABASE_PATH, get_connection, initialize_database

app = FastAPI(title="Brazil Indicators API", version="1.0.0")


class IndicatorRecord(BaseModel):
    country_code: str
    country_name: str
    indicator_code: str
    indicator_name: str
    year: int
    value: float
    source: str
    collected_at: str


class IndicatorSummary(BaseModel):
    indicator_code: str
    indicator_name: str
    first_year: int
    last_year: int
    min_value: float
    max_value: float
    average_value: float
    observations: int


class CollectionResult(BaseModel):
    inserted_or_updated: dict[str, int]


@app.on_event("startup")
def startup() -> None:
    initialize_database()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/collect", response_model=CollectionResult)
def collect_now() -> CollectionResult:
    return CollectionResult(inserted_or_updated=run_collection())


@app.get("/indicators", response_model=list[IndicatorRecord])
def list_indicators(
    indicator_code: Annotated[str | None, Query()] = None,
    country_code: Annotated[str | None, Query()] = None,
    start_year: Annotated[int | None, Query(ge=1900)] = None,
    end_year: Annotated[int | None, Query(ge=1900)] = None,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    database_path: Path = DATABASE_PATH,
) -> list[IndicatorRecord]:
    query = "SELECT * FROM indicators WHERE 1 = 1"
    params: list[str | int] = []

    if indicator_code:
        query += " AND indicator_code = ?"
        params.append(indicator_code)
    if country_code:
        query += " AND country_code = ?"
        params.append(country_code)
    if start_year:
        query += " AND year >= ?"
        params.append(start_year)
    if end_year:
        query += " AND year <= ?"
        params.append(end_year)

    query += " ORDER BY indicator_code, year DESC LIMIT ?"
    params.append(limit)

    with get_connection(database_path) as connection:
        rows = connection.execute(query, params).fetchall()

    return [IndicatorRecord(**dict(row)) for row in rows]


@app.get("/indicators/summary", response_model=list[IndicatorSummary])
def summarize_indicators(database_path: Path = DATABASE_PATH) -> list[IndicatorSummary]:
    with get_connection(database_path) as connection:
        rows = connection.execute("""
            SELECT
                indicator_code,
                indicator_name,
                MIN(year) AS first_year,
                MAX(year) AS last_year,
                MIN(value) AS min_value,
                MAX(value) AS max_value,
                AVG(value) AS average_value,
                COUNT(*) AS observations
            FROM indicators
            GROUP BY indicator_code, indicator_name
            ORDER BY indicator_code
            """).fetchall()

    return [IndicatorSummary(**dict(row)) for row in rows]
