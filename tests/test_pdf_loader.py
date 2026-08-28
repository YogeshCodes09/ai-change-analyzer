from ai_change_analyzer.ingestion.pdf_loader import load_pdf


def test_load_sop_pdf() -> None:
    documents = load_pdf(
        "data/sop/card_production_sop.pdf",
        source_type="sop",
    )

    assert len(documents) > 0
    assert documents[0].metadata["source_type"] == "sop"


def test_load_product_pdf() -> None:
    documents = load_pdf(
        "data/product/card_production_solution.pdf",
        source_type="product",
    )

    assert len(documents) > 0
    assert documents[0].metadata["source_type"] == "product"