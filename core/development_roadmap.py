"""
Development Roadmap and Phase Planning.

Defines the 10-phase development strategy for MVP.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class Phase(Enum):
    """Fasi di sviluppo."""
    PHASE_0 = "phase_0_environment"
    PHASE_1 = "phase_1_basic_agent"
    PHASE_2 = "phase_2_langgraph"
    PHASE_3 = "phase_3_project_memory"
    PHASE_4 = "phase_4_testing_loop"
    PHASE_5 = "phase_5_code_intelligence"
    PHASE_6 = "phase_6_dependency_graph"
    PHASE_7 = "phase_7_vector_db"
    PHASE_8 = "phase_8_git_integration"
    PHASE_9 = "phase_9_evaluation"
    PHASE_10 = "phase_10_advanced_autonomy"


class Priority(Enum):
    """Livelli di priorità."""
    CRITICAL = "critical"
    HIGHEST = "highest"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Component:
    """Componente di una fase."""
    name: str
    description: str
    complexity: str  # low, medium, high
    dependencies: List[str] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class PhaseDefinition:
    """Definizione di una fase."""
    phase: Phase
    title: str
    objective: str
    priority: Priority
    components: List[Component]
    estimated_days: int
    success_criteria: List[str]
    next_phase: Optional[Phase] = None


class RoadmapManager:
    """
    Gestore della roadmap di sviluppo.
    """

    def __init__(self):
        """Inizializza roadmap manager."""
        self.phases = self._build_phases()
        self.current_phase = Phase.PHASE_0

    def _build_phases(self) -> Dict[Phase, PhaseDefinition]:
        """Costruisce definizioni delle fasi."""
        return {
            Phase.PHASE_0: PhaseDefinition(
                phase=Phase.PHASE_0,
                title="Ambiente locale",
                objective="Preparare l'infrastruttura",
                priority=Priority.CRITICAL,
                components=[
                    Component("Python", "Runtime Python 3.11+", "low"),
                    Component("Ollama", "LLM runtime locale", "low"),
                    Component("LangChain", "Framework LLM", "low"),
                    Component("LangGraph", "Workflow orchestration", "low"),
                ],
                estimated_days=2,
                success_criteria=[
                    "Ollama server attivo",
                    "Modelli scaricati",
                    "Connessione LangChain funzionante",
                ],
                next_phase=Phase.PHASE_1
            ),
            Phase.PHASE_1: PhaseDefinition(
                phase=Phase.PHASE_1,
                title="Basic Coding Agent",
                objective="Creare primo agente che modifica codice",
                priority=Priority.HIGHEST,
                components=[
                    Component("Chat Interface", "Input utente", "low"),
                    Component("Coding Agent", "Generazione codice", "medium"),
                    Component("Filesystem Tools", "read, write, patch", "low"),
                ],
                estimated_days=5,
                success_criteria=[
                    "Agente legge e scrive file",
                    "Apply patch funziona",
                    "Primo test manuale superato",
                ],
                next_phase=Phase.PHASE_2
            ),
            Phase.PHASE_2: PhaseDefinition(
                phase=Phase.PHASE_2,
                title="Introduzione LangGraph",
                objective="Passare da chatbot a workflow",
                priority=Priority.HIGHEST,
                components=[
                    Component("Architect Agent", "Analisi requisiti", "medium"),
                    Component("Planner Agent", "Decomposizione task", "medium"),
                    Component("LangGraph Workflow", "Orchestrazione", "high"),
                ],
                estimated_days=7,
                success_criteria=[
                    "Architect genera plan",
                    "Planner crea task list",
                    "Workflow lineare funziona",
                ],
                next_phase=Phase.PHASE_3
            ),
            Phase.PHASE_3: PhaseDefinition(
                phase=Phase.PHASE_3,
                title="Project Memory .ai",
                objective="Rendere agente consapevole del progetto",
                priority=Priority.HIGHEST,
                components=[
                    Component("project.md", "Descrizione progetto", "low"),
                    Component("rules.md", "Convention di codice", "low"),
                    Component("architecture.md", "Decisioni tecniche", "low"),
                    Component("Memory Loader", "Caricamento memoria", "low"),
                ],
                estimated_days=3,
                success_criteria=[
                    "Agente legge .ai/ al startup",
                    "Rules applicate",
                    "Context injected in prompt",
                ],
                next_phase=Phase.PHASE_4
            ),
            Phase.PHASE_4: PhaseDefinition(
                phase=Phase.PHASE_4,
                title="Testing Loop",
                objective="Creare autonomia controllata",
                priority=Priority.HIGHEST,
                components=[
                    Component("Tester Agent", "Esecuzione test", "medium"),
                    Component("Error Analyzer", "Analisi fallimenti", "medium"),
                    Component("Fix Loop", "Retry automatico", "medium"),
                ],
                estimated_days=5,
                success_criteria=[
                    "Test eseguiti automaticamente",
                    "Errori analizzati",
                    "Retry loop funzionante",
                    "MAX_RETRY = 5 rispettato",
                ],
                next_phase=Phase.PHASE_5
            ),
            Phase.PHASE_5: PhaseDefinition(
                phase=Phase.PHASE_5,
                title="Code Intelligence",
                objective="Permettere analisi su grandi repository",
                priority=Priority.HIGH,
                components=[
                    Component("Tree-sitter", "AST parsing", "high"),
                    Component("Entity Extraction", "Estrazione funzioni/classi", "medium"),
                    Component("Knowledge Base", "Immagazzinamento metadati", "low"),
                ],
                estimated_days=7,
                success_criteria=[
                    "AST parsing funzionante",
                    "Funzioni estratte",
                    "functions.json generato",
                ],
                next_phase=Phase.PHASE_6
            ),
            Phase.PHASE_6: PhaseDefinition(
                phase=Phase.PHASE_6,
                title="Dependency Graph",
                objective="Capire l'impatto delle modifiche",
                priority=Priority.HIGH,
                components=[
                    Component("Graph Builder", "Costruzione grafo", "high"),
                    Component("Impact Analysis", "Calcolo impatto", "medium"),
                    Component("Risk Assessment", "Valutazione rischio", "medium"),
                ],
                estimated_days=5,
                success_criteria=[
                    "Grafo delle dipendenze costruito",
                    "Impact analysis funzionante",
                    "Risk level calcolato",
                ],
                next_phase=Phase.PHASE_7
            ),
            Phase.PHASE_7: PhaseDefinition(
                phase=Phase.PHASE_7,
                title="Vector Database",
                objective="Migliorare retrieval semantico",
                priority=Priority.MEDIUM,
                components=[
                    Component("Vector Store", "Storage embeddings", "medium"),
                    Component("Chunking", "Divisione intelligente", "medium"),
                    Component("Semantic Search", "Ricerca semantica", "medium"),
                ],
                estimated_days=5,
                success_criteria=[
                    "Codice indicizzato",
                    "Ricerca semantica funzionante",
                    "Context retrieval migliorato",
                ],
                next_phase=Phase.PHASE_8
            ),
            Phase.PHASE_8: PhaseDefinition(
                phase=Phase.PHASE_8,
                title="Git Integration",
                objective="Gestire modifiche professionalmente",
                priority=Priority.MEDIUM,
                components=[
                    Component("Branch Management", "Creazione branch", "low"),
                    Component("Commit Generation", "Creazione commit", "low"),
                    Component("PR Workflow", "Pull request automation", "medium"),
                ],
                estimated_days=4,
                success_criteria=[
                    "Branch creati automaticamente",
                    "Commit message formattati",
                    "PR generate automaticamente",
                ],
                next_phase=Phase.PHASE_9
            ),
            Phase.PHASE_9: PhaseDefinition(
                phase=Phase.PHASE_9,
                title="LangSmith Evaluation",
                objective="Misurare qualità",
                priority=Priority.MEDIUM,
                components=[
                    Component("Metrics Tracking", "Tracciamento metriche", "low"),
                    Component("Evaluators", "Valutatori automatici", "medium"),
                    Component("Dashboard", "Visualizzazione metriche", "medium"),
                ],
                estimated_days=4,
                success_criteria=[
                    "Metriche tracciate",
                    "Success rate misurato",
                    "Dashboard funzionante",
                ],
                next_phase=Phase.PHASE_10
            ),
            Phase.PHASE_10: PhaseDefinition(
                phase=Phase.PHASE_10,
                title="Advanced Autonomy",
                objective="Avvicinarsi al livello software engineer",
                priority=Priority.LOW,
                components=[
                    Component("Multi-Model Routing", "Routing intelligente modelli", "high"),
                    Component("Self-Improvement", "Apprendimento automatico", "high"),
                    Component("Advanced Memory", "Memoria architetturale", "medium"),
                ],
                estimated_days=10,
                success_criteria=[
                    "Modelli routing funzionante",
                    "Self-improvement attivo",
                    "Agent ricorda decisioni",
                ],
                next_phase=None
            ),
        }

    def get_phase(self, phase: Phase) -> Optional[PhaseDefinition]:
        """Ritorna definizione fase."""
        return self.phases.get(phase)

    def get_all_phases(self) -> List[PhaseDefinition]:
        """Ritorna tutte le fasi in ordine."""
        return [
            self.phases[p] for p in [
                Phase.PHASE_0, Phase.PHASE_1, Phase.PHASE_2, Phase.PHASE_3,
                Phase.PHASE_4, Phase.PHASE_5, Phase.PHASE_6, Phase.PHASE_7,
                Phase.PHASE_8, Phase.PHASE_9, Phase.PHASE_10,
            ]
        ]

    def get_priority_ranking(self) -> List[tuple]:
        """Ritorna fasi ordinate per priorità."""
        ranking = {
            Priority.CRITICAL: 5,
            Priority.HIGHEST: 4,
            Priority.HIGH: 3,
            Priority.MEDIUM: 2,
            Priority.LOW: 1,
        }

        phases = [(p, ranking[p.priority]) for p in self.get_all_phases()]
        phases.sort(key=lambda x: x[1], reverse=True)
        return phases

    def get_estimated_total_days(self) -> int:
        """Ritorna giorni totali stimati."""
        return sum(p.estimated_days for p in self.get_all_phases())

    def print_roadmap_summary(self):
        """Stampa sommario roadmap."""
        total_days = self.get_estimated_total_days()
        total_weeks = total_days / 5
        
        print("\n" + "="*70)
        print("AI SOFTWARE ENGINEER AGENT - DEVELOPMENT ROADMAP")
        print("="*70)
        print(f"Total Estimated Time: {total_days} days (~{total_weeks:.1f} weeks)\n")
        
        for phase_def in self.get_all_phases():
            print(f"\n{phase_def.phase.value.upper()}")
            print(f"  Title: {phase_def.title}")
            print(f"  Priority: {phase_def.priority.value}")
            print(f"  Estimated: {phase_def.estimated_days} days")
            print(f"  Components: {len(phase_def.components)}")
        
        print("\n" + "="*70 + "\n")


def create_roadmap_manager() -> RoadmapManager:
    """Factory function."""
    return RoadmapManager()

