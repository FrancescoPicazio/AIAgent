"""
AI Model Layer - Model routing, selection, and prompt architecture.

Orchestrates LLM selection based on task type and manages prompts.
"""

import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Tipi di modelli disponibili."""
    ROUTING = "routing"
    CODING = "coding"
    REASONING = "reasoning"
    REVIEW = "review"


class TaskType(Enum):
    """Tipi di task che richiedono modelli diversi."""
    ORCHESTRATION = "orchestration"  # Routing, task management
    ARCHITECTURE = "architecture"  # Planning, design decisions
    IMPLEMENTATION = "implementation"  # Code generation
    REVIEW = "review"  # Code review
    TESTING = "testing"  # Test analysis


@dataclass
class ModelConfig:
    """Configurazione di un modello."""
    name: str
    model_type: ModelType
    ollama_name: str
    vram_required_gb: float
    context_window: int
    temperature: float = 0.3
    max_tokens: int = 2048
    fallback_model: Optional[str] = None
    description: str = ""


@dataclass
class PromptTemplate:
    """Template di un prompt."""
    name: str
    role: str
    task_description: str
    rules: List[str]
    output_format: str
    temperature_override: Optional[float] = None


class ModelRegistry:
    """
    Registro dei modelli disponibili.
    
    Gestisce configurazione, disponibilità, e fallback.
    """

    def __init__(self):
        """Inizializza registry."""
        self.models: Dict[str, ModelConfig] = {}
        self._register_default_models()

    def register_model(self, config: ModelConfig):
        """Registra un modello."""
        self.models[config.name] = config
        logger.info(f"Registered model: {config.name} ({config.ollama_name})")

    def get_model(self, model_name: str) -> Optional[ModelConfig]:
        """Ritorna configurazione modello."""
        return self.models.get(model_name)

    def get_models_by_type(self, model_type: ModelType) -> List[ModelConfig]:
        """Ritorna modelli di un tipo specifico."""
        return [m for m in self.models.values() if m.model_type == model_type]

    def can_fit_in_vram(self, vram_gb: float) -> List[ModelConfig]:
        """Ritorna modelli che stanno in memoria."""
        return [m for m in self.models.values() if m.vram_required_gb <= vram_gb]

    def get_with_fallback(self, model_name: str) -> Optional[ModelConfig]:
        """Ritorna modello con fallback."""
        model = self.get_model(model_name)
        if not model:
            return None
        if model.fallback_model:
            return self.get_model(model.fallback_model)
        return model

    def _register_default_models(self):
        """Registra modelli di default."""
        # Orchestrazione
        self.register_model(ModelConfig(
            name="qwen-4b",
            model_type=ModelType.ROUTING,
            ollama_name="qwen2:4b",
            vram_required_gb=4.0,
            context_window=4096,
            temperature=0.2,
            description="Lightweight orchestrator for routing and planning"
        ))

        # Coding
        self.register_model(ModelConfig(
            name="qwen-coder-14b",
            model_type=ModelType.CODING,
            ollama_name="qwen2-coder:14b",
            vram_required_gb=10.0,
            context_window=8192,
            temperature=0.1,
            fallback_model="qwen-coder-7b",
            description="Code generation and modification"
        ))

        self.register_model(ModelConfig(
            name="qwen-coder-7b",
            model_type=ModelType.CODING,
            ollama_name="qwen2-coder:7b",
            vram_required_gb=6.0,
            context_window=4096,
            temperature=0.1,
            description="Lightweight code model (fallback)"
        ))

        # Reasoning
        self.register_model(ModelConfig(
            name="gemma-reasoning",
            model_type=ModelType.REASONING,
            ollama_name="gemma:latest",
            vram_required_gb=8.0,
            context_window=8192,
            temperature=0.3,
            description="Architectural decisions and complex analysis"
        ))

        # Review
        self.register_model(ModelConfig(
            name="qwen-review",
            model_type=ModelType.REVIEW,
            ollama_name="qwen2:4b",
            vram_required_gb=4.0,
            context_window=4096,
            temperature=0.2,
            description="Code review and quality analysis"
        ))


class ModelRouter:
    """
    Router che seleziona il modello appropriato per ogni task.
    """

    def __init__(self, registry: ModelRegistry, available_vram_gb: float = 16.0):
        """
        Inizializza router.
        
        Args:
            registry: ModelRegistry
            available_vram_gb: VRAM disponibile in GB
        """
        self.registry = registry
        self.available_vram_gb = available_vram_gb
        self.routing_table = self._build_routing_table()

    def select_model(self, task_type: TaskType, agent_name: str) -> Optional[ModelConfig]:
        """
        Seleziona il modello appropriato.
        
        Args:
            task_type: Tipo di task
            agent_name: Nome dell'agente che esegue il task
            
        Returns:
            Configurazione modello selezionato
        """
        # Lookup routing table
        key = (task_type, agent_name)
        model_type = self.routing_table.get(key)

        if not model_type:
            logger.warning(f"No routing for {key}")
            return None

        # Get models di quel tipo
        candidates = self.registry.get_models_by_type(model_type)

        # Filter per VRAM disponibile
        candidates = [m for m in candidates if m.vram_required_gb <= self.available_vram_gb]

        if not candidates:
            logger.warning(f"No models fit in available VRAM ({self.available_vram_gb}GB)")
            return None

        # Seleziona il primo (dovrebbe essere il più capace)
        model = candidates[0]

        # Usa fallback se necessario
        if not model:
            model = self.registry.get_with_fallback(model.name)

        return model

    def _build_routing_table(self) -> Dict[tuple, ModelType]:
        """Costruisce tabella di routing."""
        return {
            # Orchestration tasks
            (TaskType.ORCHESTRATION, "planner"): ModelType.ROUTING,
            (TaskType.ORCHESTRATION, "memory_updater"): ModelType.ROUTING,
            (TaskType.ORCHESTRATION, "task_manager"): ModelType.ROUTING,

            # Architecture tasks
            (TaskType.ARCHITECTURE, "architect"): ModelType.REASONING,

            # Implementation tasks
            (TaskType.IMPLEMENTATION, "coder"): ModelType.CODING,

            # Review tasks
            (TaskType.REVIEW, "reviewer"): ModelType.REVIEW,

            # Testing tasks
            (TaskType.TESTING, "tester"): ModelType.REVIEW,
        }


class PromptManager:
    """
    Gestione centralizzata dei prompt.
    """

    def __init__(self):
        """Inizializza prompt manager."""
        self.prompts: Dict[str, PromptTemplate] = {}
        self._register_default_prompts()

    def register_prompt(self, prompt: PromptTemplate):
        """Registra un template di prompt."""
        self.prompts[prompt.name] = prompt
        logger.info(f"Registered prompt: {prompt.name}")

    def get_prompt(self, prompt_name: str) -> Optional[PromptTemplate]:
        """Ritorna template di prompt."""
        return self.prompts.get(prompt_name)

    def render_prompt(
        self,
        prompt_name: str,
        context: Dict[str, Any],
        task: str
    ) -> str:
        """
        Renderizza un prompt con contesto.
        
        Args:
            prompt_name: Nome del template
            context: Variabili di contesto
            task: Descrizione del task
            
        Returns:
            Prompt renderizzato
        """
        prompt = self.get_prompt(prompt_name)
        if not prompt:
            return f"Task: {task}"

        # Build prompt
        lines = [
            f"# {prompt.role}",
            "",
            prompt.task_description,
            "",
            "## Rules",
        ]

        for rule in prompt.rules:
            lines.append(f"- {rule}")

        lines.extend([
            "",
            "## Task",
            task,
            "",
            "## Output Format",
            prompt.output_format,
        ])

        return "\n".join(lines)

    def _register_default_prompts(self):
        """Registra prompt di default."""
        self.register_prompt(PromptTemplate(
            name="architect",
            role="Software Architect",
            task_description="Analizza il requisito e proponi una soluzione architetturale.",
            rules=[
                "Non scrivere codice",
                "Analizza l'architettura esistente",
                "Valuta trade-off",
                "Identifica rischi",
                "Proponi alternative"
            ],
            output_format="""
{
  "approach": "...",
  "affected_components": [...],
  "pattern": "...",
  "risk": "low/medium/high",
  "rationale": "..."
}
            """,
            temperature_override=0.3
        ))

        self.register_prompt(PromptTemplate(
            name="planner",
            role="Technical Planner",
            task_description="Dividi il requisito in task atomici ordinati.",
            rules=[
                "Crea task indipendenti quando possibile",
                "Specifica dipendenze",
                "Valuta il rischio di ogni task",
                "Stima complessità",
                "Fornisci criteri di completamento"
            ],
            output_format="""
{
  "tasks": [
    {
      "id": 1,
      "title": "...",
      "files": [...],
      "dependencies": [...],
      "risk": "low/medium/high"
    }
  ]
}
            """,
            temperature_override=0.2
        ))

        self.register_prompt(PromptTemplate(
            name="coder",
            role="Senior Developer",
            task_description="Implementa il task assegnato modificando il codice.",
            rules=[
                "Rispetta rules.md del progetto",
                "Analizza il codice esistente prima di modificare",
                "Usa patch atomiche",
                "Aggiungi test",
                "Mantieni coerenza stilistica"
            ],
            output_format="""
{
  "files": [...],
  "changes": [...],
  "patch": "...",
  "testing": "..."
}
            """,
            temperature_override=0.1
        ))

        self.register_prompt(PromptTemplate(
            name="reviewer",
            role="Code Reviewer",
            task_description="Rivedi la qualità e correttezza del codice.",
            rules=[
                "Valuta qualità",
                "Verifica sicurezza",
                "Controlla manutenibilità",
                "Valuta conformità all'architettura",
                "Suggerisci miglioramenti"
            ],
            output_format="""
{
  "quality_score": 0.0-10.0,
  "issues": [...],
  "suggestions": [...],
  "status": "ok/needs_fix/critical"
}
            """,
            temperature_override=0.2
        ))

        self.register_prompt(PromptTemplate(
            name="tester",
            role="Test Analyzer",
            task_description="Analizza errori di test e proponi correzioni.",
            rules=[
                "Identifica la causa principale",
                "Non modificare codice direttamente",
                "Proponi correzione al coder",
                "Valuta impatto della correzione"
            ],
            output_format="""
{
  "error": "...",
  "root_cause": "...",
  "affected_code": [...],
  "suggested_fix": "..."
}
            """,
            temperature_override=0.2
        ))


class ModelOrchestrator:
    """
    Orchestratore principale per modelli.
    
    Coordina registry, router, e prompt manager.
    """

    def __init__(self, available_vram_gb: float = 16.0):
        """Inizializza orchestratore."""
        self.registry = ModelRegistry()
        self.router = ModelRouter(self.registry, available_vram_gb)
        self.prompts = PromptManager()
        self.call_count = 0
        self.token_count = 0

    def get_model_for_task(self, task_type: TaskType, agent_name: str) -> Optional[ModelConfig]:
        """Seleziona modello per task."""
        return self.router.select_model(task_type, agent_name)

    def get_prompt_for_agent(self, agent_name: str) -> Optional[PromptTemplate]:
        """Ritorna prompt template per agente."""
        return self.prompts.get_prompt(agent_name)

    def render_system_prompt(
        self,
        agent_name: str,
        context: Dict[str, Any],
        task: str
    ) -> str:
        """Renderizza system prompt completo."""
        return self.prompts.render_prompt(agent_name, context, task)

    def record_call(self, tokens_used: int):
        """Registra una chiamata LLM."""
        self.call_count += 1
        self.token_count += tokens_used
        logger.info(f"LLM Call #{self.call_count}, Total tokens: {self.token_count}")

    def get_stats(self) -> Dict[str, Any]:
        """Ritorna statistiche utilizzo."""
        return {
            "calls": self.call_count,
            "total_tokens": self.token_count,
            "avg_tokens_per_call": self.token_count / max(1, self.call_count),
            "available_vram_gb": self.router.available_vram_gb
        }


def create_model_orchestrator(vram_gb: float = 16.0) -> ModelOrchestrator:
    """Factory function."""
    return ModelOrchestrator(vram_gb)

