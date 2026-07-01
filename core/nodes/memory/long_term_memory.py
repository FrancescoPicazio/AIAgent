from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Tuple


class LongTermMemory:
    """Persistent long-term memory with semantic retrieval and text fallback."""

    def __init__(
        self,
        memory_file: str = "knowledge/IO/agent_memory.md",
        explicit_memory_file: str = "knowledge/IO/general_memory.md",
        bookshelf_dir: str = "knowledge/bookshelf",
    ):
        self.memory_file = Path(memory_file)
        self.explicit_memory_file = Path(explicit_memory_file)
        self.bookshelf_dir = Path(bookshelf_dir)
        self._vector_db = None
        self._vector_signature: Tuple[Tuple[str, float, int], ...] | None = None

    def add_exchange(self, user_text: str, assistant_text: str) -> None:
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        block = (
            f"\n## {timestamp}\n"
            f"User: {user_text.strip()}\n"
            f"Assistant: {assistant_text.strip()}\n"
        )
        with self.memory_file.open("a", encoding="utf-8") as f:
            f.write(block)
        self._vector_db = None
        self._vector_signature = None

    def retrieve(self, query: str, k: int = 5) -> str:
        docs = self._load_segments()
        if not docs:
            return ""

        semantic = self._semantic_retrieve(query, k)
        if semantic:
            return semantic

        return self._keyword_retrieve(query, docs, k)

    def _source_files(self) -> Iterable[Path]:
        for path in (self.memory_file, self.explicit_memory_file):
            if path.exists():
                yield path

        if self.bookshelf_dir.exists():
            for path in sorted(self.bookshelf_dir.glob("*")):
                if path.suffix.lower() in {".txt", ".md"} and path.exists():
                    yield path

    def _signature(self) -> Tuple[Tuple[str, float, int], ...]:
        signature = []
        for path in self._source_files():
            try:
                stat = path.stat()
                signature.append((str(path), stat.st_mtime, stat.st_size))
            except OSError:
                continue
        return tuple(signature)

    def _load_segments(self) -> List[Tuple[str, str]]:
        segments: List[Tuple[str, str]] = []
        for path in self._source_files():
            try:
                text = path.read_text(encoding="utf-8").strip()
            except UnicodeDecodeError:
                text = path.read_text(encoding="cp1252", errors="ignore").strip()
            except OSError:
                continue

            if not text:
                continue

            parts = [p.strip() for p in text.split("\n\n") if p.strip()]
            for part in parts:
                segments.append((str(path), part[:1800]))
        return segments

    def _semantic_retrieve(self, query: str, k: int, score_threshold: float = 0.45) -> str:
        try:
            from langchain_core.documents import Document
            from langchain_community.vectorstores import FAISS
            from langchain_huggingface import HuggingFaceEmbeddings
        except Exception:
            return ""

        try:
            signature = self._signature()
            if self._vector_db is None or self._vector_signature != signature:
                docs = [
                    Document(page_content=text, metadata={"source": source})
                    for source, text in self._load_segments()
                ]
                if not docs:
                    return ""

                embeddings = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2"
                )
                self._vector_db = FAISS.from_documents(docs, embeddings)
                self._vector_signature = signature

            # similarity_search_with_relevance_scores normalizza lo score in [0, 1]
            # (1 = massima similarità), permettendo una soglia minima coerente.
            results = self._vector_db.similarity_search_with_relevance_score(
                query, k=k
            )
        except Exception:
            return ""

        matches = []
        for doc, score in results:
            if score < score_threshold:
                continue
            source = doc.metadata.get("source", "memory")
            matches.append(f"[{source}] {doc.page_content.strip()}")
        return "\n\n".join(matches)

    @staticmethod
    def _keyword_retrieve(
        query: str,
        docs: List[Tuple[str, str]],
        k: int,
        min_score: int = 2,
    ) -> str:
        terms = {t.lower() for t in query.split() if len(t) > 2}
        if not terms:
            return ""

        scored = []
        for source, text in docs:
            low = text.lower()
            score = sum(1 for term in terms if term in low)
            # Richiede che lo score sia rilevante rispetto al numero di termini
            # della query, non solo un singolo match casuale su query lunghe,
            # e comunque almeno min_score termini in comune.
            if score >= min_score and score >= max(1, len(terms) // 2):
                scored.append((score, source, text))

        scored.sort(key=lambda item: item[0], reverse=True)
        return "\n\n".join(f"[{source}] {text}" for _, source, text in scored[:k])
