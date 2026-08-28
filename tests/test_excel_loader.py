from ai_change_analyzer.ingestion.excel_loader import (
    load_changes,
    load_incidents,
)


def test_load_changes() -> None:
    documents = load_changes("data/changes/changes.xlsx")

    assert len(documents) == 5
    assert documents[0].metadata["source_type"] == "change"


def test_load_incidents() -> None:
    documents = load_incidents("data/incidents/incidents.xlsx")

    assert len(documents) == 12
    assert documents[0].metadata["source_type"] == "incident"