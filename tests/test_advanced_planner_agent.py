"""
Tests for Task 20: Advanced Planner Agent.

Testing hierarchical decomposition, dependency management, cycle detection,
complexity estimation, and metrics calculation.
"""

import pytest
from core.agents import (
    AdvancedPlannerAgent, ComplexityLevel, TaskHierarchy, DependencyGraph,
    TaskDependency, TaskDependencyType, ComplexityEstimate
)


class TestComplexityEstimate:
    """Test complexity estimation."""
    
    def test_complexity_low(self):
        """Test LOW complexity calculation."""
        estimate = ComplexityEstimate(base_effort=10)
        assert estimate.complexity_level == ComplexityLevel.LOW
        assert estimate.estimated_hours < 20
    
    def test_complexity_medium(self):
        """Test MEDIUM complexity calculation."""
        estimate = ComplexityEstimate(base_effort=25)
        assert estimate.complexity_level == ComplexityLevel.MEDIUM
        assert 20 <= estimate.estimated_hours < 100
    
    def test_complexity_high(self):
        """Test HIGH complexity calculation."""
        estimate = ComplexityEstimate(base_effort=150)
        assert estimate.complexity_level == ComplexityLevel.HIGH
        assert 100 <= estimate.estimated_hours < 500
    
    def test_complexity_critical(self):
        """Test CRITICAL complexity calculation."""
        estimate = ComplexityEstimate(base_effort=600)
        assert estimate.complexity_level == ComplexityLevel.CRITICAL
        assert estimate.estimated_hours >= 500
    
    def test_complexity_with_factors(self):
        """Test complexity with adjustment factors."""
        estimate = ComplexityEstimate(
            base_effort=10,
            scope_factor=2.0,
            risk_factor=1.5
        )
        assert estimate.estimated_hours == 30  # 10 * 2.0 * 1.5


class TestTaskHierarchy:
    """Test hierarchical task representation."""
    
    def test_task_creation(self):
        """Test creating a task."""
        task = TaskHierarchy("t1", "Test Task", "A test task", level=0)
        assert task.id == "t1"
        assert task.title == "Test Task"
        assert task.level == 0
        assert len(task.subtasks) == 0
    
    def test_task_with_subtasks(self):
        """Test task with subtasks."""
        root = TaskHierarchy("root", "Root", "Root task", level=0)
        sub1 = TaskHierarchy("sub1", "Subtask 1", "First subtask", level=1)
        sub2 = TaskHierarchy("sub2", "Subtask 2", "Second subtask", level=1)
        
        root.add_subtask(sub1)
        root.add_subtask(sub2)
        
        assert len(root.subtasks) == 2
        assert root.subtasks[0].id == "sub1"
    
    def test_flatten_hierarchy(self):
        """Test flattening hierarchy."""
        root = TaskHierarchy("root", "Root", "", level=0)
        sub1 = TaskHierarchy("sub1", "Sub1", "", level=1)
        subsub1 = TaskHierarchy("subsub1", "SubSub1", "", level=2)
        
        root.add_subtask(sub1)
        sub1.add_subtask(subsub1)
        
        flat = root.flatten()
        assert len(flat) == 3
        assert flat[0].id == "root"
        assert flat[1].id == "sub1"
        assert flat[2].id == "subsub1"


class TestDependencyGraph:
    """Test dependency graph operations."""
    
    def test_graph_creation(self):
        """Test creating dependency graph."""
        graph = DependencyGraph()
        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0
    
    def test_add_node(self):
        """Test adding nodes to graph."""
        graph = DependencyGraph()
        task = TaskHierarchy("t1", "Task 1", "", level=0)
        graph.add_node("t1", task)
        
        assert "t1" in graph.nodes
        assert graph.nodes["t1"].title == "Task 1"
    
    def test_add_edge(self):
        """Test adding edges (dependencies)."""
        graph = DependencyGraph()
        t1 = TaskHierarchy("t1", "Task 1", "", level=0)
        t2 = TaskHierarchy("t2", "Task 2", "", level=0)
        
        graph.add_node("t1", t1)
        graph.add_node("t2", t2)
        
        dep = TaskDependency("t2", "t1")
        graph.add_edge("t2", "t1", dep)
        
        assert len(graph.edges["t2"]) == 1
        assert graph.edges["t2"][0].source_id == "t2"
    
    def test_no_cycle(self):
        """Test graph without cycles."""
        graph = DependencyGraph()
        t1 = TaskHierarchy("t1", "Task 1", "", level=0)
        t2 = TaskHierarchy("t2", "Task 2", "", level=0)
        t3 = TaskHierarchy("t3", "Task 3", "", level=0)
        
        graph.add_node("t1", t1)
        graph.add_node("t2", t2)
        graph.add_node("t3", t3)
        
        graph.add_edge("t2", "t1", TaskDependency("t2", "t1"))
        graph.add_edge("t3", "t2", TaskDependency("t3", "t2"))
        
        assert not graph.has_cycle()
    
    def test_cycle_detection(self):
        """Test cycle detection."""
        graph = DependencyGraph()
        t1 = TaskHierarchy("t1", "Task 1", "", level=0)
        t2 = TaskHierarchy("t2", "Task 2", "", level=0)
        t3 = TaskHierarchy("t3", "Task 3", "", level=0)
        
        graph.add_node("t1", t1)
        graph.add_node("t2", t2)
        graph.add_node("t3", t3)
        
        # Create cycle: t1 -> t2 -> t3 -> t1
        graph.add_edge("t2", "t1", TaskDependency("t2", "t1"))
        graph.add_edge("t3", "t2", TaskDependency("t3", "t2"))
        graph.add_edge("t1", "t3", TaskDependency("t1", "t3"))
        
        assert graph.has_cycle()


class TestAdvancedPlannerAgent:
    """Test Advanced Planner Agent."""
    
    def test_agent_creation(self):
        """Test creating advanced planner agent."""
        agent = AdvancedPlannerAgent()
        assert agent.name == "AdvancedPlannerAgent"
    
    def test_hierarchical_decomposition_generic(self):
        """Test generic task decomposition."""
        agent = AdvancedPlannerAgent()
        root = agent._hierarchical_decompose("Add a new feature")
        
        flat = root.flatten()
        assert len(flat) >= 2
        assert any("implement" in task.title.lower() for task in flat)
    
    def test_hierarchical_decomposition_auth(self):
        """Test authentication-specific decomposition."""
        agent = AdvancedPlannerAgent()
        root = agent._hierarchical_decompose("Add JWT authentication")
        
        flat = root.flatten()
        assert len(flat) >= 5  # Root + design/impl/test + subtasks
        
        titles = [t.title.lower() for t in flat]
        assert any("design" in t for t in titles)
        assert any("implement" in t for t in titles)
        assert any("test" in t for t in titles)
    
    def test_dependency_graph_building(self):
        """Test building dependency graph."""
        agent = AdvancedPlannerAgent()
        root = agent._hierarchical_decompose("Test request")
        graph = agent._build_dependency_graph(root)
        
        assert len(graph.nodes) > 0
        assert not graph.has_cycle()
    
    def test_complexity_estimation(self):
        """Test complexity estimation."""
        agent = AdvancedPlannerAgent()
        
        task_design = TaskHierarchy("d1", "Design Module", "", level=0)
        est_design = agent._estimate_complexity(task_design)
        
        task_impl = TaskHierarchy("i1", "Implement Service", "", level=0)
        est_impl = agent._estimate_complexity(task_impl)
        
        # Implementation should be more complex than design
        assert est_impl.estimated_hours > est_design.estimated_hours
    
    def test_metrics_calculation(self):
        """Test metrics calculation."""
        agent = AdvancedPlannerAgent()
        root = agent._hierarchical_decompose("Test request")
        
        # Estimate all tasks
        for task in root.flatten():
            task.complexity = agent._estimate_complexity(task)
        
        graph = agent._build_dependency_graph(root)
        metrics = agent._calculate_metrics(root, graph)
        
        assert "total_tasks" in metrics
        assert "total_estimated_hours" in metrics
        assert "plan_accuracy" in metrics
        assert metrics["total_tasks"] > 0
        assert metrics["total_estimated_hours"] > 0
    
    def test_full_planning_workflow(self):
        """Test complete planning workflow."""
        agent = AdvancedPlannerAgent()
        state = {"user_request": "Add authentication to the API"}
        
        result = agent.run(state)
        
        assert "plan" in result
        assert "status" in result["plan"]
        assert result["plan"]["status"] == "planned"
        assert "flat_tasks" in result["plan"]
        assert len(result["plan"]["flat_tasks"]) > 0
    
    def test_planning_with_no_request(self):
        """Test planning with no request."""
        agent = AdvancedPlannerAgent()
        state = {}
        
        result = agent.run(state)
        
        assert "plan" not in result  # Should not add plan if no request
    
    def test_auth_planning_detailed(self):
        """Test detailed authentication planning."""
        agent = AdvancedPlannerAgent()
        state = {"user_request": "Add JWT authentication"}
        
        result = agent.run(state)
        
        assert "plan" in result
        plan = result["plan"]
        
        flat_tasks = plan["flat_tasks"]
        
        # Verify structure
        assert len(flat_tasks) >= 8  # Root + 3 levels + multiple subtasks
        
        # Check for specific task types
        task_types = {
            "design": any("design" in t.title.lower() for t in flat_tasks),
            "auth": any("auth" in t.title.lower() for t in flat_tasks),
            "test": any("test" in t.title.lower() for t in flat_tasks),
        }
        
        assert task_types["design"]
        assert task_types["auth"] or task_types["test"]  # At least one of these
    
    def test_metrics_content(self):
        """Test metrics content."""
        agent = AdvancedPlannerAgent()
        state = {"user_request": "Build new feature"}
        
        result = agent.run(state)
        
        metrics = result["plan"]["metrics"]
        
        assert isinstance(metrics["total_tasks"], int)
        assert isinstance(metrics["total_estimated_hours"], int)
        assert isinstance(metrics["plan_accuracy"], float)
        assert 0 <= metrics["plan_accuracy"] <= 1


class TestComplexityLevels:
    """Test complexity level enums."""
    
    def test_complexity_level_values(self):
        """Test complexity level values."""
        assert ComplexityLevel.LOW.value == 1
        assert ComplexityLevel.MEDIUM.value == 2
        assert ComplexityLevel.HIGH.value == 3
        assert ComplexityLevel.CRITICAL.value == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

