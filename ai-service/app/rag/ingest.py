"""
Loads all documents from knowledge_base/, splits them into chunks,
embeds them, and persists them into the Chroma vector store in vector_db/.

Run this manually whenever knowledge_base/ content changes:

    python -m app.rag.ingest
"""

from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings


def load_documents():
    loader = DirectoryLoader(
        str(settings.KNOWLEDGE_BASE_DIR),
        glob="**/*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )
    return loader.load()


def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n## ", "\n# ", "\n\n", "\n", " ", ""],
    )
    return splitter.split_documents(documents)


def build_vector_store():
    documents = load_documents()
    print(f"Loaded {len(documents)} documents from {settings.KNOWLEDGE_BASE_DIR}")

    chunks = split_documents(documents)
    print(f"Split into {len(chunks)} chunks")

    embeddings = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=settings.CHROMA_COLLECTION_NAME,
        persist_directory=str(settings.VECTOR_DB_DIR),
    )

    print(
        f"Persisted {len(chunks)} chunks to "
        f"{settings.VECTOR_DB_DIR} (collection: {settings.CHROMA_COLLECTION_NAME})"
    )
    return vector_store


if __name__ == "__main__":
    build_vector_store()
