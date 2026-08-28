from ai_change_analyzer.ingestion.pdf_loader import load_pdf
from ai_change_analyzer.ingestion.section_chunker import chunk_by_sections


def test_card_production_sop_chunking() -> None:
    documents = load_pdf(
        "data/sop/card_production_sop.pdf",
        source_type="sop",
    )

    chunks = chunk_by_sections(documents)

    assert len(chunks) == 9
    assert chunks[0].metadata["section_title"] == "Purpose"
    assert chunks[3].metadata["section_title"] == "Database Failure Handling"


def test_solution_document_chunking() -> None:
    documents = load_pdf(
        "data/product/card_production_solution.pdf",
        source_type="product",
    )

    chunks = chunk_by_sections(documents)

    assert len(chunks) == 10
    assert chunks[8].metadata["section_title"] == "Retry Considerations"