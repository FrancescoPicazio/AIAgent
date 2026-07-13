"""
Test per Multi-Agent System State Definitions.

Valida: AgentState, routing, task definitions.
"""

import pytest
from core.agent_state import (
    AgentState, Task, CodeChange, ReviewComment, TestResult,
    ArchitectureDecision, ApprovalStatus, ReviewStatus, TestStatus,
    AgentRole, NodeType, NodeDefinition, create_agent_state,
    AGENT_NODES, ROUTER_NODES, ROUTER_RULES
)


class TestApprovalStatus:
    """Test enum ApprovalStatus."""

    def test_approval_values(self):
        """Test valori enum."""
        assert ApprovalStatus.PENDING.value == "pending"
        assert ApprovalStatus.APPROVED.value == "approved"
        assert ApprovalStatus.REJECTED.value == "rejected"


class TestTask:
    """Test dataclass Task."""

    def test_task_creation(self):
        """Test creazione task."""
        task = Task(
            id=1,
            title="Add authentication",
            files=["auth.py"],
            dependencies=[],
            risk="medium"
        )

        assert task.id == 1
        assert task.title == "Add authentication"
        assert len(task.files) == 1
        assert task.status == "pending"

    def test_task_with_dependencies(self):
        """Test task con dipendenze."""
        task = Task(
            id=2,
            title="Implement OAuth",
            dependencies=[1],
        )

        assert len(task.dependencies) == 1
        assert 1 in task.dependencies


class TestCodeChange:
    """Test dataclass CodeChange."""

    def test_code_change_creation(self):
        """Test creazione modifica."""
        change = CodeChange(
            file="auth.py",
            original_content="def login(): pass",
            new_content="def login_with_oauth(): pass",
            diff="- def login():\n+ def login_with_oauth():",
            description="Add OAuth support"
        )

        assert change.file == "auth.py"
        assert "login_with_oauth" in change.new_content


class TestArchitectureDecision:
    """Test dataclass ArchitectureDecision."""

    def test_architecture_decision(self):
        """Test decisione architetturale."""
        decision = ArchitectureDecision(
            approach="OAuth2 integration",
            affected_components=["auth_module", "user_service"],
            pattern="Adapter Pattern",
            risk="medium",
            rationale="Enables third-party authentication"
        )

        assert decision.approach == "OAuth2 integration"
        assert len(decision.affected_components) == 2
        assert decision.pattern == "Adapter Pattern"


class TestTestResult:
    """Test dataclass TestResult."""

    def test_test_result_passed(self):
        """Test risultato superato."""
        result = TestResult(
            status="passed",
            total_tests=10,
            passed_tests=10,
            coverage=0.95,
            duration_seconds=2.3
        )

        assert result.status == "passed"
        assert result.passed_tests == 10
        assert result.coverage == 0.95

    def test_test_result_failed(self):
        """Test risultato fallito."""
        result = TestResult(
            status="failed",
            total_tests=10,
            passed_tests=8,
            failed_tests=2,
            errors=[
                {"file": "test_auth.py", "line": 42, "message": "AssertionError"}
            ]
        )

        assert result.status == "failed"
        assert result.failed_tests == 2
        assert len(result.errors) > 0


class TestAgentState:
    """Test AgentState."""

    def test_state_creation(self):
        """Test creazione stato."""
        state = AgentState()

        assert state["user_request"] == ""
        assert state["task_id"] is None
        assert state["status"] == "in_progress"
        assert state["correction_loop_count"] == 0

    def test_state_is_approved(self):
        """Test check approvazione."""
        state = AgentState()
        assert not state.is_approved()

        state["approval_status"] = ApprovalStatus.APPROVED.value
        assert state.is_approved()

    def test_state_is_rejected(self):
        """Test check rifiuto."""
        state = AgentState()
        assert not state.is_rejected()

        state["approval_status"] = ApprovalStatus.REJECTED.value
        assert state.is_rejected()

    def test_state_needs_revision(self):
        """Test check revisione."""
        state = AgentState()
        state["approval_status"] = ApprovalStatus.NEEDS_REVISION.value
        assert state.needs_revision()

    def test_state_review_passed(self):
        """Test check review."""
        state = AgentState()
        assert state.review_passed()

        state["review_status"] = ReviewStatus.NEEDS_FIX.value
        assert not state.review_passed()

    def test_state_tests_passed(self):
        """Test check test."""
        state = AgentState()
        assert state.tests_passed()

        state["test_status"] = TestStatus.FAILED.value
        assert not state.tests_passed()

    def test_state_increment_correction_loop(self):
        """Test incremento loop correzione."""
        state = AgentState()
        assert state["correction_loop_count"] == 0

        state.increment_correction_loop()
        assert state["correction_loop_count"] == 1

    def test_state_can_retry_correction(self):
        """Test check retry."""
        state = AgentState()
        assert state.can_retry_correction()

        state["correction_loop_count"] = 5
        state["max_correction_loops"] = 5
        assert not state.can_retry_correction()

    def test_state_set_failed(self):
        """Test mark failed."""
        state = AgentState()
        state.set_failed("Critical error")

        assert state.is_failed()
        assert state["error_message"] == "Critical error"

    def test_state_set_completed(self):
        """Test mark completed."""
        state = AgentState()
        state.set_completed("Task finished successfully")

        assert state.is_completed()
        assert state["final_output"] == "Task finished successfully"

    def test_state_get_current_task(self):
        """Test get current task."""
        state = AgentState()
        assert state.get_current_task() is None

        task = Task(id=1, title="Test")
        state["current_task"] = task
        assert state.get_current_task() == task

    def test_state_get_task_list(self):
        """Test get task list."""
        state = AgentState()
        assert len(state.get_task_list()) == 0

        tasks = [Task(id=1, title="T1"), Task(id=2, title="T2")]
        state["task_list"] = tasks
        assert len(state.get_task_list()) == 2


class TestNodeDefinition:
    """Test NodeDefinition."""

    def test_node_definition_creation(self):
        """Test creazione definizione nodo."""
        node = NodeDefinition(
            name="test_agent",
            role=AgentRole.ARCHITECT,
            node_type=NodeType.AGENT,
            description="Test agent",
            model="qwen2:4b",
            max_retries=3,
            timeout_seconds=120
        )

        assert node.name == "test_agent"
        assert node.role == AgentRole.ARCHITECT
        assert node.max_retries == 3

    def test_node_definition_router(self):
        """Test definizione nodo router."""
        node = NodeDefinition(
            name="approval_gate",
            role=None,
            node_type=NodeType.APPROVAL,
        )

        assert node.role is None
        assert node.node_type == NodeType.APPROVAL


class TestAgentNodes:
    """Test AGENT_NODES configuration."""

    def test_agent_nodes_exist(self):
        """Test che nodi agenti sono definiti."""
        assert len(AGENT_NODES) >= 6
        
        node_names = [n.name for n in AGENT_NODES]
        assert "architect" in node_names
        assert "planner" in node_names
        assert "coder" in node_names
        assert "reviewer" in node_names
        assert "tester" in node_names

    def test_coder_uses_coder_model(self):
        """Test che coder usa modello coder."""
        coder_node = next(n for n in AGENT_NODES if n.name == "coder")
        assert "coder" in coder_node.model


class TestRouterNodes:
    """Test ROUTER_NODES configuration."""

    def test_router_nodes_exist(self):
        """Test che nodi router sono definiti."""
        assert len(ROUTER_NODES) >= 3
        
        node_names = [n.name for n in ROUTER_NODES]
        assert "approval_gate" in node_names
        assert "correction_decision" in node_names


class TestRouterRules:
    """Test ROUTER_RULES."""

    def test_router_rules_structure(self):
        """Test struttura routing rules."""
        assert "architect" in ROUTER_RULES
        assert "planner" in ROUTER_RULES
        assert "approval_gate" in ROUTER_RULES

    def test_approval_gate_routing(self):
        """Test routing approval gate."""
        approval_rules = ROUTER_RULES["approval_gate"]
        
        assert "approved" in approval_rules
        assert "rejected" in approval_rules
        assert "needs_revision" in approval_rules

    def test_tester_routing(self):
        """Test routing tester."""
        tester_rules = ROUTER_RULES["tester"]
        
        assert "passed" in tester_rules
        assert "failed" in tester_rules


class TestCreateAgentState:
    """Test factory function."""

    def test_create_agent_state(self):
        """Test factory crea stato valido."""
        state = create_agent_state()
        
        assert isinstance(state, AgentState)
        assert state["status"] == "in_progress"
        assert "user_request" in state


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

