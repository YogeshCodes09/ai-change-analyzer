from ai_change_analyzer.ingestion.pipeline import load_knowledge_base
from ai_change_analyzer.retrieval.vector_store import get_vector_store


def build_index() -> None:
    documents = load_knowledge_base()
    vector_store = get_vector_store()

    existing = vector_store.get()

    if existing["ids"]:
        print(
            f"Vector store already contains {len(existing['ids'])} documents. "
            "Skipping indexing."
        )
        return

    ids = [
        f"document-{index}"
        for index in range(len(documents))
    ]

    vector_store.add_documents(
        documents=documents,
        ids=ids,
    )

    print(f"Indexed {len(documents)} documents.")


if __name__ == "__main__":
    build_index()