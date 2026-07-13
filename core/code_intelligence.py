"""
Code Intelligence Layer — Core module for AST analysis, dependency graphs, and vector DB.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class FunctionMetadata:
    """Metadata per una funzione/metodo."""
    name: str
    file: str
    type: str = "function"
    description: str = ""
    inputs: List[Dict[str, str]] = None
    output: str = ""
    dependencies: List[str] = None
    complexity: str = "low"  # low, medium, high
    last_modified: str = ""
    test_coverage: float = 0.0
    adr_reference: str = ""

    def __post_init__(self):
        if self.inputs is None:
            self.inputs = []
        if self.dependencies is None:
            self.dependencies = []

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ClassMetadata:
    """Metadata per una classe."""
    name: str
    file: str
    description: str = ""
    methods: List[str] = None
    dependencies: List[str] = None
    complexity: str = "low"
    last_modified: str = ""
    test_coverage: float = 0.0

    def __post_init__(self):
        if self.methods is None:
            self.methods = []
        if self.dependencies is None:
            self.dependencies = []

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FileAnalysis:
    """Analisi di un singolo file."""
    file_path: str
    language: str
    functions: List[FunctionMetadata] = None
    classes: List[ClassMetadata] = None
    imports: List[str] = None
    exports: List[str] = None

    def __post_init__(self):
        if self.functions is None:
            self.functions = []
        if self.classes is None:
            self.classes = []
        if self.imports is None:
            self.imports = []
        if self.exports is None:
            self.exports = []


class DependencyGraph:
    """
    Grafo delle dipendenze del progetto.
    
    Rappresenta le relazioni tra funzioni, classi e moduli.
    """

    def __init__(self):
        """Inizializza il grafo."""
        self.nodes: Dict[str, Dict[str, Any]] = {}  # node_id → node_data
        self.edges: Dict[str, Set[str]] = {}  # node_id → set di dipendenze
        self.reverse_edges: Dict[str, Set[str]] = {}  # node_id → set di dipendenti

    def add_node(self, node_id: str, node_type: str, metadata: Dict[str, Any]):
        """
        Aggiungi un nodo al grafo.
        
        Args:
            node_id: Identificatore unico (es. "file.py:FunctionName")
            node_type: Tipo di nodo ("function", "class", "module")
            metadata: Informazioni aggiuntive
        """
        self.nodes[node_id] = {
            "type": node_type,
            "metadata": metadata,
            "depth": 0,
        }
        if node_id not in self.edges:
            self.edges[node_id] = set()
        if node_id not in self.reverse_edges:
            self.reverse_edges[node_id] = set()
        logger.debug(f"Added node: {node_id}")

    def add_edge(self, from_node: str, to_node: str):
        """
        Aggiungi un arco (dipendenza) nel grafo.
        
        Args:
            from_node: Nodo che chiama/dipende
            to_node: Nodo che viene chiamato
        """
        if from_node not in self.edges:
            self.edges[from_node] = set()
        if to_node not in self.reverse_edges:
            self.reverse_edges[to_node] = set()

        self.edges[from_node].add(to_node)
        self.reverse_edges[to_node].add(from_node)
        logger.debug(f"Added edge: {from_node} → {to_node}")

    def get_dependents(self, node_id: str) -> Set[str]:
        """
        Ritorna tutti i nodi che dipendono da questo nodo.
        
        Args:
            node_id: Identificatore del nodo
            
        Returns:
            Set di nodi dipendenti
        """
        return self.reverse_edges.get(node_id, set())

    def get_dependencies(self, node_id: str) -> Set[str]:
        """
        Ritorna tutte le dipendenze di questo nodo.
        
        Args:
            node_id: Identificatore del nodo
            
        Returns:
            Set di dipendenze
        """
        return self.edges.get(node_id, set())

    def get_impact(self, node_id: str, max_depth: int = 3) -> Dict[str, Any]:
        """
        Analizza l'impatto di una modifica su un nodo.
        
        Args:
            node_id: Identificatore del nodo modificato
            max_depth: Profondità massima di analisi
            
        Returns:
            Dizionario con analisi d'impatto
        """
        affected = set()
        to_visit = [(node_id, 0)]
        visited = set()

        while to_visit:
            current, depth = to_visit.pop(0)
            if current in visited or depth > max_depth:
                continue

            visited.add(current)
            dependents = self.get_dependents(current)
            affected.update(dependents)

            for dep in dependents:
                to_visit.append((dep, depth + 1))

        risk_level = "LOW"
        if len(affected) > 20:
            risk_level = "HIGH"
        elif len(affected) > 5:
            risk_level = "MEDIUM"

        return {
            "modified_node": node_id,
            "affected_nodes": list(affected),
            "affected_count": len(affected),
            "risk_level": risk_level,
            "dependencies": list(self.get_dependencies(node_id)),
        }

    def to_dict(self) -> Dict[str, Any]:
        """Esporta il grafo come dizionario."""
        return {
            "nodes": self.nodes,
            "edges": {k: list(v) for k, v in self.edges.items()},
            "reverse_edges": {k: list(v) for k, v in self.reverse_edges.items()},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DependencyGraph":
        """Importa il grafo da dizionario."""
        graph = cls()
        graph.nodes = data.get("nodes", {})
        graph.edges = {k: set(v) for k, v in data.get("edges", {}).items()}
        graph.reverse_edges = {k: set(v) for k, v in data.get("reverse_edges", {}).items()}
        return graph


class CodeScanner:
    """
    Scansione del repository per identificare linguaggi, struttura e file.
    """

    SUPPORTED_LANGUAGES = {
        ".py": "Python",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".jsx": "JavaScript",
        ".tsx": "TypeScript",
        ".go": "Go",
        ".rs": "Rust",
        ".java": "Java",
    }

    IGNORE_DIRS = {
        "__pycache__", ".git", ".venv", "venv", "node_modules",
        ".idea", ".vscode", ".pytest_cache", "dist", "build",
        ".ai", "temp", "tmp"
    }

    def __init__(self, root_path: str):
        """
        Inizializza lo scanner.
        
        Args:
            root_path: Percorso radice del repository
        """
        self.root_path = Path(root_path)
        self.languages: Set[str] = set()
        self.files: List[Path] = []

    def scan(self) -> Dict[str, Any]:
        """
        Esegui la scansione del repository.
        
        Returns:
            Dizionario con risultati della scansione
        """
        logger.info(f"Scanning repository: {self.root_path}")

        self._walk_directory(self.root_path)

        languages_by_count = {}
        for file_path in self.files:
            ext = file_path.suffix.lower()
            lang = self.SUPPORTED_LANGUAGES.get(ext, "Unknown")
            if lang != "Unknown":
                languages_by_count[lang] = languages_by_count.get(lang, 0) + 1
                self.languages.add(lang)

        result = {
            "root": str(self.root_path),
            "languages": sorted(list(self.languages)),
            "file_count": len(self.files),
            "language_distribution": languages_by_count,
            "directory_count": len(set(f.parent for f in self.files)),
        }

        logger.info(f"Scan complete: {len(self.files)} files, {len(self.languages)} languages")
        return result

    def _walk_directory(self, path: Path):
        """Ricorsivamente scannerizza directory."""
        for item in path.iterdir():
            if item.name.startswith("."):
                continue
            if item.is_dir():
                if item.name not in self.IGNORE_DIRS:
                    self._walk_directory(item)
            elif item.is_file():
                if item.suffix.lower() in self.SUPPORTED_LANGUAGES:
                    self.files.append(item)

    def get_files_by_language(self, language: str) -> List[Path]:
        """Ritorna file di un linguaggio specifico."""
        target_ext = [k for k, v in self.SUPPORTED_LANGUAGES.items() if v == language]
        return [f for f in self.files if f.suffix.lower() in target_ext]


class CodeIntelligenceLayer:
    """
    Layer principale di intelligenza del codice.
    
    Coordina scanner, parser, dependency graph e vector DB.
    """

    def __init__(self, project_root: str, ai_path: str = ".ai"):
        """
        Inizializza il layer.
        
        Args:
            project_root: Radice del progetto
            ai_path: Path della cartella .ai
        """
        self.project_root = Path(project_root)
        self.ai_path = Path(project_root) / ai_path
        self.graph = DependencyGraph()
        self.scanner = CodeScanner(project_root)
        self.file_analyses: Dict[str, FileAnalysis] = {}
        
        # Crea directory se non esiste
        (self.ai_path / "knowledge").mkdir(parents=True, exist_ok=True)
        (self.ai_path / "graph").mkdir(parents=True, exist_ok=True)

    def initialize(self) -> Dict[str, Any]:
        """
        Esegui scansione iniziale del progetto.
        
        Returns:
            Risultati scansione
        """
        logger.info("Initializing Code Intelligence Layer...")
        
        scan_results = self.scanner.scan()
        self._save_scan_results(scan_results)
        
        logger.info("Code Intelligence Layer initialized")
        return scan_results

    def _save_scan_results(self, results: Dict[str, Any]):
        """Salva risultati scansione in .ai/knowledge."""
        output_file = self.ai_path / "knowledge" / "project_scan.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)
        logger.info(f"Scan results saved to {output_file}")

    def save_graph(self):
        """Salva il dependency graph in .ai/graph."""
        output_file = self.ai_path / "graph" / "dependency_graph.json"
        with open(output_file, "w") as f:
            json.dump(self.graph.to_dict(), f, indent=2)
        logger.info(f"Dependency graph saved to {output_file}")

    def load_graph(self):
        """Carica il dependency graph da .ai/graph."""
        graph_file = self.ai_path / "graph" / "dependency_graph.json"
        if graph_file.exists():
            with open(graph_file, "r") as f:
                data = json.load(f)
                self.graph = DependencyGraph.from_dict(data)
            logger.info(f"Dependency graph loaded from {graph_file}")


# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

