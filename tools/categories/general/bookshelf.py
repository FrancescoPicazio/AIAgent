from pathlib import Path

from langchain.tools import tool
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

BOOKSHELF_DIR = Path("knowledge/bookshelf")
IO_DIR = Path("knowledge/IO")

_vector_db = None  # lazy singleton, costruito alla prima chiamata


def _get_vector_db():
    global _vector_db
    if _vector_db is not None:
        return _vector_db

    if not BOOKSHELF_DIR.exists():
        return None

    docs = []
    files = []
    if BOOKSHELF_DIR.exists():
        files.extend(BOOKSHELF_DIR.glob("*.txt"))
        files.extend(BOOKSHELF_DIR.glob("*.md"))
    if IO_DIR.exists():
        files.extend(IO_DIR.glob("*.md"))

    for file in files:
        try:
            loaded = TextLoader(str(file), encoding="utf-8").load()
            if loaded and loaded[0].page_content.strip():
                docs.extend(loaded)
        except Exception:
            continue  # file illeggibile/vuoto: skip senza far crashare il tool

    if not docs:
        return None

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    _vector_db = FAISS.from_documents(docs, embeddings)
    return _vector_db


@tool
def search_docs(query: str) -> str:
    """Cerca informazioni specifiche nella knowledge base personale (bookshelf).
    Usa questo tool solo quando l'utente chiede qualcosa che potrebbe trovarsi
    nei documenti salvati (note, manuali, ecc.), non per small talk."""
    db = _get_vector_db()
    if db is None:
        return "La knowledge base è vuota o non disponibile."

    results = db.as_retriever(search_kwargs={"k": 3}).invoke(query)
    matches = [d.page_content.strip() for d in results if d.page_content.strip()]
    if not matches:
        return "Nessun risultato trovato nella knowledge base."

    return "Risultato trovato nella knowledge base:\n\n" + "\n\n".join(matches)
