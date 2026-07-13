"""
Tests for Task 21: Advanced Code Intelligence Engine.

Testing multi-level analysis, semantic understanding, impact assessment,
and intelligent search capabilities.
"""

import pytest
from core.advanced_code_intelligence import (
    AnalysisLevel, RiskLevel, CodeSemantics, ImpactAssessment,
    RefactoringSuggestion, CodeNode, CodeNodeType, ASTAnalyzer,
    DependencyResolver, CodeEmbedding, AdvancedCodeIntelligence,
    create_advanced_code_intelligence
)


class TestAnalysisLevels:
    """Test analysis level enums."""
    
    def test_analysis_level_values(self):
        """Test analysis level values."""
        assert AnalysisLevel.BASIC.value == 1
        assert AnalysisLevel.INTERMEDIATE.value == 2
        assert AnalysisLevel.ADVANCED.value == 3
        assert AnalysisLevel.EXPERT.value == 4


class TestRiskLevels:
    """Test risk level enums."""
    
    def test_risk_levels(self):
        """Test risk level values."""
        assert RiskLevel.LOW.value == "LOW"
        assert RiskLevel.MEDIUM.value == "MEDIUM"
        assert RiskLevel.HIGH.value == "HIGH"
        assert RiskLevel.CRITICAL.value == "CRITICAL"


class TestCodeSemantics:
    """Test code semantics."""
    
    def test_create_semantics(self):
        """Test creating code semantics."""
        semantics = CodeSemantics(
            entity_id="func_1",
            entity_type="function",
            purpose="Validate user input",
            complexity=5
        )
        
        assert semantics.entity_id == "func_1"
        assert semantics.purpose == "Validate user input"
        assert semantics.complexity == 5
    
    def test_add_responsibility(self):
        """Test adding responsibilities."""
        semantics = CodeSemantics("func_1", "function")
        semantics.responsibilities.append("Check email format")
        
        assert len(semantics.responsibilities) == 1
        assert "Check email format" in semantics.responsibilities


class TestImpactAssessment:
    """Test impact assessment."""
    
    def test_create_assessment(self):
        """Test creating impact assessment."""
        assessment = ImpactAssessment("change_1")
        
        assert assessment.change_id == "change_1"
        assert assessment.risk_level == "LOW"
        assert len(assessment.directly_affected) == 0
    
    def test_add_affected_nodes(self):
        """Test adding affected nodes."""
        assessment = ImpactAssessment("change_1")
        assessment.directly_affected.add("func_1")
        assessment.directly_affected.add("func_2")
        
        assert len(assessment.directly_affected) == 2


class TestRefactoringSuggestion:
    """Test refactoring suggestions."""
    
    def test_create_suggestion(self):
        """Test creating suggestion."""
        suggestion = RefactoringSuggestion(
            suggestion_type="extract_method",
            location="file.py:50-100",
            rationale="Function too long",
            effort="MEDIUM"
        )
        
        assert suggestion.suggestion_type == "extract_method"
        assert suggestion.effort == "MEDIUM"


class TestASTAnalyzer:
    """Test AST analyzer."""
    
    def test_analyzer_creation(self):
        """Test creating analyzer."""
        analyzer = ASTAnalyzer()
        assert len(analyzer.nodes) == 0
    
    def test_analyze_simple_function(self):
        """Test analyzing simple function."""
        analyzer = ASTAnalyzer()
        code = """
def add(a, b):
    '''Add two numbers'''
    return a + b
"""
        nodes = analyzer.analyze_file("test.py", code)
        
        assert len(nodes) >= 1
        assert any("add" in node.name for node in nodes)
    
    def test_analyze_class(self):
        """Test analyzing class."""
        analyzer = ASTAnalyzer()
        code = """
class Calculator:
    '''Simple calculator'''
    
    def add(self, a, b):
        return a + b
"""
        nodes = analyzer.analyze_file("test.py", code)
        
        assert len(nodes) >= 1
        types = [node.node_type for node in nodes]
        assert CodeNodeType.CLASS in types or CodeNodeType.FUNCTION in types
    
    def test_analyzer_stores_nodes(self):
        """Test that analyzer stores nodes."""
        analyzer = ASTAnalyzer()
        code = "def test(): pass"
        nodes = analyzer.analyze_file("test.py", code)
        
        all_nodes = analyzer.get_all_nodes()
        assert len(all_nodes) > 0


class TestDependencyResolver:
    """Test dependency resolver."""
    
    def test_resolver_creation(self):
        """Test creating resolver."""
        analyzer = ASTAnalyzer()
        resolver = DependencyResolver(analyzer)
        assert resolver.dependency_graph == {}
    
    def test_build_graph(self):
        """Test building dependency graph."""
        analyzer = ASTAnalyzer()
        code1 = """
def foo():
    return 42

def bar():
    return foo()
"""
        analyzer.analyze_file("test.py", code1)
        
        resolver = DependencyResolver(analyzer)
        graph = resolver.build_dependency_graph()
        
        assert len(graph) > 0
    
    def test_analyze_impact(self):
        """Test impact analysis."""
        analyzer = ASTAnalyzer()
        code = "def foo(): pass\ndef bar(): pass"
        analyzer.analyze_file("test.py", code)
        
        resolver = DependencyResolver(analyzer)
        resolver.build_dependency_graph()
        
        # Find a node ID
        nodes = analyzer.get_all_nodes()
        if nodes:
            first_node_id = list(nodes.keys())[0]
            impact = resolver.analyze_change_impact(first_node_id)
            
            assert "changed_node" in impact
            assert "affected_nodes" in impact
            assert "risk_level" in impact


class TestCodeEmbedding:
    """Test code embeddings."""
    
    def test_embedding_creation(self):
        """Test creating embeddings."""
        embeddings = CodeEmbedding()
        
        node = CodeNode(
            node_id="func_1",
            name="test_func",
            node_type=CodeNodeType.FUNCTION,
            file_path="test.py",
            line_start=1,
            line_end=5,
            content="def test(): return 42"
        )
        
        vector = embeddings.embed_code(node)
        
        assert len(vector) > 0
        assert isinstance(vector, list)
        assert all(isinstance(x, float) for x in vector)
    
    def test_embedding_normalization(self):
        """Test embedding normalization."""
        embeddings = CodeEmbedding()
        
        node = CodeNode(
            node_id="func_1",
            name="test",
            node_type=CodeNodeType.FUNCTION,
            file_path="test.py",
            line_start=1,
            line_end=1,
            content="def test(): pass"
        )
        
        vector = embeddings.embed_code(node)
        
        # Check normalization (L2 norm should be ~1.0)
        norm = sum(x**2 for x in vector) ** 0.5
        assert abs(norm - 1.0) < 0.01 or norm == 0.0  # Allow 1% tolerance
    
    def test_find_similar(self):
        """Test finding similar code."""
        embeddings = CodeEmbedding()
        
        node1 = CodeNode("n1", "func1", CodeNodeType.FUNCTION, "f.py", 1, 1, "def validate_email(): pass")
        node2 = CodeNode("n2", "func2", CodeNodeType.FUNCTION, "f.py", 2, 2, "def check_email(): pass")
        
        embeddings.embed_code(node1)
        embeddings.embed_code(node2)
        
        # Find similar to first node
        vector = embeddings.embeddings["n1"]
        similar = embeddings.find_similar_code(vector, top_k=2)
        
        assert len(similar) <= 2


class TestAdvancedCodeIntelligence:
    """Test complete system."""
    
    def test_system_creation(self):
        """Test creating system."""
        system = AdvancedCodeIntelligence()
        
        assert system.ast_analyzer is not None
        assert system.dependency_resolver is not None
        assert system.embeddings is not None
    
    def test_analyze_repository(self):
        """Test analyzing repository."""
        system = AdvancedCodeIntelligence()
        
        files = {
            "main.py": "def main(): pass",
            "utils.py": "def helper(): pass"
        }
        
        result = system.analyze_repository(files)
        
        assert result["total_files"] == 2
        assert "code_nodes" in result
        assert "total_code_elements" in result
    
    def test_factory_function(self):
        """Test factory function."""
        system = create_advanced_code_intelligence()
        
        assert isinstance(system, AdvancedCodeIntelligence)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

