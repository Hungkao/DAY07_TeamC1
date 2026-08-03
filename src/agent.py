from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        results = self.store.search(question, top_k=top_k)
        if not results:
            return self.llm_fn(
                f"Instruction: Use only the following context to answer the question. If the context is insufficient, state it clearly.\n\n"
                f"Context:\nNo context available.\n\n"
                f"Question: {question}\n\n"
                f"Answer:"
            )

        context_lines = []
        for idx, r in enumerate(results, 1):
            doc_id = r.get("metadata", {}).get("doc_id") or r.get("id", "unknown")
            content = r.get("content", "")
            context_lines.append(f"[{idx}] (Source: {doc_id}) {content}")

        context_str = "\n".join(context_lines)
        prompt = (
            f"Instruction: Use only the following context to answer the question. If the context is insufficient, state it clearly.\n\n"
            f"Context:\n{context_str}\n\n"
            f"Question: {question}\n\n"
            f"Answer:"
        )
        return self.llm_fn(prompt)
