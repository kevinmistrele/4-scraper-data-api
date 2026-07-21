from __future__ import annotations

import time
from typing import Any

import httpx

WORLD_BANK_API_URL = "https://api.worldbank.org/v2/country/{country}/indicator/{indicator}"


class FetchError(RuntimeError):
    """Raised when the source API cannot be fetched."""


def fetch_indicator(
    indicator: str,
    country: str = "BR",
    *,
    per_page: int = 100,
    retries: int = 3,
    timeout: float = 10.0,
) -> list[dict[str, Any]]:
    params = {"format": "json", "per_page": per_page, "page": 1}
    records: list[dict[str, Any]] = []

    with httpx.Client(timeout=timeout, headers={"User-Agent": "scraper-data-api/1.0"}) as client:
        total_pages = 1
        while params["page"] <= total_pages:
            payload = _request_page(client, indicator, country, params, retries)
            if not isinstance(payload, list) or len(payload) < 2:
                raise FetchError("Unexpected response format from World Bank API.")

            metadata = payload[0]
            page_records = payload[1] or []
            total_pages = int(metadata.get("pages", 1))
            records.extend(page_records)
            params["page"] += 1

    return records


def _request_page(
    client: httpx.Client,
    indicator: str,
    country: str,
    params: dict[str, int | str],
    retries: int,
) -> list[Any]:
    url = WORLD_BANK_API_URL.format(country=country, indicator=indicator)
    for attempt in range(1, retries + 1):
        try:
            response = client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPError, ValueError) as exc:
            if attempt == retries:
                raise FetchError(f"Failed to fetch {indicator} after {retries} attempts.") from exc
            time.sleep(2 ** (attempt - 1))

    raise FetchError(f"Failed to fetch {indicator}.")
