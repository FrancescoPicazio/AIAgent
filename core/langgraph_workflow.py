"""
LangGraph Workflow Integration for MVP v1.

Complete end-to-end workflow orchestration connecting:
- Agents (Planner, Coder, Tester)
- Tools (FileSystem, Terminal, Git)
- Models (ModelOrchestrator)
- State management
"""

import logging
from typing import Dict, Any
from core.agent_state import AgentState, create_agent_state
from core.agents import AgentFactory
from core.tools import ToolsFactory
from core.llm_models import create_model_orchestrator, TaskType
from core.workflow_orchestrator import WorkflowOrchestrator

logger = logging.getLogger(__name__)


class LangGraphWorkflow:
    """
    Complete LangGraph workflow orchestration.
    
    Connects all subsystems into a functional development agent.
    """

    def __init__(self, project_root: str = "."):
        """
        Initialize LangGraph workflow.
        
        Args:
            project_root: Root directory for project operations
        """
        self.project_root = project_root
        
        # Initialize components
        self.agents = AgentFactory.create_all_agents()
        self.tools = ToolsFactory.create_all_tools(project_root)
        self.model_orchestrator = create_model_orchestrator()
        self.workflow_orchestrator = WorkflowOrchestrator()
        
        logger.info("LangGraph workflow initialized")

    def plan_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Planning node - decompose user request into tasks.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with plan
        """
        logger.info("→ PLAN NODE")
        
        # Get model for planning
        model = self.model_orchestrator.get_model_for_task(
            TaskType.ORCHESTRATION,
            "planner"
        )
        logger.info(f"  Using model: {model.name if model else 'default'}")
        
        # Run planner agent
        planner = self.agents["planner"]
        result_state = planner.run(state)
        
        logger.info(f"  Generated {len(result_state.get('plan', {}).get('tasks', []))} tasks")
        return result_state

    def code_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coding node - implement code changes.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with code changes
        """
        logger.info("→ CODE NODE")
        
        # Get model for coding
        model = self.model_orchestrator.get_model_for_task(
            TaskType.IMPLEMENTATION,
            "coder"
        )
        logger.info(f"  Using model: {model.name if model else 'default'}")
        
        # Get first task from plan
        plan = state.get("plan", {})
        tasks = plan.get("tasks", [])
        
        if not tasks:
            logger.warning("  No tasks in plan")
            return state
        
        # Set current task
        state["current_task"] = tasks[0]
        
        # Run coder agent
        coder = self.agents["coder"]
        result_state = coder.run(state)
        
        logger.info(f"  Modified {len(result_state.get('code_changes', {}).get('files_modified', []))} files")
        return result_state

    def test_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Testing node - validate code changes.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with test results
        """
        logger.info("→ TEST NODE")
        
        # Get model for testing
        model = self.model_orchestrator.get_model_for_task(
            TaskType.TESTING,
            "tester"
        )
        logger.info(f"  Using model: {model.name if model else 'default'}")
        
        # Run tester agent
        tester = self.agents["tester"]
        result_state = tester.run(state)
        
        test_status = result_state.get("test_status", "unknown")
        logger.info(f"  Test status: {test_status}")
        return result_state

    def router_node(self, state: Dict[str, Any]) -> str:
        """
        Router node - decide next step based on test results.
        
        Args:
            state: Current workflow state
            
        Returns:
            Next node name
        """
        logger.info("→ ROUTER NODE")
        
        test_status = state.get("test_status", "unknown")
        retry_count = state.get("retry_count", 0)
        max_retries = state.get("retry_count_max", 3)
        
        if test_status == "passed":
            logger.info("  ✅ Tests passed → END")
            return "end"
        elif retry_count >= max_retries:
            logger.info(f"  ❌ Max retries ({max_retries}) reached → END")
            return "end"
        else:
            retry_count += 1
            state["retry_count"] = retry_count
            logger.info(f"  🔄 Tests failed, retry {retry_count}/{max_retries} → CODE")
            return "code"

    def build_graph(self):
        """
        Build the LangGraph workflow graph.
        
        Returns:
            Compiled graph ready for execution
        """
        logger.info("Building LangGraph workflow...")
        
        # Note: This is a simplified version without actual LangGraph
        # In production, this would use:
        # from langgraph.graph import StateGraph
        
        # Graph structure:
        # START → plan → code → test → router → {end, code}
        
        graph_structure = {
            "nodes": {
                "plan": self.plan_node,
                "code": self.code_node,
                "test": self.test_node,
                "router": self.router_node,
            },
            "edges": [
                ("plan", "code"),
                ("code", "test"),
                ("test", "router"),
                ("router", "end", lambda s: s == "end"),
                ("router", "code", lambda s: s == "code"),
            ],
            "entry_point": "plan",
        }
        
        logger.info(f"Graph built with {len(graph_structure['nodes'])} nodes")
        return graph_structure

    def execute(self, user_request: str) -> Dict[str, Any]:
        """
        Execute the complete workflow for a user request.
        
        Args:
            user_request: User's natural language request
            
        Returns:
            Final state after workflow execution
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"EXECUTING WORKFLOW: {user_request}")
        logger.info(f"{'='*70}\n")
        
        # Initialize state
        state = {
            "user_request": user_request,
            "plan": {},
            "current_task": None,
            "code_changes": {},
            "test_results": {},
            "test_status": "unknown",
            "retry_count": 0,
            "retry_count_max": 3,
        }
        
        # Execute nodes in sequence
        logger.info("Starting workflow execution...\n")
        
        # Plan phase
        state = self.plan_node(state)
        
        # Coding + Testing loop
        max_iterations = 10
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            logger.info(f"\n--- Iteration {iteration} ---\n")
            
            # Code phase
            state = self.code_node(state)
            
            # Test phase
            state = self.test_node(state)
            
            # Route decision
            next_node = self.router_node(state)
            
            if next_node == "end":
                logger.info(f"\n{'='*70}")
                logger.info("WORKFLOW COMPLETED")
                logger.info(f"{'='*70}\n")
                break
        
        return state

    def print_workflow_summary(self):
        """Print workflow structure summary."""
        print("\n" + "="*70)
        print("LANGGRAPH WORKFLOW STRUCTURE - MVP v1")
        print("="*70)
        print("\nNodes:")
        print("  1. PLAN      - PlannerAgent decomposes request into tasks")
        print("  2. CODE      - CoderAgent implements code changes")
        print("  3. TEST      - TesterAgent validates with test execution")
        print("  4. ROUTER    - Decides: end or retry code")
        print("\nEdges:")
        print("  PLAN → CODE → TEST → ROUTER")
        print("                        ├→ END (tests passed)")
        print("                        └→ CODE (tests failed + retries < max)")
        print("\nAgents:")
        for agent_name, agent in self.agents.items():
            print(f"  • {agent_name}: {agent.__class__.__name__}")
        print("\nTools:")
        for tool_name in self.tools.keys():
            print(f"  • {tool_name}")
        print("\nModels:")
        for model_name in self.model_orchestrator.registry.models.keys():
            print(f"  • {model_name}")
        print("\n" + "="*70 + "\n")


def create_langgraph_workflow(project_root: str = ".") -> LangGraphWorkflow:
    """Factory function for creating workflow."""
    return LangGraphWorkflow(project_root)

