"""
Advanced Code Intelligence Layer - AST Analysis and Dependency Management.

Deep code understanding through abstract syntax tree analysis,
semantic code chunking, vector embeddings, and dependency resolution.

Task 21 Extensions:
- Multi-level code analysis (BASIC/INTERMEDIATE/ADVANCED/EXPERT)
- Semantic code analysis
- Impact assessment
- Intelligent search
- Refactoring suggestions
"""

import logging
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger(__name__)


# ============================================================================
# TASK 21: Advanced Code Intelligence - Data Structures
# ============================================================================

class AnalysisLevel(Enum):
    """Depth of code analysis."""
    BASIC = 1
    INTERMEDIATE = 2
    ADVANCED = 3
    EXPERT = 4


class RiskLevel(Enum):
    """Risk levels for code changes."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class CodeSemantics:
    """Semantic meaning of code."""
    entity_id: str
    entity_type: str  # "function", "class", "module"
    purpose: str = ""
    responsibilities: List[str] = field(default_factory=list)
    interfaces: List[str] = field(default_factory=list)
    complexity: int = 0
    maintainability: float = 0.0


@dataclass
class ImpactAssessment:
    """Assessment of code change impact."""
    change_id: str
    directly_affected: Set[str] = field(default_factory=set)
    indirectly_affected: Set[str] = field(default_factory=set)
    risk_level: str = "LOW"
    affected_areas: Dict[str, str] = field(default_factory=dict)
    cascade_risks: List[str] = field(default_factory=list)


@dataclass
class RefactoringSuggestion:
    """Suggestion for code refactoring."""
    suggestion_type: str
    location: str = ""
    current: str = ""
    suggested: str = ""
    rationale: str = ""
    impact: str = ""
    effort: str = "MEDIUM"


class CodeNodeType(Enum):
    """Types of code nodes in AST."""
    FILE = "file"
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    VARIABLE = "variable"
    IMPORT = "import"
    CONSTANT = "constant"


class DependencyType(Enum):
    """Types of dependencies."""
    IMPORTS = "imports"
    CALLS = "calls"
    INHERITANCE = "inheritance"
    COMPOSITION = "composition"
    TYPES = "types"


@dataclass
class CodeNode:
    """Represents a code element (function, class, etc)."""
    node_id: str
    name: str
    node_type: CodeNodeType
    file_path: str
    line_start: int
    line_end: int
    content: str
    docstring: Optional[str] = None
    parameters: List[str] = field(default_factory=list)
    return_type: Optional[str] = None
    complexity: int = 0  # Cyclomatic complexity
    dependencies: Set[str] = field(default_factory=set)
    dependents: Set[str] = field(default_factory=set)
    embeddings: Optional[List[float]] = None


@dataclass
class CodeChange:
    """Represents a code change and its impact."""
    change_id: str
    file_path: str
    node_id: str
    change_type: str  # "added", "modified", "deleted"
    old_code: Optional[str] = None
    new_code: Optional[str] = None
    affected_nodes: List[str] = field(default_factory=list)
    impact_score: float = 0.0  # 0.0-1.0
    risk_level: str = "low"  # "low", "medium", "high"


class ASTAnalyzer:
    """
    Advanced AST analysis for code understanding.
    
    Extracts functions, classes, dependencies from Python code.
    """

    def __init__(self):
        """Initialize AST analyzer."""
        self.nodes: Dict[str, CodeNode] = {}
        logger.info("AST analyzer initialized")

    def analyze_file(self, file_path: str, content: str) -> List[CodeNode]:
        """
        Analyze a Python file and extract code elements.
        
        Args:
            file_path: Path to file
            content: File content
            
        Returns:
            List of CodeNode objects
        """
        nodes = []
        
        try:
            import ast
            tree = ast.parse(content)
            
            # Extract classes and functions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    code_node = self._extract_function(node, file_path, content)
                    if code_node:
                        nodes.append(code_node)
                        self.nodes[code_node.node_id] = code_node
                
                elif isinstance(node, ast.ClassDef):
                    code_node = self._extract_class(node, file_path, content)
                    if code_node:
                        nodes.append(code_node)
                        self.nodes[code_node.node_id] = code_node
                
                elif isinstance(node, ast.ImportFrom) or isinstance(node, ast.Import):
                    code_node = self._extract_import(node, file_path, content)
                    if code_node:
                        nodes.append(code_node)
                        self.nodes[code_node.node_id] = code_node
            
            logger.info(f"Analyzed {file_path}: found {len(nodes)} code elements")
            return nodes
        
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            return []

    def _extract_function(self, node: Any, file_path: str, content: str) -> Optional[CodeNode]:
        """Extract function details."""
        try:
            import ast
            lines = content.split('\n')
            docstring = ast.get_docstring(node)
            
            # Extract parameters
            params = [arg.arg for arg in node.args.args]
            
            # Get return type annotation
            return_type = None
            if node.returns:
                return_type = ast.unparse(node.returns) if hasattr(ast, 'unparse') else str(node.returns)
            
            code_node = CodeNode(
                node_id=f"{file_path}::function::{node.name}",
                name=node.name,
                node_type=CodeNodeType.FUNCTION,
                file_path=file_path,
                line_start=node.lineno,
                line_end=node.end_lineno or node.lineno,
                content='\n'.join(lines[node.lineno-1:node.end_lineno or node.lineno]),
                docstring=docstring,
                parameters=params,
                return_type=return_type
            )
            
            return code_node
        except Exception as e:
            logger.warning(f"Error extracting function {node.name}: {e}")
            return None

    def _extract_class(self, node: Any, file_path: str, content: str) -> Optional[CodeNode]:
        """Extract class details."""
        try:
            import ast
            lines = content.split('\n')
            docstring = ast.get_docstring(node)
            
            code_node = CodeNode(
                node_id=f"{file_path}::class::{node.name}",
                name=node.name,
                node_type=CodeNodeType.CLASS,
                file_path=file_path,
                line_start=node.lineno,
                line_end=node.end_lineno or node.lineno,
                content='\n'.join(lines[node.lineno-1:node.end_lineno or node.lineno]),
                docstring=docstring
            )
            
            return code_node
        except Exception as e:
            logger.warning(f"Error extracting class {node.name}: {e}")
            return None

    def _extract_import(self, node: Any, file_path: str, content: str) -> Optional[CodeNode]:
        """Extract import details."""
        try:
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                names = [alias.name for alias in node.names]
            else:
                module = ""
                names = [alias.name for alias in node.names]
            
            import_str = f"from {module} import {', '.join(names)}"
            
            code_node = CodeNode(
                node_id=f"{file_path}::import::{module}",
                name=import_str,
                node_type=CodeNodeType.IMPORT,
                file_path=file_path,
                line_start=node.lineno,
                line_end=node.lineno,
                content=import_str
            )
            
            return code_node
        except Exception as e:
            logger.warning(f"Error extracting import: {e}")
            return None

    def get_all_nodes(self) -> Dict[str, CodeNode]:
        """Get all analyzed nodes."""
        return self.nodes.copy()


class DependencyResolver:
    """
    Builds dependency graph and analyzes impact.
    """

    def __init__(self, ast_analyzer: ASTAnalyzer):
        """
        Initialize dependency resolver.
        
        Args:
            ast_analyzer: AST analyzer instance
        """
        self.ast_analyzer = ast_analyzer
        self.dependency_graph: Dict[str, Set[str]] = {}
        logger.info("Dependency resolver initialized")

    def build_dependency_graph(self) -> Dict[str, Set[str]]:
        """
        Build complete dependency graph.
        
        Returns:
            Graph as adjacency list
        """
        nodes = self.ast_analyzer.get_all_nodes()
        
        # For MVP, use simple heuristics
        for node_id, node in nodes.items():
            self.dependency_graph[node_id] = set()
            
            # Find references in content
            for other_id, other_node in nodes.items():
                if node_id != other_id:
                    if other_node.name in node.content:
                        self.dependency_graph[node_id].add(other_id)
        
        logger.info(f"Built dependency graph with {len(self.dependency_graph)} nodes")
        return self.dependency_graph.copy()

    def analyze_change_impact(self, changed_node_id: str) -> Dict[str, Any]:
        """
        Analyze impact of changing a node.
        
        Args:
            changed_node_id: Node that was changed
            
        Returns:
            Impact analysis result
        """
        if not self.dependency_graph:
            self.build_dependency_graph()

        # Find all affected nodes
        affected = set()
        to_check = {changed_node_id}
        
        while to_check:
            current = to_check.pop()
            
            # Find nodes that depend on current
            for node_id, deps in self.dependency_graph.items():
                if current in deps and node_id not in affected:
                    affected.add(node_id)
                    to_check.add(node_id)
        
        # Calculate risk
        risk_score = min(len(affected) / 10.0, 1.0)  # Normalize 0-1
        risk_level = "low"
        if risk_score > 0.66:
            risk_level = "high"
        elif risk_score > 0.33:
            risk_level = "medium"
        
        return {
            "changed_node": changed_node_id,
            "affected_nodes": list(affected),
            "total_affected": len(affected),
            "risk_score": risk_score,
            "risk_level": risk_level
        }

    def get_dependencies(self, node_id: str) -> List[str]:
        """Get direct dependencies of a node."""
        if not self.dependency_graph:
            self.build_dependency_graph()
        
        return list(self.dependency_graph.get(node_id, set()))


class CodeEmbedding:
    """
    Generate semantic embeddings for code chunks.
    
    For MVP, use simple TF-IDF style embeddings.
    In production, would use specialized models.
    """

    def __init__(self):
        """Initialize code embedding."""
        self.embeddings: Dict[str, List[float]] = {}
        self.vocabulary: Set[str] = set()
        logger.info("Code embedding system initialized")

    def embed_code(self, code_node: CodeNode) -> List[float]:
        """
        Generate embedding for code node.
        
        Args:
            code_node: Code node to embed
            
        Returns:
            Embedding vector (list of floats)
        """
        # Simple tokenization
        tokens = self._tokenize_code(code_node.content)
        
        # Build vocabulary
        for token in tokens:
            self.vocabulary.add(token)
        
        # Create vector
        vocab_list = sorted(list(self.vocabulary))
        embedding = [1.0 if token in tokens else 0.0 for token in vocab_list]
        
        # Normalize
        norm = sum(x**2 for x in embedding) ** 0.5
        if norm > 0:
            embedding = [x / norm for x in embedding]
        
        self.embeddings[code_node.node_id] = embedding
        return embedding

    def _tokenize_code(self, code: str) -> Set[str]:
        """Simple code tokenization."""
        import re
        # Split on whitespace and special characters
        tokens = re.findall(r'\b\w+\b', code.lower())
        return set(tokens)

    def find_similar_code(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[str, float]]:
        """Find similar code nodes."""
        scores = []
        
        for node_id, embedding in self.embeddings.items():
            # Cosine similarity
            dot_product = sum(q * e for q, e in zip(query_embedding, embedding))
            scores.append((node_id, dot_product))
        
        # Sort by score
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]


class AdvancedCodeIntelligence:
    """
    Complete advanced code intelligence system.
    """

    def __init__(self):
        """Initialize advanced code intelligence."""
        self.ast_analyzer = ASTAnalyzer()
        self.dependency_resolver = DependencyResolver(self.ast_analyzer)
        self.embeddings = CodeEmbedding()
        
        logger.info("Advanced code intelligence system initialized")

    def analyze_repository(self, files: Dict[str, str]) -> Dict[str, Any]:
        """
        Analyze entire repository.
        
        Args:
            files: Dict of file_path -> content
            
        Returns:
            Complete analysis
        """
        # Analyze all files
        all_nodes = []
        for file_path, content in files.items():
            nodes = self.ast_analyzer.analyze_file(file_path, content)
            all_nodes.extend(nodes)
            
            # Generate embeddings
            for node in nodes:
                self.embeddings.embed_code(node)
        
        # Build dependency graph
        dep_graph = self.dependency_resolver.build_dependency_graph()
        
        return {
            "total_files": len(files),
            "total_code_elements": len(all_nodes),
            "dependency_graph_size": len(dep_graph),
            "code_nodes": [
                {
                    "id": node.node_id,
                    "name": node.name,
                    "type": node.node_type.value,
                    "file": node.file_path,
                    "lines": f"{node.line_start}-{node.line_end}",
                    "dependencies": len(node.dependencies)
                }
                for node in all_nodes
            ]
        }

    def analyze_change_impact(self, changed_file: str, changed_node_id: str) -> Dict[str, Any]:
        """Analyze impact of a code change."""
        return self.dependency_resolver.analyze_change_impact(changed_node_id)

    def get_context_for_node(self, node_id: str) -> Dict[str, Any]:
        """Get context for a specific code node."""
        node = self.ast_analyzer.nodes.get(node_id)
        if not node:
            return {"error": f"Node not found: {node_id}"}
        
        dependencies = self.dependency_resolver.get_dependencies(node_id)
        
        return {
            "node": {
                "id": node.node_id,
                "name": node.name,
                "type": node.node_type.value,
                "file": node.file_path,
                "docstring": node.docstring
            },
            "dependencies": dependencies,
            "impact": self.analyze_change_impact(node.file_path, node_id)
        }


def create_advanced_code_intelligence() -> AdvancedCodeIntelligence:
    """Factory function."""
    return AdvancedCodeIntelligence()


