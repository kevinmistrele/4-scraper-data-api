from __future__ import annotations

from pathlib import Path

from collector.fetch import FetchError, fetch_indicator
from collector.transform import normalize_indicator_records
from storage import DATABASE_PATH, upsert_indicators

DEFAULT_INDICATORS = [
    "NY.GDP.MKTP.CD",
    "SP.POP.TOTL",
    "FP.CPI.TOTL.ZG",
]


def run_collection(
    *,
    country: str = "BR",
    indicators: list[str] | None = None,
    database_path: Path = DATABASE_PATH,
) -> dict[str, int | str]:
    selected_indicators = indicators or DEFAULT_INDICATORS
    result: dict[str, int | str] = {}

    for indicator in selected_indicators:
        try:
            records = fetch_indicator(indicator=indicator, country=country)
            frame = normalize_indicator_records(records, indicator)
            result[indicator] = upsert_indicators(frame, database_path)
        except FetchError as exc:
            result[indicator] = str(exc)

    return result
