"""
Test per Code Intelligence Layer.

Valida: Scanner, Dependency Graph, Vector DB, Retrieval Engine.
"""

import json
import pytest
from pathlib import Path
from core.code_intelligence import (
    CodeScanner, DependencyGraph, FunctionMetadata, ClassMetadata,
    CodeIntelligenceLayer
)
from core.vector_database import (
    VectorDatabase, CodeChunk, RetrievalEngine, ContextBuilder
)


class TestCodeScanner:
    """Test per CodeScanner."""

    def test_scanner_init(self):
        """Test inizializzazione scanner."""
        scanner = CodeScanner(".")
        assert scanner.root_path == Path(".")
        assert len(scanner.SUPPORTED_LANGUAGES) > 0

    def test_scanner_scan(self):
        """Test scansione repository."""
        scanner = CodeScanner(".")
        results = scanner.scan()
        
        assert "languages" in results
        assert "file_count" in results
        assert results["file_count"] >= 0
        assert len(results["languages"]) >= 0

    def test_language_detection(self):
        """Test riconoscimento linguaggi."""
        scanner = CodeScanner(".")
        ext_to_lang = scanner.SUPPORTED_LANGUAGES
        
        assert ".py" in ext_to_lang
        assert ext_to_lang[".py"] == "Python"
        assert ".js" in ext_to_lang


class TestDependencyGraph:
    """Test per DependencyGraph."""

    def test_graph_init(self):
        """Test inizializzazione grafo."""
        graph = DependencyGraph()
        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0

    def test_add_node(self):
        """Test aggiunta di un nodo."""
        graph = DependencyGraph()
        metadata = {"name": "test_function", "file": "test.py"}
        
        graph.add_node("test.py:test_function", "function", metadata)
        
        assert "test.py:test_function" in graph.nodes
        assert graph.nodes["test.py:test_function"]["type"] == "function"

    def test_add_edge(self):
        """Test aggiunta di un arco."""
        graph = DependencyGraph()
        
        graph.add_node("file1.py:func1", "function", {})
        graph.add_node("file2.py:func2", "function", {})
        graph.add_edge("file1.py:func1", "file2.py:func2")
        
        assert "file2.py:func2" in graph.edges["file1.py:func1"]
        assert "file1.py:func1" in graph.reverse_edges["file2.py:func2"]

    def test_get_dependents(self):
        """Test reperimento dipendenti."""
        graph = DependencyGraph()
        
        graph.add_node("core.py:process", "function", {})
        graph.add_node("service.py:call_process", "function", {})
        graph.add_edge("service.py:call_process", "core.py:process")
        
        dependents = graph.get_dependents("core.py:process")
        assert "service.py:call_process" in dependents

    def test_impact_analysis(self):
        """Test analisi d'impatto."""
        graph = DependencyGraph()
        
        # Crea una catena: A → B → C → D
        graph.add_node("a.py:A", "function", {})
        graph.add_node("b.py:B", "function", {})
        graph.add_node("c.py:C", "function", {})
        graph.add_node("d.py:D", "function", {})
        
        graph.add_edge("b.py:B", "a.py:A")
        graph.add_edge("c.py:C", "b.py:B")
        graph.add_edge("d.py:D", "c.py:C")
        
        impact = graph.get_impact("a.py:A")
        
        assert impact["modified_node"] == "a.py:A"
        assert len(impact["affected_nodes"]) > 0
        assert impact["risk_level"] in ["LOW", "MEDIUM", "HIGH"]

    def test_graph_serialization(self):
        """Test serializzazione grafo."""
        graph = DependencyGraph()
        
        graph.add_node("test.py:func", "function", {})
        graph.add_edge("test.py:func", "other.py:other")
        
        data = graph.to_dict()
        
        assert "nodes" in data
        assert "edges" in data
        assert "test.py:func" in data["nodes"]


class TestVectorDatabase:
    """Test per VectorDatabase."""

    def test_vdb_init(self, tmp_path):
        """Test inizializzazione vector DB."""
        vdb = VectorDatabase(tmp_path)
        assert len(vdb.chunks) == 0

    def test_add_chunk(self, tmp_path):
        """Test aggiunta chunk."""
        vdb = VectorDatabase(tmp_path)
        
        chunk = CodeChunk(
            id="test1",
            type="function",
            name="test_func",
            file="test.py",
            code="def test_func(): pass",
            description="A test function",
        )
        
        vdb.add_chunk(chunk)
        
        assert "test1" in vdb.chunks
        assert vdb.chunks["test1"].name == "test_func"

    def test_search(self, tmp_path):
        """Test ricerca semantica."""
        vdb = VectorDatabase(tmp_path)
        
        chunks = [
            CodeChunk("1", "function", "authenticate", "auth.py", "code1", "User authentication"),
            CodeChunk("2", "function", "validate", "auth.py", "code2", "Input validation"),
            CodeChunk("3", "function", "process", "data.py", "code3", "Data processing"),
        ]
        
        vdb.add_chunks(chunks)
        
        results = vdb.search("authentication", limit=5)
        
        assert len(results) > 0
        assert results[0].name == "authenticate"

    def test_save_load(self, tmp_path):
        """Test salvataggio e caricamento."""
        vdb1 = VectorDatabase(tmp_path)
        
        chunk = CodeChunk("test1", "function", "func", "file.py", "code", "desc")
        vdb1.add_chunk(chunk)
        vdb1.save()
        
        vdb2 = VectorDatabase(tmp_path)
        
        assert "test1" in vdb2.chunks
        assert vdb2.chunks["test1"].name == "func"


class TestRetrievalEngine:
    """Test per RetrievalEngine."""

    def test_build_context(self, tmp_path):
        """Test costruzione contesto."""
        vdb = VectorDatabase(tmp_path)
        graph = DependencyGraph()
        
        # Setup
        graph.add_node("auth.py:login", "function", {})
        
        chunk = CodeChunk("1", "function", "login", "auth.py", "code", "Login handler")
        vdb.add_chunk(chunk)
        
        engine = RetrievalEngine(vdb, graph)
        context = engine.build_context("authentication login")
        
        assert "query" in context
        assert "relevant_chunks" in context
        assert "affected_files" in context

    def test_get_file_context(self, tmp_path):
        """Test contesto file."""
        vdb = VectorDatabase(tmp_path)
        graph = DependencyGraph()
        
        chunks = [
            CodeChunk("1", "function", "func1", "test.py", "code1", ""),
            CodeChunk("2", "class", "Class1", "test.py", "code2", ""),
            CodeChunk("3", "function", "func2", "other.py", "code3", ""),
        ]
        
        vdb.add_chunks(chunks)
        engine = RetrievalEngine(vdb, graph)
        
        file_context = engine.get_file_context("test.py")
        
        assert file_context["file"] == "test.py"
        assert file_context["function_count"] == 1
        assert file_context["class_count"] == 1


class TestCodeIntelligenceLayer:
    """Test per CodeIntelligenceLayer."""

    def test_init(self, tmp_path):
        """Test inizializzazione layer."""
        layer = CodeIntelligenceLayer(str(tmp_path), ".ai")
        
        assert layer.project_root == tmp_path
        assert (layer.ai_path / "knowledge").exists()
        assert (layer.ai_path / "graph").exists()

    def test_initialize(self, tmp_path):
        """Test inizializzazione completa."""
        layer = CodeIntelligenceLayer(str(tmp_path), ".ai")
        results = layer.initialize()
        
        assert "languages" in results
        assert "file_count" in results
        assert (layer.ai_path / "knowledge" / "project_scan.json").exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

