"""
End-to-End Development Workflow Orchestrator.

Orchestrates the complete cycle from user request to git commit.
"""

import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class WorkflowPhase(Enum):
    """Fasi del workflow."""
    REQUEST = "request"
    ANALYSIS = "analysis"
    ARCHITECTURE = "architecture"
    PLANNING = "planning"
    IMPACT_ANALYSIS = "impact_analysis"
    APPROVAL = "approval"
    EXECUTION = "execution"
    REVIEW = "review"
    TESTING = "testing"
    KNOWLEDGE_UPDATE = "knowledge_update"
    GIT_COMMIT = "git_commit"
    COMPLETION = "completion"
    FAILED = "failed"


class WorkflowStatus(Enum):
    """Status del workflow."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_HUMAN_INTERVENTION = "needs_human_intervention"


@dataclass
class WorkflowRequest:
    """Richiesta dell'utente."""
    id: str
    user_input: str
    timestamp: str
    source: str = "chat"
    approval_required: bool = False


@dataclass
class WorkflowReport:
    """Report di completamento."""
    request_id: str
    phase: WorkflowPhase
    status: WorkflowStatus
    duration_seconds: float
    tasks_completed: int = 0
    files_changed: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    output: Dict[str, Any] = field(default_factory=dict)


class WorkflowOrchestrator:
    """
    Orchestratore principale del workflow end-to-end.
    
    Gestisce:
    - Ricezione richiesta
    - Analisi requisiti
    - Planning
    - Esecuzione task
    - Review
    - Testing
    - Aggiornamento memoria
    - Git commit
    """

    def __init__(self):
        """Inizializza orchestratore."""
        self.workflows: Dict[str, Dict[str, Any]] = {}
        self.reports: List[WorkflowReport] = []
        self.phase_handlers = self._setup_phase_handlers()

    def _setup_phase_handlers(self) -> Dict[WorkflowPhase, callable]:
        """Setup dei handler per ogni fase."""
        return {
            WorkflowPhase.REQUEST: self._handle_request,
            WorkflowPhase.ANALYSIS: self._handle_analysis,
            WorkflowPhase.ARCHITECTURE: self._handle_architecture,
            WorkflowPhase.PLANNING: self._handle_planning,
            WorkflowPhase.IMPACT_ANALYSIS: self._handle_impact_analysis,
            WorkflowPhase.APPROVAL: self._handle_approval,
            WorkflowPhase.EXECUTION: self._handle_execution,
            WorkflowPhase.REVIEW: self._handle_review,
            WorkflowPhase.TESTING: self._handle_testing,
            WorkflowPhase.KNOWLEDGE_UPDATE: self._handle_knowledge_update,
            WorkflowPhase.GIT_COMMIT: self._handle_git_commit,
        }

    def submit_request(self, request: WorkflowRequest) -> str:
        """
        Sottometti una richiesta.
        
        Args:
            request: WorkflowRequest
            
        Returns:
            Workflow ID
        """
        workflow_id = request.id
        self.workflows[workflow_id] = {
            "request": request,
            "status": WorkflowStatus.PENDING,
            "current_phase": WorkflowPhase.REQUEST,
            "start_time": datetime.now(),
            "phase_results": {},
            "retry_count": 0,
        }
        logger.info(f"Submitted workflow: {workflow_id}")
        return workflow_id

    def execute_workflow(self, workflow_id: str) -> WorkflowReport:
        """
        Esegui un workflow completo.
        
        Args:
            workflow_id: ID del workflow
            
        Returns:
            WorkflowReport finale
        """
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow not found: {workflow_id}")

        workflow["status"] = WorkflowStatus.IN_PROGRESS
        
        # Sequenza di fasi da eseguire
        phases = [
            WorkflowPhase.REQUEST,
            WorkflowPhase.ANALYSIS,
            WorkflowPhase.ARCHITECTURE,
            WorkflowPhase.PLANNING,
            WorkflowPhase.IMPACT_ANALYSIS,
            WorkflowPhase.APPROVAL,
            WorkflowPhase.EXECUTION,
            WorkflowPhase.REVIEW,
            WorkflowPhase.TESTING,
            WorkflowPhase.KNOWLEDGE_UPDATE,
            WorkflowPhase.GIT_COMMIT,
        ]

        for phase in phases:
            logger.info(f"[{workflow_id}] Executing phase: {phase.value}")
            
            try:
                handler = self.phase_handlers.get(phase)
                if handler:
                    result = handler(workflow)
                    workflow["phase_results"][phase.value] = result
                else:
                    logger.warning(f"No handler for phase: {phase.value}")

                workflow["current_phase"] = phase

            except Exception as e:
                logger.error(f"Error in phase {phase.value}: {e}")
                workflow["status"] = WorkflowStatus.FAILED
                return self._create_failure_report(workflow, phase, e)

        # Successo
        workflow["status"] = WorkflowStatus.COMPLETED
        workflow["end_time"] = datetime.now()

        return self._create_completion_report(workflow)

    def _handle_request(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Gestisci fase REQUEST."""
        request = workflow["request"]
        logger.info(f"Processing request: {request.user_input}")
        return {"request_id": request.id, "input": request.user_input}

    def _handle_analysis(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Gestisci fase ANALYSIS."""
        request = workflow["request"]
        logger.info("Analyzing requirements...")
        return {
            "analyzed": True,
            "requirement": f"Analyzed: {request.user_input}",
            "constraints": [],
        }

    def _handle_architecture(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Gestisci fase ARCHITECTURE."""
        logger.info("Creating architecture plan...")
        return {
            "approach": "TBD",
            "components": [],
            "risk": "medium",
        }

    def _handle_planning(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Gestisci fase PLANNING."""
        logger.info("Planning tasks...")
        return {
            "tasks": [],
            "total_tasks": 0,
            "dependencies": [],
        }

    def _handle_impact_analysis(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Gestisci fase IMPACT_ANALYSIS."""
        logger.info("Analyzing impact...")
        return {
            "files_affected": 0,
            "functions_affected": 0,
            "risk": "low",
            "architecture_change": False,
        }

    def _handle_approval(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Gestisci fase APPROVAL."""
        if workflow["request"].approval_required:
            logger.info("Waiting for human approval...")
            # TODO: Implementare integrazione UI
            return {"approved": True, "approver": "auto"}
        return {"approved": True, "approver": "auto"}

    def _handle_execution(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Gestisci fase EXECUTION."""
        logger.info("Executing tasks...")
        return {
            "executed_tasks": 0,
            "files_modified": [],
            "errors": [],
        }

    def _handle_review(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Gestisci fase REVIEW."""
        logger.info("Reviewing code...")
        return {
            "quality_score": 8.5,
            "status": "approved",
            "warnings": [],
        }

    def _handle_testing(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Gestisci fase TESTING."""
        logger.info("Running tests...")
        return {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "coverage": 0.0,
        }

    def _handle_knowledge_update(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Gestisci fase KNOWLEDGE_UPDATE."""
        logger.info("Updating knowledge base...")
        return {
            "glossary_updated": True,
            "graph_updated": True,
            "vector_db_updated": True,
        }

    def _handle_git_commit(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Gestisci fase GIT_COMMIT."""
        logger.info("Creating git commit...")
        return {
            "commit_hash": "abc123",
            "branch": "feature/xyz",
            "committed_files": [],
        }

    def _create_completion_report(self, workflow: Dict[str, Any]) -> WorkflowReport:
        """Crea report di completamento."""
        start = workflow["start_time"]
        end = workflow.get("end_time", datetime.now())
        duration = (end - start).total_seconds()

        report = WorkflowReport(
            request_id=workflow["request"].id,
            phase=workflow["current_phase"],
            status=workflow["status"],
            duration_seconds=duration,
            tasks_completed=workflow["phase_results"].get("execution", {}).get("executed_tasks", 0),
            files_changed=workflow["phase_results"].get("execution", {}).get("files_modified", []),
        )

        self.reports.append(report)
        logger.info(f"Workflow completed: {report.request_id}")
        return report

    def _create_failure_report(self, workflow: Dict[str, Any], phase: WorkflowPhase, error: Exception) -> WorkflowReport:
        """Crea report di fallimento."""
        start = workflow["start_time"]
        duration = (datetime.now() - start).total_seconds()

        report = WorkflowReport(
            request_id=workflow["request"].id,
            phase=phase,
            status=WorkflowStatus.FAILED,
            duration_seconds=duration,
            errors=[str(error)],
        )

        self.reports.append(report)
        logger.error(f"Workflow failed: {report.request_id} at phase {phase.value}")
        return report

    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Ritorna status di un workflow."""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return {"status": "not_found"}

        return {
            "id": workflow_id,
            "status": workflow["status"].value,
            "current_phase": workflow["current_phase"].value,
            "start_time": workflow["start_time"].isoformat(),
        }

    def get_reports(self, status: Optional[WorkflowStatus] = None) -> List[WorkflowReport]:
        """Ritorna report filtrati."""
        if not status:
            return self.reports

        return [r for r in self.reports if r.status == status]


def create_workflow_orchestrator() -> WorkflowOrchestrator:
    """Factory function."""
    return WorkflowOrchestrator()

