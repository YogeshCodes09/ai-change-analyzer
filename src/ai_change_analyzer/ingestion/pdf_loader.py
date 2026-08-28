from pathlib import Path

from langchain_core.documents import Document
from pypdf import PdfReader


def load_pdf(
    path: str | Path,
    source_type: str,
) -> list[Document]:
    path = Path(path)
    reader = PdfReader(path)

    return [
        Document(
            page_content=page.extract_text() or "",
            metadata={
                "source": str(path),
                "source_type": source_type,
                "file_name": path.name,
                "page": page_number,
            },
        )
        for page_number, page in enumerate(reader.pages)
    ]