"""
Vector Database and Retrieval Engine for semantic code search.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CodeChunk:
    """
    Un chunk di codice per indicizzazione semantica.
    
    Un chunk è un'unità logica (funzione, classe, modulo), non arbitraria.
    """
    id: str
    type: str  # "function", "class", "module", "comment"
    name: str
    file: str
    code: str
    description: str = ""
    language: str = ""
    context: str = ""
    dependencies: List[str] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "name": self.name,
            "file": self.file,
            "code": self.code,
            "description": self.description,
            "language": self.language,
            "context": self.context,
            "dependencies": self.dependencies,
        }


class VectorDatabase:
    """
    Vector Database per ricerca semantica del codice.
    
    Nota: Per MVP utilizziamo storage JSON.
    Future: ChromaDB, FAISS, Qdrant.
    """

    def __init__(self, storage_path: Path):
        """
        Inizializza vector DB.
        
        Args:
            storage_path: Path dove salvare gli indici
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.index_file = self.storage_path / "code_index.json"
        self.chunks: Dict[str, CodeChunk] = {}
        self.load()

    def add_chunk(self, chunk: CodeChunk):
        """Aggiungi un chunk all'indice."""
        self.chunks[chunk.id] = chunk
        logger.debug(f"Added chunk: {chunk.id}")

    def add_chunks(self, chunks: List[CodeChunk]):
        """Aggiungi multipli chunk all'indice."""
        for chunk in chunks:
            self.add_chunk(chunk)

    def search(self, query: str, limit: int = 5) -> List[CodeChunk]:
        """
        Ricerca semantica approssimativa (MVP version).
        
        Per MVP usiamo ricerca per keyword.
        Future: Implementare veri embeddings e similarity search.
        
        Args:
            query: Testo di ricerca
            limit: Numero massimo di risultati
            
        Returns:
            Lista di chunk rilevanti
        """
        query_lower = query.lower()
        query_words = set(query_lower.split())

        scores = {}

        for chunk_id, chunk in self.chunks.items():
            score = 0

            # Ricerca nei nomi
            if query_lower in chunk.name.lower():
                score += 10

            # Ricerca nella descrizione
            if query_lower in chunk.description.lower():
                score += 5

            # Ricerca negli endpoint (parole singole)
            for word in query_words:
                if word in chunk.description.lower():
                    score += 1
                if word in chunk.name.lower():
                    score += 1

            if score > 0:
                scores[chunk_id] = score

        # Sort by score descending
        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        result_chunks = [self.chunks[chunk_id] for chunk_id, _ in sorted_results[:limit]]

        logger.info(f"Search query: '{query}' → {len(result_chunks)} results")
        return result_chunks

    def save(self):
        """Salva l'indice su disco."""
        data = {
            "chunks": {chunk_id: chunk.to_dict() for chunk_id, chunk in self.chunks.items()}
        }
        with open(self.index_file, "w") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Vector index saved: {len(self.chunks)} chunks")

    def load(self):
        """Carica l'indice da disco."""
        if self.index_file.exists():
            try:
                with open(self.index_file, "r") as f:
                    data = json.load(f)
                    for chunk_id, chunk_data in data.get("chunks", {}).items():
                        chunk = CodeChunk(
                            id=chunk_data["id"],
                            type=chunk_data["type"],
                            name=chunk_data["name"],
                            file=chunk_data["file"],
                            code=chunk_data["code"],
                            description=chunk_data.get("description", ""),
                            language=chunk_data.get("language", ""),
                            context=chunk_data.get("context", ""),
                            dependencies=chunk_data.get("dependencies", []),
                        )
                        self.chunks[chunk_id] = chunk
                logger.info(f"Vector index loaded: {len(self.chunks)} chunks")
            except Exception as e:
                logger.error(f"Error loading vector index: {e}")
        else:
            logger.info("Vector index file not found, starting fresh")

    def get_chunk(self, chunk_id: str) -> Optional[CodeChunk]:
        """Ritorna un chunk per ID."""
        return self.chunks.get(chunk_id)

    def delete_chunk(self, chunk_id: str):
        """Elimina un chunk dall'indice."""
        if chunk_id in self.chunks:
            del self.chunks[chunk_id]
            logger.info(f"Deleted chunk: {chunk_id}")

    def clear(self):
        """Cancella tutto l'indice."""
        self.chunks.clear()
        logger.info("Vector index cleared")


class RetrievalEngine:
    """
    Motore di retrieval che combina ricerca vettoriale e dependency graph.
    
    Costruisce il contesto per gli agenti LLM.
    """

    def __init__(self, vector_db: VectorDatabase, dependency_graph: Any):
        """
        Inizializza il retrieval engine.
        
        Args:
            vector_db: Istanza del Vector Database
            dependency_graph: Istanza del DependencyGraph
        """
        self.vector_db = vector_db
        self.dependency_graph = dependency_graph

    def build_context(self, query: str, max_chunks: int = 10) -> Dict[str, Any]:
        """
        Costruisce il contesto per un task/query.
        
        Combina:
        1. Ricerca vettoriale per similarità
        2. Analisi dependency graph per impatto
        
        Args:
            query: Descrizione del task
            max_chunks: Numero max di chunk da includere
            
        Returns:
            Dizionario con contesto strutturato
        """
        logger.info(f"Building context for query: {query}")

        # 1. Ricerca semantica
        relevant_chunks = self.vector_db.search(query, limit=max_chunks // 2)

        # 2. Estrai file interessati
        affected_files = set()
        for chunk in relevant_chunks:
            affected_files.add(chunk.file)

        # 3. Per ogni file, cerca relazioni nel dependency graph
        related_functions = []
        for chunk in relevant_chunks:
            node_id = f"{chunk.file}:{chunk.name}"
            dependencies = self.dependency_graph.get_dependencies(node_id)
            dependents = self.dependency_graph.get_dependents(node_id)
            related_functions.append({
                "node": node_id,
                "dependencies": list(dependencies),
                "dependents": list(dependents),
            })

        context = {
            "query": query,
            "relevant_chunks": [chunk.to_dict() for chunk in relevant_chunks],
            "affected_files": sorted(list(affected_files)),
            "related_functions": related_functions,
            "chunk_count": len(relevant_chunks),
            "file_count": len(affected_files),
        }

        logger.info(f"Context built: {len(relevant_chunks)} chunks, {len(affected_files)} files")
        return context

    def get_file_context(self, file_path: str) -> Dict[str, Any]:
        """
        Ritorna tutto il contesto per un file specifico.
        
        Args:
            file_path: Path del file
            
        Returns:
            Contesto strutturato per il file
        """
        file_chunks = [chunk for chunk in self.vector_db.chunks.values() if chunk.file == file_path]

        functions = [chunk for chunk in file_chunks if chunk.type == "function"]
        classes = [chunk for chunk in file_chunks if chunk.type == "class"]

        return {
            "file": file_path,
            "function_count": len(functions),
            "class_count": len(classes),
            "functions": [chunk.to_dict() for chunk in functions],
            "classes": [chunk.to_dict() for chunk in classes],
        }

    def get_impact_analysis(self, node_id: str) -> Dict[str, Any]:
        """
        Analizza l'impatto di una modifica su un nodo.
        
        Args:
            node_id: Identificatore del nodo (es. "file.py:function_name")
            
        Returns:
            Analisi di impatto
        """
        impact = self.dependency_graph.get_impact(node_id)
        
        affected_chunks = []
        for affected_node in impact["affected_nodes"]:
            for chunk in self.vector_db.chunks.values():
                chunk_node = f"{chunk.file}:{chunk.name}"
                if chunk_node == affected_node:
                    affected_chunks.append(chunk.to_dict())

        return {
            **impact,
            "affected_chunks": affected_chunks,
        }


class ContextBuilder:
    """
    Construisce contesto strutturato per gli agenti.
    
    Input: task description
    Output: Contesto con file, funzioni, dipendenze rilevanti
    """

    def __init__(self, retrieval_engine: RetrievalEngine):
        """
        Inizializza il context builder.
        
        Args:
            retrieval_engine: Istanza del RetrievalEngine
        """
        self.retrieval_engine = retrieval_engine

    def build(self, task_description: str, include_impact_analysis: bool = True) -> Dict[str, Any]:
        """
        Costruisce contesto completo per un task.
        
        Args:
            task_description: Descrizione del task
            include_impact_analysis: Se includere analisi d'impatto
            
        Returns:
            Contesto strutturato
        """
        base_context = self.retrieval_engine.build_context(task_description)

        context = {
            "task": task_description,
            "relevant_code": base_context["relevant_chunks"],
            "files_to_modify": base_context["affected_files"],
            "related_functions": base_context["related_functions"],
            "statistics": {
                "relevant_chunks": base_context["chunk_count"],
                "affected_files": base_context["file_count"],
            }
        }

        if include_impact_analysis:
            # Se è stato trovato un file, analizza l'impatto
            if base_context["affected_files"]:
                primary_file = base_context["affected_files"][0]
                for chunk in base_context["relevant_chunks"]:
                    if chunk["file"] == primary_file:
                        node_id = f"{chunk['file']}:{chunk['name']}"
                        context["impact_analysis"] = self.retrieval_engine.get_impact_analysis(node_id)
                        break

        logger.info(f"Context built for task: {task_description}")
        return context


# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

