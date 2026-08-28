from ai_change_analyzer.ingestion.pipeline import load_knowledge_base


def test_load_knowledge_base() -> None:
    documents = load_knowledge_base()

    assert len(documents) == 43

    source_types = {
        document.metadata["source_type"]
        for document in documents
    }

    assert source_types == {
        "change",
        "incident",
        "sop",
        "product",
    }