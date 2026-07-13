"""Test per Advanced Code Intelligence."""

import pytest
from core.advanced_code_intelligence import (
    CodeNodeType, CodeNode, ASTAnalyzer, DependencyResolver,
    CodeEmbedding, AdvancedCodeIntelligence, create_advanced_code_intelligence
)


class TestCodeNode:
    """Test CodeNode."""

    def test_code_node_creation(self):
        """Test creazione code node."""
        node = CodeNode(
            node_id="test::func::main",
            name="main",
            node_type=CodeNodeType.FUNCTION,
            file_path="main.py",
            line_start=1,
            line_end=10,
            content="def main(): pass"
        )
        
        assert node.name == "main"
        assert node.node_type == CodeNodeType.FUNCTION


class TestASTAnalyzer:
    """Test ASTAnalyzer."""

    def test_analyzer_creation(self):
        """Test creazione analyzer."""
        analyzer = ASTAnalyzer()
        assert analyzer is not None

    def test_analyze_simple_file(self):
        """Test analisi file semplice."""
        code = """
def hello():
    return "world"

class MyClass:
    pass
"""
        analyzer = ASTAnalyzer()
        nodes = analyzer.analyze_file("test.py", code)
        
        assert len(nodes) >= 2
        assert any(n.name == "hello" for n in nodes)
        assert any(n.name == "MyClass" for n in nodes)

    def test_extract_function_details(self):
        """Test estrazione dettagli funzione."""
        code = """
def add(a, b):
    '''Add two numbers'''
    return a + b
"""
        analyzer = ASTAnalyzer()
        nodes = analyzer.analyze_file("math.py", code)
        
        func_node = next((n for n in nodes if n.name == "add"), None)
        assert func_node is not None
        assert "a" in func_node.parameters
        assert "b" in func_node.parameters


class TestDependencyResolver:
    """Test DependencyResolver."""

    def test_resolver_creation(self):
        """Test creazione resolver."""
        analyzer = ASTAnalyzer()
        resolver = DependencyResolver(analyzer)
        assert resolver is not None

    def test_build_dependency_graph(self):
        """Test costruzione grafo."""
        code = """
def func_a():
    pass

def func_b():
    func_a()
"""
        analyzer = ASTAnalyzer()
        analyzer.analyze_file("test.py", code)
        
        resolver = DependencyResolver(analyzer)
        graph = resolver.build_dependency_graph()
        
        assert len(graph) > 0

    def test_analyze_change_impact(self):
        """Test analisi impatto."""
        code = """
def base():
    pass

def caller():
    base()
"""
        analyzer = ASTAnalyzer()
        nodes = analyzer.analyze_file("test.py", code)
        
        resolver = DependencyResolver(analyzer)
        resolver.build_dependency_graph()
        
        # Analizza cambio di base
        base_node = next((n for n in nodes if n.name == "base"), None)
        if base_node:
            impact = resolver.analyze_change_impact(base_node.node_id)
            assert "affected_nodes" in impact
            assert "risk_level" in impact


class TestCodeEmbedding:
    """Test CodeEmbedding."""

    def test_embedding_creation(self):
        """Test creazione embedding."""
        embedding = CodeEmbedding()
        assert embedding is not None

    def test_embed_code_node(self):
        """Test embedding di code node."""
        node = CodeNode(
            node_id="test::func",
            name="test",
            node_type=CodeNodeType.FUNCTION,
            file_path="test.py",
            line_start=1,
            line_end=5,
            content="def test(x): return x * 2"
        )
        
        embedding = CodeEmbedding()
        vec = embedding.embed_code(node)
        
        assert len(vec) > 0
        assert all(isinstance(x, float) for x in vec)


class TestAdvancedCodeIntelligence:
    """Test AdvancedCodeIntelligence."""

    def test_creation(self):
        """Test creazione sistema."""
        system = create_advanced_code_intelligence()
        assert system is not None

    def test_analyze_repository(self):
        """Test analisi repository."""
        files = {
            "main.py": "def main(): pass",
            "utils.py": "def helper(): pass"
        }
        
        system = create_advanced_code_intelligence()
        result = system.analyze_repository(files)
        
        assert result["total_files"] == 2
        assert result["total_code_elements"] >= 2

    def test_get_context_for_node(self):
        """Test get context."""
        code = "def test(): pass"
        system = create_advanced_code_intelligence()
        system.ast_analyzer.analyze_file("test.py", code)
        
        nodes = system.ast_analyzer.get_all_nodes()
        if nodes:
            node_id = list(nodes.keys())[0]
            context = system.get_context_for_node(node_id)
            assert "node" in context


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

