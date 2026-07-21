from collector.transform import normalize_indicator_records


def test_normalize_indicator_records_deduplicates_and_drops_missing_values() -> None:
    records = [
        {
            "country": {"id": "BR", "value": "Brazil"},
            "indicator": {"id": "SP.POP.TOTL", "value": "Population, total"},
            "date": "2024",
            "value": 211000000,
        },
        {
            "country": {"id": "BR", "value": "Brazil"},
            "indicator": {"id": "SP.POP.TOTL", "value": "Population, total"},
            "date": "2024",
            "value": 212000000,
        },
        {
            "country": {"id": "BR", "value": "Brazil"},
            "indicator": {"id": "SP.POP.TOTL", "value": "Population, total"},
            "date": "2023",
            "value": None,
        },
    ]

    frame = normalize_indicator_records(records, "SP.POP.TOTL")

    assert len(frame) == 1
    assert frame.iloc[0]["year"] == 2024
    assert frame.iloc[0]["value"] == 212000000
