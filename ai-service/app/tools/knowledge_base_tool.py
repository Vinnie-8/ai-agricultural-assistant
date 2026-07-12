from langchain_core.tools import tool

from app.rag.retriever import get_retriever


@tool
def search_knowledge_base(query: str) -> str:
    """
    Search the agricultural knowledge base for information on crop
    diseases, fertilizer recommendations, and pesticide/fungicide
    guidance. Use this before giving any specific treatment advice.

    Args:
        query: A specific question or topic, e.g. "fertilizer for maize
            common rust" or "late blight treatment".
    """
    retriever = get_retriever()
    docs = retriever.invoke(query)

    if not docs:
        return "No relevant information found in the knowledge base."

    return "\n\n---\n\n".join(
        f"Source: {doc.metadata.get('source', 'unknown')}\n{doc.page_content}"
        for doc in docs
    )
