from langchain_core.documents import Document

from ai_change_analyzer.ingestion.excel_loader import (
    load_changes,
    load_incidents,
)
from ai_change_analyzer.ingestion.pdf_loader import load_pdf
from ai_change_analyzer.ingestion.section_chunker import chunk_by_sections


def load_knowledge_base() -> list[Document]:
    changes = load_changes("data/changes/changes.xlsx")
    incidents = load_incidents("data/incidents/incidents.xlsx")

    card_sop = chunk_by_sections(
        load_pdf(
            "data/sop/card_production_sop.pdf",
            source_type="sop",
        )
    )

    change_sop = chunk_by_sections(
        load_pdf(
            "data/sop/change_management_sop.pdf",
            source_type="sop",
        )
    )

    product_document = chunk_by_sections(
        load_pdf(
            "data/product/card_production_solution.pdf",
            source_type="product",
        )
    )

    return (
        changes
        + incidents
        + card_sop
        + change_sop
        + product_document
    )