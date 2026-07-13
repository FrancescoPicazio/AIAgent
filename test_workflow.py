"""Test per Workflow Orchestrator."""

import pytest
from core.workflow_orchestrator import (
    WorkflowPhase, WorkflowStatus, WorkflowRequest,
    WorkflowOrchestrator, create_workflow_orchestrator
)


class TestWorkflowRequest:
    """Test WorkflowRequest."""

    def test_request_creation(self):
        """Test creazione request."""
        req = WorkflowRequest(
            id="workflow_1",
            user_input="Add authentication",
            timestamp="2026-07-13T00:00:00Z"
        )
        assert req.id == "workflow_1"
        assert req.user_input == "Add authentication"


class TestWorkflowOrchestrator:
    """Test WorkflowOrchestrator."""

    def test_orchestrator_creation(self):
        """Test creazione orchestratore."""
        orch = create_workflow_orchestrator()
        assert len(orch.workflows) == 0
        assert len(orch.reports) == 0

    def test_submit_request(self):
        """Test sottomissione richiesta."""
        orch = create_workflow_orchestrator()
        
        req = WorkflowRequest(
            id="wf_001",
            user_input="Add OAuth",
            timestamp="2026-07-13"
        )
        
        wf_id = orch.submit_request(req)
        
        assert wf_id == "wf_001"
        assert wf_id in orch.workflows
        assert orch.workflows[wf_id]["status"] == WorkflowStatus.PENDING

    def test_get_workflow_status(self):
        """Test get status."""
        orch = create_workflow_orchestrator()
        
        req = WorkflowRequest(
            id="wf_002",
            user_input="Test",
            timestamp="2026-07-13"
        )
        
        orch.submit_request(req)
        status = orch.get_workflow_status("wf_002")
        
        assert status["id"] == "wf_002"
        assert status["status"] == "pending"

    def test_execute_workflow(self):
        """Test esecuzione workflow."""
        orch = create_workflow_orchestrator()
        
        req = WorkflowRequest(
            id="wf_003",
            user_input="Add feature",
            timestamp="2026-07-13"
        )
        
        orch.submit_request(req)
        report = orch.execute_workflow("wf_003")
        
        assert report.status == WorkflowStatus.COMPLETED
        assert report.request_id == "wf_003"

    def test_get_reports(self):
        """Test get reports."""
        orch = create_workflow_orchestrator()
        
        req = WorkflowRequest(
            id="wf_004",
            user_input="Test",
            timestamp="2026-07-13"
        )
        
        orch.submit_request(req)
        orch.execute_workflow("wf_004")
        
        reports = orch.get_reports(WorkflowStatus.COMPLETED)
        assert len(reports) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

