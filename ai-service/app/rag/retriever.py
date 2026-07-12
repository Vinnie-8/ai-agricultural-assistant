"""
Provides a retriever over the persisted Chroma vector store, for use by
the chat agent. Assumes app.rag.ingest has already been run at least once
to populate vector_db/.
"""

from functools import lru_cache

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from app.config import settings


@lru_cache(maxsize=1)
def get_vector_store() -> Chroma:
    embeddings = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)
    return Chroma(
        collection_name=settings.CHROMA_COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(settings.VECTOR_DB_DIR),
    )


def get_retriever():
    vector_store = get_vector_store()
    return vector_store.as_retriever(
        search_kwargs={"k": settings.RETRIEVER_TOP_K},
    )
