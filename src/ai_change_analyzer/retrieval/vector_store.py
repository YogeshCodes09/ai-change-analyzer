from threading import Lock

from langchain_chroma import Chroma

from ai_change_analyzer.retrieval.embeddings import get_embeddings

COLLECTION_NAME = "change_analyzer"
PERSIST_DIRECTORY = "chroma_db"

_vector_store: Chroma | None = None
_vector_store_lock = Lock()


def get_vector_store() -> Chroma:
    global _vector_store

    if _vector_store is None:
        with _vector_store_lock:
            if _vector_store is None:
                _vector_store = Chroma(
                    collection_name=COLLECTION_NAME,
                    embedding_function=get_embeddings(),
                    persist_directory=PERSIST_DIRECTORY,
                )

    return _vector_store