"""
Multi-Agent System State and Definitions for LangGraph.

Defines the shared state, agent roles, and workflow orchestration.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class ApprovalStatus(Enum):
    """Stato di approvazione per task critici."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"


class ReviewStatus(Enum):
    """Stato della revisione di codice."""
    OK = "ok"
    NEEDS_FIX = "needs_fix"
    CRITICAL_ISSUE = "critical_issue"


class TestStatus(Enum):
    """Stato dei test."""
    PASSED = "passed"
    FAILED = "failed"
    PARTIAL = "partial"


@dataclass
class ArchitectureDecision:
    """Decisione architetturale."""
    approach: str
    affected_components: List[str]
    pattern: str
    risk: str  # low, medium, high
    rationale: str = ""
    dependencies: List[str] = field(default_factory=list)


@dataclass
class Task:
    """Un task atomico da eseguire."""
    id: int
    title: str
    description: str = ""
    files: List[str] = field(default_factory=list)
    dependencies: List[int] = field(default_factory=list)
    risk: str = "low"
    status: str = "pending"  # pending, in_progress, completed, failed
    output: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CodeChange:
    """Modifica al codice proposta da un agente."""
    file: str
    original_content: str
    new_content: str
    diff: str
    description: str = ""
    imports_added: List[str] = field(default_factory=list)
    imports_removed: List[str] = field(default_factory=list)


@dataclass
class ReviewComment:
    """Commento da reviewer."""
    file: str
    line: int
    message: str
    severity: str  # info, warning, error
    suggestion: str = ""


@dataclass
class TestResult:
    """Risultato esecuzione test."""
    status: str  # passed, failed, partial
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    coverage: float = 0.0
    errors: List[Dict[str, Any]] = field(default_factory=list)
    duration_seconds: float = 0.0


class AgentState(Dict[str, Any]):
    """
    Stato condiviso tra tutti gli agenti nel workflow LangGraph.
    
    Questo dizionario viene passato da un nodo all'altro e accumulato
    durante il ciclo di sviluppo.
    """

    def __init__(self):
        super().__init__()
        # Metadati richiesta
        self["user_request"] = ""
        self["user_request_raw"] = ""
        self["request_timestamp"] = ""
        self["task_id"] = None

        # Contesto progetto
        self["project_context"] = {}
        self["project_structure"] = {}
        self["retrieved_code_context"] = []

        # Decisioni architetturali
        self["architecture_decision"] = None
        self["approach"] = ""
        self["affected_components"] = []
        self["risk_assessment"] = "low"

        # Planning
        self["task_list"] = []  # List[Task]
        self["current_task"] = None  # Task
        self["task_index"] = 0
        self["impact_report"] = {}

        # Approval
        self["approval_status"] = ApprovalStatus.PENDING.value
        self["human_feedback"] = ""
        self["approval_timestamp"] = None

        # Implementation
        self["code_changes"] = []  # List[CodeChange]
        self["files_modified"] = []
        self["coding_attempts"] = 0
        self["max_coding_attempts"] = 3

        # Review
        self["review_results"] = {}
        self["review_status"] = ReviewStatus.OK.value
        self["review_comments"] = []  # List[ReviewComment]
        self["quality_score"] = 0.0

        # Testing
        self["test_results"] = None  # TestResult
        self["test_status"] = TestStatus.PASSED.value
        self["test_attempts"] = 0
        self["max_test_attempts"] = 3

        # Correzione
        self["correction_loop_count"] = 0
        self["max_correction_loops"] = 5
        self["should_retry"] = False

        # Memoria
        self["memory_updates"] = {}
        self["glossary_updates"] = []
        self["architecture_updates"] = []
        self["adrs_created"] = []

        # Output finale
        self["status"] = "in_progress"  # in_progress, completed, failed
        self["final_output"] = ""
        self["error_message"] = ""
        self["completion_timestamp"] = None

        # Metriche
        self["metrics"] = {
            "total_duration_seconds": 0.0,
            "agent_durations": {},
            "tokens_used": 0,
            "llm_calls": 0,
        }

    def update_from_dict(self, data: Dict[str, Any]):
        """Aggiorna lo stato da un dizionario."""
        self.update(data)

    def get_current_task(self) -> Optional[Task]:
        """Ritorna il task corrente."""
        return self.get("current_task")

    def get_task_list(self) -> List[Task]:
        """Ritorna la lista di task."""
        return self.get("task_list", [])

    def is_approved(self) -> bool:
        """Verifica se è stata data approvazione."""
        return self["approval_status"] == ApprovalStatus.APPROVED.value

    def is_rejected(self) -> bool:
        """Verifica se è stata rifiutata."""
        return self["approval_status"] == ApprovalStatus.REJECTED.value

    def needs_revision(self) -> bool:
        """Verifica se serve revisione."""
        return self["approval_status"] == ApprovalStatus.NEEDS_REVISION.value

    def review_passed(self) -> bool:
        """Verifica se la revisione è passata."""
        return self["review_status"] == ReviewStatus.OK.value

    def tests_passed(self) -> bool:
        """Verifica se i test sono passati."""
        return self["test_status"] == TestStatus.PASSED.value

    def is_completed(self) -> bool:
        """Verifica se il workflow è completato."""
        return self["status"] == "completed"

    def is_failed(self) -> bool:
        """Verifica se il workflow è fallito."""
        return self["status"] == "failed"

    def increment_correction_loop(self):
        """Incrementa il contatore dei loop di correzione."""
        self["correction_loop_count"] += 1

    def can_retry_correction(self) -> bool:
        """Verifica se si può rientrare nel loop di correzione."""
        return self["correction_loop_count"] < self["max_correction_loops"]

    def set_failed(self, error: str):
        """Marca il workflow come fallito."""
        self["status"] = "failed"
        self["error_message"] = error

    def set_completed(self, output: str):
        """Marca il workflow come completato."""
        self["status"] = "completed"
        self["final_output"] = output


# Definizioni dei nodi del grafo
class AgentRole(Enum):
    """Ruoli degli agenti nel sistema."""
    ARCHITECT = "architect"
    PLANNER = "planner"
    CODER = "coder"
    REVIEWER = "reviewer"
    TESTER = "tester"
    MEMORY_UPDATER = "memory_updater"
    ORCHESTRATOR = "orchestrator"


class NodeType(Enum):
    """Tipi di nodi nel grafo LangGraph."""
    AGENT = "agent"
    ROUTER = "router"
    APPROVAL = "approval"
    DECISION = "decision"
    END = "end"


@dataclass
class NodeDefinition:
    """Definizione di un nodo nel grafo LangGraph."""
    name: str
    role: Optional[AgentRole]
    node_type: NodeType
    description: str = ""
    model: str = ""  # Quale LLM usare
    max_retries: int = 0
    timeout_seconds: int = 60


# Definizioni nodi principali
AGENT_NODES = [
    NodeDefinition(
        name="architect",
        role=AgentRole.ARCHITECT,
        node_type=NodeType.AGENT,
        description="Analizza requisiti e propone soluzione architettuale",
        model="qwen2:4b",
        max_retries=2,
    ),
    NodeDefinition(
        name="planner",
        role=AgentRole.PLANNER,
        node_type=NodeType.AGENT,
        description="Scompone soluzione in task eseguibili",
        model="qwen2:4b",
        max_retries=2,
    ),
    NodeDefinition(
        name="coder",
        role=AgentRole.CODER,
        node_type=NodeType.AGENT,
        description="Implementa il task assegnato",
        model="qwen2:coder",
        max_retries=3,
    ),
    NodeDefinition(
        name="reviewer",
        role=AgentRole.REVIEWER,
        node_type=NodeType.AGENT,
        description="Revisiona qualità e conformità del codice",
        model="qwen2:4b",
        max_retries=2,
    ),
    NodeDefinition(
        name="tester",
        role=AgentRole.TESTER,
        node_type=NodeType.AGENT,
        description="Esegue test e validazione",
        model="qwen2:4b",
        max_retries=3,
    ),
    NodeDefinition(
        name="memory_updater",
        role=AgentRole.MEMORY_UPDATER,
        node_type=NodeType.AGENT,
        description="Aggiorna memoria del progetto (.ai/)",
        model="qwen2:4b",
        max_retries=1,
    ),
]

# Router e decisioni
ROUTER_NODES = [
    NodeDefinition(
        name="approval_gate",
        role=None,
        node_type=NodeType.APPROVAL,
        description="Gate per approvazione umana su modifiche critiche",
    ),
    NodeDefinition(
        name="correction_decision",
        role=None,
        node_type=NodeType.DECISION,
        description="Decide se riprovare correzione o fallire",
    ),
    NodeDefinition(
        name="completion_check",
        role=None,
        node_type=NodeType.DECISION,
        description="Verifica se workflow è completato",
    ),
]


# Configurazione routing dinamico
ROUTER_RULES = {
    "architect": ["planner"],
    "planner": ["approval_gate"],
    "approval_gate": {
        "approved": ["coder"],
        "rejected": ["end"],
        "needs_revision": ["architect"],
    },
    "coder": ["reviewer"],
    "reviewer": {
        "ok": ["tester"],
        "needs_fix": ["coder"],
        "critical_issue": ["end"],
    },
    "tester": {
        "passed": ["memory_updater"],
        "failed": ["correction_decision"],
        "partial": ["correction_decision"],
    },
    "correction_decision": {
        "retry": ["coder"],
        "fail": ["end"],
    },
    "memory_updater": ["completion_check"],
    "completion_check": ["end"],
}


def create_agent_state() -> AgentState:
    """Factory function per creare un nuovo stato."""
    return AgentState()

