import re

from langchain_core.documents import Document

SECTION_PATTERN = re.compile(
    r"(?m)^(\d+)\.\s+(.+)$"
)


def chunk_by_sections(documents: list[Document]) -> list[Document]:
    if not documents:
        return []

    full_text = "\n".join(document.page_content for document in documents)

    matches = list(SECTION_PATTERN.finditer(full_text))

    if not matches:
        return documents

    chunks = []

    for index, match in enumerate(matches):
        section_number = match.group(1)
        section_title = match.group(2).strip()

        content_start = match.end()

        if index + 1 < len(matches):
            content_end = matches[index + 1].start()
        else:
            content_end = len(full_text)

        section_content = full_text[content_start:content_end].strip()

        chunk_text = (
            f"Section {section_number}: {section_title}\n"
            f"{section_content}"
        )

        metadata = documents[0].metadata.copy()

        metadata.update(
            {
                "section_number": section_number,
                "section_title": section_title,
                "chunk_type": "section",
            }
        )

        chunks.append(
            Document(
                page_content=chunk_text,
                metadata=metadata,
            )
        )

    return chunks