"""Test per Memory System v2."""

import pytest
from core.memory_system_v2 import (
    MemoryType, RelationType, MemoryEntry, KnowledgeNode, KnowledgeRelation,
    EpisodicMemory, SemanticMemory, KnowledgeGraph, MemorySystemV2, create_memory_system_v2
)


class TestEpisodicMemory:
    """Test EpisodicMemory."""

    def test_record_event(self):
        """Test recording event."""
        memory = EpisodicMemory()
        entry = memory.record_event("e1", "Test event", ["test"])
        
        assert entry.entry_id == "e1"
        assert entry.memory_type == MemoryType.EPISODIC

    def test_retrieve_by_tags(self):
        """Test retrieval by tags."""
        memory = EpisodicMemory()
        memory.record_event("e1", "Event 1", ["important"])
        memory.record_event("e2", "Event 2", ["important", "bug"])
        
        results = memory.retrieve_by_tags(["important"])
        
        assert len(results) == 2

    def test_get_recent_events(self):
        """Test get recent events."""
        memory = EpisodicMemory()
        memory.record_event("e1", "First")
        memory.record_event("e2", "Second")
        
        recent = memory.get_recent_events(1)
        
        assert len(recent) == 1
        assert recent[0].entry_id == "e2"


class TestSemanticMemory:
    """Test SemanticMemory."""

    def test_store_and_retrieve_fact(self):
        """Test store and retrieve."""
        memory = SemanticMemory()
        memory.store_fact("python_version", "3.11")
        
        value = memory.retrieve_fact("python_version")
        
        assert value == "3.11"

    def test_search_facts(self):
        """Test search facts."""
        memory = SemanticMemory()
        memory.store_fact("language_python", "Dynamic")
        memory.store_fact("language_rust", "Static")
        
        results = memory.search_facts("language")
        
        assert len(results) == 2

    def test_get_most_accessed(self):
        """Test most accessed facts."""
        memory = SemanticMemory()
        memory.store_fact("key1", "val1")
        memory.store_fact("key2", "val2")
        
        # Access key1 multiple times
        memory.retrieve_fact("key1")
        memory.retrieve_fact("key1")
        memory.retrieve_fact("key2")
        
        most_accessed = memory.get_most_accessed(1)
        
        assert most_accessed[0][0] == "key1"


class TestKnowledgeGraph:
    """Test KnowledgeGraph."""

    def test_add_node(self):
        """Test adding node."""
        graph = KnowledgeGraph()
        node = graph.add_node("n1", "Concept 1", "concept")
        
        assert node.node_id == "n1"
        assert "n1" in graph.nodes

    def test_add_relation(self):
        """Test adding relation."""
        graph = KnowledgeGraph()
        graph.add_node("n1", "Concept 1", "concept")
        graph.add_node("n2", "Concept 2", "concept")
        
        relation = graph.add_relation("n1", "n2", RelationType.USES)
        
        assert relation is not None
        assert relation.source_id == "n1"

    def test_find_related_nodes(self):
        """Test finding related nodes."""
        graph = KnowledgeGraph()
        graph.add_node("n1", "C1", "concept")
        graph.add_node("n2", "C2", "concept")
        graph.add_node("n3", "C3", "concept")
        
        graph.add_relation("n1", "n2", RelationType.USES)
        graph.add_relation("n2", "n3", RelationType.RELATED_TO)
        
        related = graph.find_related_nodes("n1", depth=2)
        
        assert "n2" in related
        assert "n3" in related

    def test_get_node_context(self):
        """Test get node context."""
        graph = KnowledgeGraph()
        graph.add_node("n1", "Concept", "concept")
        graph.add_node("n2", "Related", "concept")
        graph.add_relation("n1", "n2", RelationType.USES)
        
        context = graph.get_node_context("n1")
        
        assert context["node"]["id"] == "n1"
        assert context["related_nodes"] == 1


class TestMemorySystemV2:
    """Test MemorySystemV2."""

    def test_creation(self):
        """Test system creation."""
        system = create_memory_system_v2()
        assert system is not None

    def test_record_conversation(self):
        """Test recording conversation."""
        system = create_memory_system_v2()
        entry = system.record_conversation("conv1", "Summary", ["test"])
        
        assert entry.entry_id == "conv1"

    def test_store_and_retrieve_knowledge(self):
        """Test store and retrieve knowledge."""
        system = create_memory_system_v2()
        system.store_knowledge("key1", "value1")
        
        value = system.retrieve_knowledge("key1")
        
        assert value == "value1"

    def test_add_and_relate_concepts(self):
        """Test add and relate concepts."""
        system = create_memory_system_v2()
        system.add_concept("c1", "Concept 1")
        system.add_concept("c2", "Concept 2")
        
        relation = system.relate_concepts("c1", "c2", RelationType.USES)
        
        assert relation is not None

    def test_get_comprehensive_memory(self):
        """Test comprehensive memory retrieval."""
        system = create_memory_system_v2()
        system.store_knowledge("python_version", "3.11")
        system.record_conversation("c1", "Python discussion", ["python"])
        
        memory = system.get_comprehensive_memory("python")
        
        assert memory["semantic_facts"] > 0 or memory["episodic_events"] > 0

    def test_get_system_status(self):
        """Test system status."""
        system = create_memory_system_v2()
        system.store_knowledge("k1", "v1")
        system.add_concept("c1", "Concept")
        
        status = system.get_system_status()
        
        assert status["semantic_facts"] >= 1
        assert status["graph_nodes"] >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

