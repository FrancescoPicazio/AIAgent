"""
Memory System v2 - Advanced Retrieval and Knowledge Graph.

Semantic memory retrieval, graph-based relationships, and adaptive learning.
"""

import logging
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class MemoryType(Enum):
    """Types of memory."""
    EPISODIC = "episodic"  # Specific events/conversations
    SEMANTIC = "semantic"  # Knowledge, facts
    PROCEDURAL = "procedural"  # How to do things
    STRUCTURAL = "structural"  # Architecture decisions


class RelationType(Enum):
    """Types of relationships in knowledge graph."""
    DEPENDS_ON = "depends_on"
    RELATED_TO = "related_to"
    IMPLEMENTS = "implements"
    USES = "uses"
    REFINES = "refines"
    CONFLICTS_WITH = "conflicts_with"


@dataclass
class MemoryEntry:
    """Single memory entry."""
    entry_id: str
    content: str
    memory_type: MemoryType
    timestamp: str
    relevance_score: float = 0.0
    tags: List[str] = field(default_factory=list)
    embedding: Optional[List[float]] = None
    access_count: int = 0
    last_accessed: str = ""


@dataclass
class KnowledgeNode:
    """Node in knowledge graph."""
    node_id: str
    label: str
    node_type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    updated_at: str = ""


@dataclass
class KnowledgeRelation:
    """Relation between knowledge nodes."""
    relation_id: str
    source_id: str
    target_id: str
    relation_type: RelationType
    weight: float = 1.0  # Importance weight
    metadata: Dict[str, Any] = field(default_factory=dict)


class EpisodicMemory:
    """
    Episodic memory - specific events and conversations.
    """

    def __init__(self, max_entries: int = 1000):
        """
        Initialize episodic memory.
        
        Args:
            max_entries: Maximum entries to keep
        """
        self.entries: Dict[str, MemoryEntry] = {}
        self.max_entries = max_entries
        logger.info(f"Episodic memory initialized (max: {max_entries})")

    def record_event(self, event_id: str, description: str, tags: List[str] = None) -> MemoryEntry:
        """
        Record an event.
        
        Args:
            event_id: Event identifier
            description: Event description
            tags: Event tags
            
        Returns:
            Memory entry
        """
        entry = MemoryEntry(
            entry_id=event_id,
            content=description,
            memory_type=MemoryType.EPISODIC,
            timestamp=datetime.now().isoformat(),
            tags=tags or [],
            relevance_score=1.0
        )
        
        self.entries[event_id] = entry
        
        # Manage size
        if len(self.entries) > self.max_entries:
            # Remove oldest least accessed entry
            oldest = min(self.entries.values(), 
                        key=lambda x: (x.access_count, x.last_accessed))
            del self.entries[oldest.entry_id]
        
        logger.info(f"Event recorded: {event_id}")
        return entry

    def retrieve_by_tags(self, tags: List[str]) -> List[MemoryEntry]:
        """
        Retrieve entries by tags.
        
        Args:
            tags: Tags to search
            
        Returns:
            Matching entries
        """
        results = []
        for entry in self.entries.values():
            if any(tag in entry.tags for tag in tags):
                results.append(entry)
                entry.access_count += 1
                entry.last_accessed = datetime.now().isoformat()
        
        return sorted(results, key=lambda x: x.relevance_score, reverse=True)

    def get_recent_events(self, limit: int = 10) -> List[MemoryEntry]:
        """Get recent events."""
        entries = sorted(self.entries.values(), 
                        key=lambda x: x.timestamp, reverse=True)
        return entries[:limit]


class SemanticMemory:
    """
    Semantic memory - knowledge and facts.
    """

    def __init__(self):
        """Initialize semantic memory."""
        self.knowledge: Dict[str, str] = {}
        self.access_frequency: Dict[str, int] = {}
        logger.info("Semantic memory initialized")

    def store_fact(self, key: str, value: str) -> bool:
        """
        Store a fact.
        
        Args:
            key: Fact key
            value: Fact value
            
        Returns:
            Success status
        """
        self.knowledge[key] = value
        self.access_frequency[key] = 0
        logger.info(f"Fact stored: {key}")
        return True

    def retrieve_fact(self, key: str) -> Optional[str]:
        """
        Retrieve a fact.
        
        Args:
            key: Fact key
            
        Returns:
            Fact value or None
        """
        if key in self.knowledge:
            self.access_frequency[key] = self.access_frequency.get(key, 0) + 1
            return self.knowledge[key]
        return None

    def search_facts(self, query: str) -> List[Tuple[str, str]]:
        """
        Search facts by partial key match.
        
        Args:
            query: Search query
            
        Returns:
            Matching (key, value) pairs
        """
        results = []
        query_lower = query.lower()
        
        for key, value in self.knowledge.items():
            if query_lower in key.lower():
                results.append((key, value))
                self.access_frequency[key] = self.access_frequency.get(key, 0) + 1
        
        return results

    def get_most_accessed(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get most frequently accessed facts."""
        items = sorted(self.access_frequency.items(), 
                      key=lambda x: x[1], reverse=True)
        return items[:limit]


class KnowledgeGraph:
    """
    Knowledge graph - relationships between concepts.
    """

    def __init__(self):
        """Initialize knowledge graph."""
        self.nodes: Dict[str, KnowledgeNode] = {}
        self.relations: Dict[str, KnowledgeRelation] = {}
        self.adjacency: Dict[str, List[str]] = {}
        logger.info("Knowledge graph initialized")

    def add_node(self, node_id: str, label: str, node_type: str, 
                properties: Dict[str, Any] = None) -> KnowledgeNode:
        """
        Add a node to the graph.
        
        Args:
            node_id: Node identifier
            label: Node label
            node_type: Node type
            properties: Node properties
            
        Returns:
            Knowledge node
        """
        node = KnowledgeNode(
            node_id=node_id,
            label=label,
            node_type=node_type,
            properties=properties or {},
            created_at=datetime.now().isoformat()
        )
        
        self.nodes[node_id] = node
        self.adjacency[node_id] = []
        
        logger.info(f"Node added: {node_id}")
        return node

    def add_relation(self, source_id: str, target_id: str, 
                    relation_type: RelationType, weight: float = 1.0) -> Optional[KnowledgeRelation]:
        """
        Add a relation between nodes.
        
        Args:
            source_id: Source node
            target_id: Target node
            relation_type: Relation type
            weight: Relation weight
            
        Returns:
            Knowledge relation or None
        """
        if source_id not in self.nodes or target_id not in self.nodes:
            logger.warning(f"One or both nodes not found: {source_id}, {target_id}")
            return None

        relation_id = f"{source_id}_{relation_type.value}_{target_id}"
        relation = KnowledgeRelation(
            relation_id=relation_id,
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            weight=weight
        )
        
        self.relations[relation_id] = relation
        self.adjacency[source_id].append(target_id)
        
        logger.info(f"Relation added: {relation_id}")
        return relation

    def find_related_nodes(self, node_id: str, depth: int = 2) -> List[str]:
        """
        Find related nodes up to given depth.
        
        Args:
            node_id: Starting node
            depth: Search depth
            
        Returns:
            List of related node IDs
        """
        if node_id not in self.nodes:
            return []

        visited = set()
        to_visit = [(node_id, 0)]
        related = []

        while to_visit:
            current, current_depth = to_visit.pop(0)
            
            if current in visited or current_depth > depth:
                continue
            
            visited.add(current)
            
            for neighbor in self.adjacency.get(current, []):
                if neighbor not in visited:
                    related.append(neighbor)
                    to_visit.append((neighbor, current_depth + 1))

        return related

    def get_node_context(self, node_id: str) -> Dict[str, Any]:
        """Get complete context for a node."""
        if node_id not in self.nodes:
            return {}

        node = self.nodes[node_id]
        related = self.find_related_nodes(node_id, depth=2)

        return {
            "node": {
                "id": node.node_id,
                "label": node.label,
                "type": node.node_type,
                "properties": node.properties
            },
            "related_nodes": len(related),
            "related_ids": related,
            "created_at": node.created_at,
            "updated_at": node.updated_at
        }


class MemorySystemV2:
    """
    Complete memory system v2 with multiple memory types and knowledge graph.
    """

    def __init__(self):
        """Initialize memory system v2."""
        self.episodic = EpisodicMemory()
        self.semantic = SemanticMemory()
        self.knowledge_graph = KnowledgeGraph()
        
        logger.info("Memory system v2 initialized")

    def record_conversation(self, conversation_id: str, summary: str, tags: List[str] = None):
        """Record a conversation."""
        return self.episodic.record_event(conversation_id, summary, tags)

    def store_knowledge(self, key: str, value: str):
        """Store knowledge fact."""
        return self.semantic.store_fact(key, value)

    def retrieve_knowledge(self, key: str):
        """Retrieve knowledge fact."""
        return self.semantic.retrieve_fact(key)

    def add_concept(self, concept_id: str, label: str, properties: Dict[str, Any] = None):
        """Add concept to knowledge graph."""
        return self.knowledge_graph.add_node(concept_id, label, "concept", properties)

    def relate_concepts(self, source_id: str, target_id: str, relation_type: RelationType):
        """Create relationship between concepts."""
        return self.knowledge_graph.add_relation(source_id, target_id, relation_type)

    def get_comprehensive_memory(self, query: str) -> Dict[str, Any]:
        """
        Get comprehensive memory context for a query.
        
        Args:
            query: Query string
            
        Returns:
            Comprehensive memory context
        """
        # Search semantic memory
        semantic_results = self.semantic.search_facts(query)
        
        # Search episodic memory
        episodic_results = self.episodic.retrieve_by_tags(query.split())

        return {
            "query": query,
            "semantic_facts": len(semantic_results),
            "episodic_events": len(episodic_results),
            "facts": [
                {"key": k, "value": v} for k, v in semantic_results[:5]
            ],
            "events": [
                {
                    "id": e.entry_id,
                    "content": e.content,
                    "timestamp": e.timestamp
                }
                for e in episodic_results[:5]
            ],
            "timestamp": datetime.now().isoformat()
        }

    def get_system_status(self) -> Dict[str, Any]:
        """Get memory system status."""
        return {
            "episodic_entries": len(self.episodic.entries),
            "semantic_facts": len(self.semantic.knowledge),
            "graph_nodes": len(self.knowledge_graph.nodes),
            "graph_relations": len(self.knowledge_graph.relations),
            "most_accessed_facts": self.semantic.get_most_accessed(5),
            "initialized_at": datetime.now().isoformat()
        }


def create_memory_system_v2() -> MemorySystemV2:
    """Factory function."""
    return MemorySystemV2()


