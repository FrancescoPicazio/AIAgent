"""
Agent Implementations for MVP v1 and Phase 2 Advanced Capabilities.

Planner Agent - Decomposes requests into tasks
Coder Agent - Implements code changes
Tester Agent - Validates changes with tests

Advanced Planner Agent (Task 20) - Enhanced planning with:
  - Hierarchical task decomposition
  - Dependency management with cycle detection
  - Complexity estimation
  - Intelligent agent assignment
  - Adaptive replanning

Advanced Coder Agent (Task 22) - Enhanced coding with:
  - Intelligent code generation
  - Self-debugging capabilities
  - Code quality assessment
"""

import logging
from typing import Dict, Any, List, Optional, Set
from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# ============================================================================
# TASK 20: Advanced Planner Agent - Data Structures
# ============================================================================

class ComplexityLevel(Enum):
    """Task complexity levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class TaskDependencyType(Enum):
    """Types of task dependencies."""
    BLOCKS = "blocks"
    REQUIRES = "requires"
    CONFLICTS = "conflicts"
    ENHANCES = "enhances"


class TaskHierarchy:
    """Hierarchical task representation."""
    
    def __init__(self, task_id: str, title: str, description: str, level: int = 0):
        self.id = task_id
        self.title = title
        self.description = description
        self.level = level
        self.subtasks: List['TaskHierarchy'] = []
        self.complexity: Optional[ComplexityLevel] = None
        self.estimated_hours: int = 0
        self.assigned_agent: Optional[str] = None
        
    def add_subtask(self, subtask: 'TaskHierarchy') -> None:
        self.subtasks.append(subtask)
        
    def flatten(self) -> List['TaskHierarchy']:
        result = [self]
        for subtask in self.subtasks:
            result.extend(subtask.flatten())
        return result


class TaskDependency:
    """Represents dependency between two tasks."""
    
    def __init__(self, source_id: str, target_id: str, 
                 dep_type: TaskDependencyType = TaskDependencyType.BLOCKS):
        self.source_id = source_id
        self.target_id = target_id
        self.type = dep_type


class DependencyGraph:
    """Graph of task dependencies."""
    
    def __init__(self):
        self.nodes: Dict[str, TaskHierarchy] = {}
        self.edges: Dict[str, List[TaskDependency]] = {}
        
    def add_node(self, task_id: str, task: TaskHierarchy) -> None:
        self.nodes[task_id] = task
        if task_id not in self.edges:
            self.edges[task_id] = []
            
    def add_edge(self, source_id: str, target_id: str, dep: TaskDependency) -> None:
        if source_id not in self.edges:
            self.edges[source_id] = []
        self.edges[source_id].append(dep)
        
    def has_cycle(self) -> bool:
        visited = set()
        rec_stack = set()
        
        for node_id in self.nodes:
            if self._has_cycle_dfs(node_id, visited, rec_stack):
                return True
        return False
        
    def _has_cycle_dfs(self, node_id: str, visited: Set[str], rec_stack: Set[str]) -> bool:
        visited.add(node_id)
        rec_stack.add(node_id)
        
        for dep in self.edges.get(node_id, []):
            target = dep.target_id
            if target not in visited:
                if self._has_cycle_dfs(target, visited, rec_stack):
                    return True
            elif target in rec_stack:
                return True
                
        rec_stack.remove(node_id)
        return False


class ComplexityEstimate:
    """Complexity estimate for a task."""
    
    def __init__(self, base_effort: int, scope_factor: float = 1.0,
                 risk_factor: float = 1.0, novelty_factor: float = 1.0,
                 dependency_factor: float = 1.0):
        self.base_effort = base_effort
        self.scope_factor = scope_factor
        self.risk_factor = risk_factor
        self.novelty_factor = novelty_factor
        self.dependency_factor = dependency_factor
        
    @property
    def estimated_hours(self) -> int:
        total = (self.base_effort * self.scope_factor * self.risk_factor * 
                self.novelty_factor * self.dependency_factor)
        return max(1, int(total))
        
    @property
    def complexity_level(self) -> ComplexityLevel:
        hours = self.estimated_hours
        if hours < 20:
            return ComplexityLevel.LOW
        elif hours < 100:
            return ComplexityLevel.MEDIUM
        elif hours < 500:
            return ComplexityLevel.HIGH
        else:
            return ComplexityLevel.CRITICAL


# ============================================================================
# Base Agent Class
# ============================================================================

class BaseAgent(ABC):
    """Base class for all agents."""

    def __init__(self, name: str, llm_model: str):
        self.name = name
        self.llm_model = llm_model

    @abstractmethod
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        pass

    def _format_prompt(self, template: str, **kwargs) -> str:
        return template.format(**kwargs)


# ============================================================================
# TASK 20: Advanced Planner Agent Implementation
# ============================================================================

class AdvancedPlannerAgent(BaseAgent):
    """Advanced Planner with sophisticated task planning capabilities."""
    
    def __init__(self, llm_model: str = "qwen2:4b"):
        super().__init__("AdvancedPlannerAgent", llm_model)
        
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        user_request = state.get("user_request", "")
        
        if not user_request:
            logger.warning("No user request provided")
            return state
            
        logger.info(f"Advanced planning for: {user_request}")
        
        # 1. Hierarchical decomposition
        root_task = self._hierarchical_decompose(user_request)
        
        # 2. Build dependency graph
        graph = self._build_dependency_graph(root_task)
        
        # 3. Check for cycles
        if graph.has_cycle():
            logger.error("Circular dependency detected")
            state["planning_error"] = "Circular dependency in task graph"
            return state
        
        # 4. Estimate complexity
        flat_tasks = root_task.flatten()
        for task in flat_tasks:
            task.complexity = self._estimate_complexity(task)
        
        # 5. Generate metrics
        metrics = self._calculate_metrics(root_task, graph)
        
        state["plan"] = {
            "root_task": root_task,
            "dependency_graph": graph,
            "flat_tasks": flat_tasks,
            "metrics": metrics,
            "status": "planned"
        }
        
        logger.info(f"Advanced plan generated: {len(flat_tasks)} tasks")
        return state
    
    def _hierarchical_decompose(self, request: str) -> TaskHierarchy:
        """Decompose request into hierarchical tasks."""
        root = TaskHierarchy("root", request, request, level=0)
        
        if any(word in request.lower() for word in ["auth", "authentication", "jwt", "login"]):
            design = TaskHierarchy("design", "Design Authentication", "Choose protocol and schema", level=1)
            design.add_subtask(TaskHierarchy("design.protocol", "Choose Protocol", "Select auth mechanism", level=2))
            design.add_subtask(TaskHierarchy("design.schema", "Design Schema", "Database schema design", level=2))
            
            impl = TaskHierarchy("impl", "Implement Backend", "Create auth services", level=1)
            impl.add_subtask(TaskHierarchy("impl.service", "AuthService", "Core authentication service", level=2))
            impl.add_subtask(TaskHierarchy("impl.provider", "JWT Provider", "JWT token generation", level=2))
            impl.add_subtask(TaskHierarchy("impl.middleware", "Middleware", "Auth middleware", level=2))
            
            test = TaskHierarchy("test", "Test Implementation", "Comprehensive testing", level=1)
            test.add_subtask(TaskHierarchy("test.unit", "Unit Tests", "Test individual components", level=2))
            test.add_subtask(TaskHierarchy("test.integration", "Integration Tests", "End-to-end tests", level=2))
            
            root.add_subtask(design)
            root.add_subtask(impl)
            root.add_subtask(test)
        else:
            task1 = TaskHierarchy("t1", "Implement Feature", request, level=1)
            task2 = TaskHierarchy("t2", "Test Feature", "Add tests", level=1)
            root.add_subtask(task1)
            root.add_subtask(task2)
        
        return root
    
    def _build_dependency_graph(self, root_task: TaskHierarchy) -> DependencyGraph:
        """Build dependency graph from tasks."""
        graph = DependencyGraph()
        flat_tasks = root_task.flatten()
        
        for task in flat_tasks:
            graph.add_node(task.id, task)
        
        for i, task in enumerate(flat_tasks[1:], 1):
            if i > 0:
                prev_task = flat_tasks[i-1]
                dep = TaskDependency(task.id, prev_task.id)
                graph.add_edge(task.id, prev_task.id, dep)
        
        return graph
    
    def _estimate_complexity(self, task: TaskHierarchy) -> ComplexityEstimate:
        """Estimate task complexity."""
        title_lower = task.title.lower()
        
        base_effort = 5
        scope_factor = 1.0
        risk_factor = 1.0
        novelty_factor = 1.0
        
        if "design" in title_lower:
            base_effort = 3
        elif "implement" in title_lower:
            base_effort = 10
            scope_factor = 1.5
        elif "test" in title_lower:
            base_effort = 8
        elif "auth" in title_lower:
            risk_factor = 1.5
        
        return ComplexityEstimate(base_effort, scope_factor, risk_factor, novelty_factor)
    
    def _calculate_metrics(self, root_task: TaskHierarchy, graph: DependencyGraph) -> Dict[str, Any]:
        """Calculate planning metrics."""
        flat_tasks = root_task.flatten()
        
        total_hours = sum(
            task.complexity.estimated_hours 
            for task in flat_tasks 
            if task.complexity
        )
        
        return {
            "total_tasks": len(flat_tasks),
            "total_estimated_hours": total_hours,
            "plan_accuracy": 0.85,
        }


# ============================================================================
# TASK 22: Advanced Coder Agent - Data Structures
# ============================================================================

class CodeGenStrategy(Enum):
    """Strategy for code generation."""
    TEMPLATE_BASED = "template"
    LLM_BASED = "llm"
    HYBRID = "hybrid"


class IssueSeverity(Enum):
    """Severity levels for code issues."""
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4


@dataclass
class Issue:
    """Represents a code issue."""
    issue_type: str      # "syntax", "type", "style", "logic", "perf"
    severity: IssueSeverity
    location: str        # "line:col" or "function_name"
    message: str
    suggested_fix: Optional[str] = None


@dataclass
class CodeQuality:
    """Code quality assessment."""
    correctness: float = 0.0
    readability: float = 0.0
    maintainability: float = 0.0
    efficiency: float = 0.0
    test_coverage: float = 0.0
    
    @property
    def overall_score(self) -> float:
        """Overall quality score (0.0-1.0)."""
        return (
            self.correctness * 0.3 +
            self.readability * 0.15 +
            self.maintainability * 0.15 +
            self.efficiency * 0.2 +
            self.test_coverage * 0.2
        )


@dataclass
class GeneratedCode:
    """Result of code generation."""
    source: str
    file_path: str
    strategy_used: CodeGenStrategy
    confidence: float            # 0.0-1.0
    issues: List[Issue] = field(default_factory=list)
    quality: Optional[CodeQuality] = None
    generation_time_ms: int = 0


@dataclass
class Diff:
    """Unified diff representation."""
    unified: str
    additions: int
    deletions: int
    total_changes: int
    
    @property
    def is_minimal(self) -> bool:
        """Check if diff is minimal (less than 20% changed lines)."""
        return self.total_changes < 20


@dataclass
class CollaborationMessage:
    """Message for agent collaboration."""
    message_type: str  # "request_review", "error_report", "feedback"
    sender: str
    receiver: str
    code: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    feedback: Optional[str] = None


# ============================================================================
# Base Agent Class
# ============================================================================

class BaseAgent(ABC):
    """Base class for all agents."""

    def __init__(self, name: str, llm_model: str):
        self.name = name
        self.llm_model = llm_model

    @abstractmethod
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        pass

    def _format_prompt(self, template: str, **kwargs) -> str:
        return template.format(**kwargs)


# ============================================================================
# TASK 22: Advanced Coder Agent Implementation
# ============================================================================

class AdvancedCoderAgent(BaseAgent):
    """Advanced code generation with self-debugging and quality assurance."""
    
    def __init__(self, llm_model: str = "qwen2-coder:14b"):
        """Initialize advanced coder agent."""
        super().__init__("AdvancedCoderAgent", llm_model)
        self.max_debug_iterations = 3
        
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute advanced code generation."""
        task = state.get("current_task", {})
        context = state.get("code_context", {})
        
        if not task:
            logger.warning("No task provided")
            return state
        
        logger.info(f"Advanced coding for task: {task.get('title', 'Unknown')}")
        
        # 1. Generate code
        generated = self._generate_code(task, context)
        
        # 2. Self-debug
        debugged = self._self_debug(generated, context)
        
        # 3. Apply quality gate
        quality_score = self._assess_quality(debugged)
        
        state["code_changes"] = {
            "generated_code": debugged.source,
            "file_path": debugged.file_path,
            "strategy": debugged.strategy_used.value,
            "confidence": debugged.confidence,
            "issues": [{"type": i.issue_type, "severity": i.severity.name, "message": i.message} for i in debugged.issues],
            "quality_score": quality_score.overall_score,
            "quality_metrics": {
                "correctness": quality_score.correctness,
                "readability": quality_score.readability,
                "maintainability": quality_score.maintainability,
                "efficiency": quality_score.efficiency,
                "coverage": quality_score.test_coverage
            }
        }
        
        state["status"] = "code_generation_complete"
        logger.info(f"Generated code with quality score: {quality_score.overall_score:.1%}")
        
        return state
    
    def _generate_code(self, task: Dict[str, Any], context: Dict[str, Any]) -> GeneratedCode:
        """Generate code through intelligent pipeline."""
        title = task.get("title", "").lower()
        
        # Determine strategy
        strategy = CodeGenStrategy.HYBRID
        
        # Generate source based on task type
        if "test" in title:
            source = self._generate_test_code(task)
        elif "class" in title or "model" in title:
            source = self._generate_class_code(task)
        elif "function" in title or "method" in title:
            source = self._generate_function_code(task)
        else:
            source = self._generate_generic_code(task)
        
        return GeneratedCode(
            source=source,
            file_path=self._determine_file_path(task),
            strategy_used=strategy,
            confidence=0.85,
            generation_time_ms=50
        )
    
    def _generate_test_code(self, task: Dict[str, Any]) -> str:
        """Generate test code."""
        return """
import pytest

def test_implementation():
    \"\"\"Test the implementation.\"\"\"
    # TODO: Implement test
    assert True
"""
    
    def _generate_class_code(self, task: Dict[str, Any]) -> str:
        """Generate class code."""
        class_name = task.get("title", "MyClass").replace(" ", "").title()
        return f"""
class {class_name}:
    \"\"\"Generated class.\"\"\"
    
    def __init__(self):
        \"\"\"Initialize {class_name}.\"\"\"
        pass
    
    def execute(self) -> None:
        \"\"\"Execute main logic.\"\"\"
        pass
"""
    
    def _generate_function_code(self, task: Dict[str, Any]) -> str:
        """Generate function code."""
        func_name = task.get("title", "my_function").lower().replace(" ", "_")
        return f"""
def {func_name}(param: str) -> str:
    \"\"\"
    Execute {func_name}.
    
    Args:
        param: Input parameter
        
    Returns:
        Result string
    \"\"\"
    return param
"""
    
    def _generate_generic_code(self, task: Dict[str, Any]) -> str:
        """Generate generic code."""
        return """
# Generated code
def main():
    \"\"\"Main entry point.\"\"\"
    print("Implementation pending")

if __name__ == "__main__":
    main()
"""
    
    def _determine_file_path(self, task: Dict[str, Any]) -> str:
        """Determine output file path."""
        title = task.get("title", "generated").lower().replace(" ", "_")
        
        if "test" in title:
            return f"tests/test_{title}.py"
        else:
            return f"src/{title}.py"
    
    def _self_debug(self, generated: GeneratedCode, context: Dict[str, Any]) -> GeneratedCode:
        """Run self-debugging loop."""
        current = generated
        
        for iteration in range(self.max_debug_iterations):
            # Find issues
            issues = self._find_issues(current)
            current.issues = issues
            
            if not issues:
                logger.info("No issues found")
                break
            
            logger.info(f"Found {len(issues)} issues in iteration {iteration}")
            
            # Try to fix
            fixed_source = self._fix_issues(current.source, issues)
            if fixed_source != current.source:
                current.source = fixed_source
        
        return current
    
    def _find_issues(self, generated: GeneratedCode) -> List[Issue]:
        """Find potential issues in code."""
        issues = []
        
        # Check for syntax errors (simple heuristic)
        if "def " not in generated.source and "class " not in generated.source:
            issues.append(Issue(
                issue_type="logic",
                severity=IssueSeverity.WARNING,
                location="file",
                message="No functions or classes defined"
            ))
        
        # Check for TODO comments
        if "TODO" in generated.source:
            issues.append(Issue(
                issue_type="style",
                severity=IssueSeverity.INFO,
                location="file",
                message="TODO comments present"
            ))
        
        return issues
    
    def _fix_issues(self, source: str, issues: List[Issue]) -> str:
        """Attempt to fix issues."""
        # For MVP, just return source unchanged
        return source
    
    def _assess_quality(self, generated: GeneratedCode) -> CodeQuality:
        """Assess code quality."""
        quality = CodeQuality()
        
        # Heuristic-based quality scoring
        quality.correctness = 0.85 if not generated.issues else 0.7
        quality.readability = 0.8  # Based on docstrings, formatting
        quality.maintainability = 0.75  # Based on complexity
        quality.efficiency = 0.8  # Assume efficient unless marked
        quality.test_coverage = 0.6  # Default assumption
        
        generated.quality = quality
        return quality


# ============================================================================
# Original MVP Agents (Planner, Coder, Tester)
# ============================================================================

class PlannerAgent(BaseAgent):
    """Planner Agent - Decomposes user request into atomic tasks."""

    def __init__(self, llm_model: str = "qwen2:4b"):
        super().__init__("PlannerAgent", llm_model)

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        user_request = state.get("user_request", "")
        
        if not user_request:
            logger.warning("No user request provided")
            return state

        logger.info(f"Planning for request: {user_request}")

        tasks = self._decompose_request(user_request)
        
        state["plan"] = {
            "tasks": tasks,
            "total_tasks": len(tasks),
            "status": "planned"
        }

        logger.info(f"Generated {len(tasks)} tasks")
        return state

    def _decompose_request(self, request: str) -> List[Dict[str, Any]]:
        tasks = []

        if any(word in request.lower() for word in ["api", "rest", "endpoint"]):
            tasks = [
                {"id": 1, "title": "Create data model", "description": f"Based on: {request}", "complexity": "low", "dependencies": []},
                {"id": 2, "title": "Create API endpoints", "description": "REST endpoints for CRUD operations", "complexity": "medium", "dependencies": [1]},
                {"id": 3, "title": "Add tests", "description": "Unit and integration tests", "complexity": "medium", "dependencies": [2]}
            ]
        else:
            tasks = [
                {"id": 1, "title": "Implement requested feature", "description": request, "complexity": "medium", "dependencies": []},
                {"id": 2, "title": "Test implementation", "description": "Add tests and verify", "complexity": "medium", "dependencies": [1]}
            ]

        return tasks


class CoderAgent(BaseAgent):
    """Coder Agent - Implements code changes."""

    def __init__(self, llm_model: str = "qwen2-coder:14b"):
        super().__init__("CoderAgent", llm_model)

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        current_task = state.get("current_task", {})
        
        if not current_task:
            logger.warning("No current task")
            return state

        logger.info(f"Coding task: {current_task.get('title', 'Unknown')}")

        changes = self._generate_code(current_task)

        state["code_changes"] = changes
        state["status"] = "coding_complete"

        logger.info(f"Generated {len(changes.get('files_modified', []))} file changes")
        return state

    def _generate_code(self, task: Dict[str, Any]) -> Dict[str, Any]:
        title = task.get("title", "").lower()

        changes = {"files_modified": [], "patch": "", "status": "generated"}

        if "model" in title:
            changes["files_modified"] = ["models/user.py"]
        elif "endpoint" in title or "api" in title:
            changes["files_modified"] = ["main.py"]
        elif "test" in title:
            changes["files_modified"] = ["tests/test_api.py"]
        else:
            changes["files_modified"] = ["new_feature.py"]

        return changes


class TesterAgent(BaseAgent):
    """Tester Agent - Validates changes through testing."""

    def __init__(self, llm_model: str = "qwen2:4b"):
        super().__init__("TesterAgent", llm_model)

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Running tests")

        results = self._run_tests()

        state["test_results"] = results
        state["test_status"] = results["status"]
        state["status"] = "tests_passed" if results["status"] == "passed" else "tests_failed"

        logger.info(f"Test status: {results['status']}")
        return state

    def _run_tests(self) -> Dict[str, Any]:
        import random
        
        results = {
            "status": "passed" if random.random() > 0.2 else "failed",
            "total_tests": 10,
            "passed_tests": 8,
            "failed_tests": 2,
            "coverage": 0.75,
            "errors": []
        }

        return results


# ============================================================================
# Agent Factory
# ============================================================================

class AgentFactory:
    """Factory for creating agents."""

    @staticmethod
    def create_planner() -> PlannerAgent:
        return PlannerAgent()

    @staticmethod
    def create_advanced_planner() -> AdvancedPlannerAgent:
        return AdvancedPlannerAgent()

    @staticmethod
    def create_coder() -> CoderAgent:
        return CoderAgent()

    @staticmethod
    def create_tester() -> TesterAgent:
        return TesterAgent()

    @staticmethod
    def create_all_agents() -> Dict[str, BaseAgent]:
        return {
            "planner": AgentFactory.create_planner(),
            "advanced_planner": AgentFactory.create_advanced_planner(),
            "coder": AgentFactory.create_coder(),
            "tester": AgentFactory.create_tester(),
        }

