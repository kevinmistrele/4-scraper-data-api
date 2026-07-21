from __future__ import annotations

from typing import Any

import pandas as pd


def normalize_indicator_records(records: list[dict[str, Any]], indicator_code: str) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []

    for record in records:
        country = record.get("country") or {}
        indicator = record.get("indicator") or {}
        value = record.get("value")

        rows.append(
            {
                "country_code": _string_or_empty(country.get("id")),
                "country_name": _string_or_empty(country.get("value")),
                "indicator_code": _string_or_empty(indicator.get("id") or indicator_code),
                "indicator_name": _string_or_empty(indicator.get("value")),
                "year": record.get("date"),
                "value": value,
                "source": "World Bank API",
            }
        )

    frame = pd.DataFrame(rows)
    if frame.empty:
        return pd.DataFrame(
            columns=[
                "country_code",
                "country_name",
                "indicator_code",
                "indicator_name",
                "year",
                "value",
                "source",
            ]
        )

    frame["year"] = pd.to_numeric(frame["year"], errors="coerce").astype("Int64")
    frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
    frame = frame.dropna(subset=["year", "value"])
    frame = frame.drop_duplicates(subset=["country_code", "indicator_code", "year"], keep="last")
    frame = frame.sort_values(["indicator_code", "year"]).reset_index(drop=True)
    return frame


def _string_or_empty(value: Any) -> str:
    return str(value).strip() if value is not None else ""
