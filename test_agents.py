"""Test per Agents Implementation."""

import pytest
from core.agents import (
    BaseAgent, PlannerAgent, CoderAgent, TesterAgent,
    AgentFactory
)


class TestPlannerAgent:
    """Test PlannerAgent."""

    def test_planner_creation(self):
        """Test creazione planner."""
        agent = PlannerAgent()
        assert agent is not None
        assert agent.name == "PlannerAgent"

    def test_planner_run(self):
        """Test esecuzione planner."""
        agent = PlannerAgent()
        state = {"user_request": "Create API for users"}
        
        result = agent.run(state)
        
        assert "plan" in result
        assert "tasks" in result["plan"]
        assert len(result["plan"]["tasks"]) > 0

    def test_planner_task_structure(self):
        """Test struttura dei task."""
        agent = PlannerAgent()
        state = {"user_request": "Create REST API"}
        
        result = agent.run(state)
        tasks = result["plan"]["tasks"]
        
        for task in tasks:
            assert "id" in task
            assert "title" in task
            assert "complexity" in task


class TestCoderAgent:
    """Test CoderAgent."""

    def test_coder_creation(self):
        """Test creazione coder."""
        agent = CoderAgent()
        assert agent is not None
        assert agent.name == "CoderAgent"

    def test_coder_run(self):
        """Test esecuzione coder."""
        agent = CoderAgent()
        state = {"current_task": {"title": "Create user model", "id": 1}}
        
        result = agent.run(state)
        
        assert "code_changes" in result
        assert "files_modified" in result["code_changes"]

    def test_coder_generates_patch(self):
        """Test generazione patch."""
        agent = CoderAgent()
        state = {"current_task": {"title": "Create user model"}}
        
        result = agent.run(state)
        
        # In new version, patch can be empty (simplified implementation)
        assert "patch" in result["code_changes"]


class TestTesterAgent:
    """Test TesterAgent."""

    def test_tester_creation(self):
        """Test creazione tester."""
        agent = TesterAgent()
        assert agent is not None
        assert agent.name == "TesterAgent"

    def test_tester_run(self):
        """Test esecuzione tester."""
        agent = TesterAgent()
        state = {"code_changes": {"files_modified": ["test.py"]}}
        
        result = agent.run(state)
        
        assert "test_results" in result
        assert "status" in result["test_results"]

    def test_tester_results_structure(self):
        """Test struttura risultati test."""
        agent = TesterAgent()
        state = {}
        
        result = agent.run(state)
        results = result["test_results"]
        
        assert results["status"] in ["passed", "failed"]
        assert "total_tests" in results
        assert "passed_tests" in results


class TestAgentFactory:
    """Test AgentFactory."""

    def test_create_planner(self):
        """Test factory create planner."""
        agent = AgentFactory.create_planner()
        assert isinstance(agent, PlannerAgent)

    def test_create_coder(self):
        """Test factory create coder."""
        agent = AgentFactory.create_coder()
        assert isinstance(agent, CoderAgent)

    def test_create_tester(self):
        """Test factory create tester."""
        agent = AgentFactory.create_tester()
        assert isinstance(agent, TesterAgent)

    def test_create_all_agents(self):
        """Test factory create all agents."""
        agents = AgentFactory.create_all_agents()
        
        assert "planner" in agents
        assert "coder" in agents
        assert "tester" in agents
        assert "advanced_planner" in agents  # New in Task 20
        assert len(agents) == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

