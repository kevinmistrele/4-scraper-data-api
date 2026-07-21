from pathlib import Path

import pandas as pd

from storage import get_connection, initialize_database, upsert_indicators


def test_upsert_indicators_updates_existing_row(tmp_path: Path) -> None:
    database_path = tmp_path / "indicators.sqlite"
    initialize_database(database_path)

    frame = pd.DataFrame(
        [
            {
                "country_code": "BR",
                "country_name": "Brazil",
                "indicator_code": "NY.GDP.MKTP.CD",
                "indicator_name": "GDP",
                "year": 2024,
                "value": 1.0,
                "source": "World Bank API",
            }
        ]
    )

    upsert_indicators(frame, database_path)
    frame.loc[0, "value"] = 2.0
    upsert_indicators(frame, database_path)

    with get_connection(database_path) as connection:
        row = connection.execute("SELECT value FROM indicators").fetchone()

    assert row["value"] == 2.0
