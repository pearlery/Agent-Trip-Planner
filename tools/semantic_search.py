from logger_utils import log_retrieved_docs

_vector_store = None


def init_search_tool(vector_store):
    global _vector_store
    _vector_store = vector_store


def semantic_search(query: str, n_results: int = 3) -> str:
    """Search the travel knowledge base using semantic similarity."""
    if _vector_store is None or _vector_store.count() == 0:
        return "Knowledge base is empty. Please add PDF or TXT files to the data/ folder and restart."

    docs, scores, metas = _vector_store.search(query, n_results=n_results)
    log_retrieved_docs(docs, scores, metas)

    if not docs:
        return "No relevant information found."

    parts = [f"Found {len(docs)} relevant results:\n"]
    for i, (doc, score, meta) in enumerate(zip(docs, scores, metas), 1):
        # Support both CSV tour metadata and PDF/TXT source metadata
        if meta.get("program_tour"):
            meta_str = (
                f"tour={meta.get('program_tour', '')}  "
                f"price={meta.get('price', '')}  "
                f"region={meta.get('region', '')}  "
                f"url={meta.get('url', '')}"
            )
        else:
            meta_str = f"source={meta.get('source', 'unknown')}"
        parts.append(f"[{i}] relevance={score:.4f}  {meta_str}\n{doc}\n")
    return "\n".join(parts)
