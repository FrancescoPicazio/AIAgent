"""Test per LangGraph Workflow Integration."""

import pytest
from core.langgraph_workflow import (
    LangGraphWorkflow, create_langgraph_workflow
)


class TestLangGraphWorkflow:
    """Test LangGraphWorkflow."""

    def test_workflow_creation(self):
        """Test creazione workflow."""
        workflow = create_langgraph_workflow(".")
        assert workflow is not None
        assert workflow.project_root == "."

    def test_workflow_has_agents(self):
        """Test che workflow ha agenti."""
        workflow = create_langgraph_workflow(".")
        
        assert len(workflow.agents) == 3
        assert "planner" in workflow.agents
        assert "coder" in workflow.agents
        assert "tester" in workflow.agents

    def test_workflow_has_tools(self):
        """Test che workflow ha tool."""
        workflow = create_langgraph_workflow(".")
        
        assert len(workflow.tools) == 3
        assert "filesystem" in workflow.tools
        assert "terminal" in workflow.tools
        assert "git" in workflow.tools

    def test_plan_node(self):
        """Test nodo planning."""
        workflow = create_langgraph_workflow(".")
        state = {"user_request": "Create API"}
        
        result = workflow.plan_node(state)
        
        assert "plan" in result
        assert "tasks" in result["plan"]

    def test_code_node(self):
        """Test nodo coding."""
        workflow = create_langgraph_workflow(".")
        state = {
            "user_request": "Create API",
            "plan": {"tasks": [{"id": 1, "title": "Create model"}]},
            "current_task": {"id": 1}
        }
        
        result = workflow.code_node(state)
        
        assert "code_changes" in result

    def test_test_node(self):
        """Test nodo testing."""
        workflow = create_langgraph_workflow(".")
        state = {"code_changes": {}}
        
        result = workflow.test_node(state)
        
        assert "test_results" in result
        assert "test_status" in result

    def test_router_node_passed(self):
        """Test router quando test passano."""
        workflow = create_langgraph_workflow(".")
        state = {"test_status": "passed", "retry_count": 0}
        
        result = workflow.router_node(state)
        
        assert result == "end"

    def test_router_node_failed_retry(self):
        """Test router quando test falliscono."""
        workflow = create_langgraph_workflow(".")
        state = {"test_status": "failed", "retry_count": 0, "retry_count_max": 3}
        
        result = workflow.router_node(state)
        
        assert result == "code"
        assert state["retry_count"] == 1

    def test_router_node_max_retries(self):
        """Test router quando max retries raggiunto."""
        workflow = create_langgraph_workflow(".")
        state = {"test_status": "failed", "retry_count": 3, "retry_count_max": 3}
        
        result = workflow.router_node(state)
        
        assert result == "end"

    def test_build_graph(self):
        """Test costruzione grafo."""
        workflow = create_langgraph_workflow(".")
        graph = workflow.build_graph()
        
        assert "nodes" in graph
        assert "edges" in graph
        assert "entry_point" in graph
        assert len(graph["nodes"]) == 4

    def test_execute_workflow(self):
        """Test esecuzione completa workflow."""
        workflow = create_langgraph_workflow(".")
        result = workflow.execute("Create a simple function")
        
        assert "user_request" in result
        assert "plan" in result
        assert result["user_request"] == "Create a simple function"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

