from langchain_core.documents import Document

from ai_change_analyzer.retrieval.vector_store import get_vector_store


def search(
    query: str,
    source_type: str,
    k: int = 3,
) -> list[tuple[Document, float]]:
    vector_store = get_vector_store()

    return vector_store.similarity_search_with_score(
        query=query,
        k=k,
        filter={"source_type": source_type},
    )