"""
LangGraph Integration for Parallel Agents Execution.

Extends the LangGraph workflow to support parallel agent execution
with proper synchronization and conflict resolution.
"""

import logging
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor
from core.parallel_agent_pool import ParallelAgentPool, ParallelTask, TaskPriority
from core.synchronization import (
    LockManager,
    StateVersionManager,
    create_lock_manager,
    create_state_version_manager,
)
from core.conflict_resolver import (
    ConflictDetector,
    ConflictResolver,
    create_conflict_detector,
    create_conflict_resolver,
)
from core.parallel_scheduler import ParallelScheduler, create_parallel_scheduler

logger = logging.getLogger(__name__)


class ParallelWorkflowOrchestrator:
    """
    Orchestrates parallel execution of agents in a LangGraph workflow.
    
    Manages:
    - Task scheduling and execution groups
    - Agent pool management
    - State synchronization across parallel branches
    - Conflict detection and resolution
    - Lock management for shared resources
    """
    
    def __init__(
        self,
        max_parallel_agents: int = 4,
        agent_ids: Optional[List[str]] = None,
    ):
        """
        Initialize parallel workflow orchestrator.
        
        Args:
            max_parallel_agents: Maximum agents running in parallel
            agent_ids: List of agent IDs in system
        """
        self.max_parallel_agents = max_parallel_agents
        self.agent_ids = agent_ids or [
            "planner", "coder", "tester", "reviewer", "security_analyzer"
        ]
        
        # Initialize subsystems
        self.agent_pool = ParallelAgentPool(max_parallel_agents)
        self.lock_manager = create_lock_manager()
        self.state_version_manager = create_state_version_manager(self.agent_ids)
        self.conflict_detector = create_conflict_detector()
        self.conflict_resolver = create_conflict_resolver()
        self.scheduler = create_parallel_scheduler()
        
        logger.info(
            f"ParallelWorkflowOrchestrator initialized "
            f"with {max_parallel_agents} parallel workers"
        )
    
    def plan_parallel_execution(
        self,
        state: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Analyze task list and plan parallel execution groups.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with execution plan
        """
        logger.info("Planning parallel execution...")
        
        # Extract task list from state
        task_list = state.get("task_list", [])
        
        if not task_list:
            logger.warning("No tasks to parallelize")
            state["parallel_plan"] = {"groups": []}
            return state
        
        # Build task dependency graph
        tasks = {}
        dependencies = []
        
        for i, task in enumerate(task_list):
            task_id = f"task_{i}"
            tasks[task_id] = {
                "name": task.title if hasattr(task, 'title') else str(task),
                "index": i,
            }
            
            # Check dependencies
            if hasattr(task, 'dependencies'):
                for dep_idx in task.dependencies:
                    dependencies.append((f"task_{dep_idx}", task_id))
        
        # Build dependency graph
        try:
            self.scheduler.build_dependency_graph(tasks, dependencies)
        except Exception as e:
            logger.error(f"Error building dependency graph: {e}")
            state["parallel_plan"] = {"groups": [[str(i) for i in range(len(task_list))]]}
            return state
        
        # Compute parallel execution groups
        parallel_groups = self.scheduler.compute_parallel_groups()
        
        # Compute scheduling stats
        stats = self.scheduler.compute_scheduling_stats()
        
        logger.info(
            f"Parallel execution plan: {len(parallel_groups)} groups, "
            f"parallelism factor: {stats.get('parallelism_factor', 1.0):.2f}x"
        )
        
        state["parallel_plan"] = {
            "groups": parallel_groups,
            "stats": stats,
            "critical_path": stats.get("critical_path", []),
        }
        
        return state
    
    def register_agents(self, agents: Dict[str, Any]) -> None:
        """
        Register agents with the pool.
        
        Args:
            agents: Dictionary mapping agent_id to agent object
        """
        for agent_id, agent_obj in agents.items():
            # Determine role from agent ID
            role = agent_id.split('_')[0]  # e.g., "coder" from "coder_1"
            self.agent_pool.register_agent(agent_id, role, agent_obj)
        
        logger.info(f"Registered {len(agents)} agents")
    
    def execute_parallel_group(
        self,
        group_tasks: List[str],
        state: Dict[str, Any],
        agents: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute a group of tasks in parallel.
        
        Args:
            group_tasks: List of task indices in group
            state: Current workflow state
            agents: Dictionary of available agents
            
        Returns:
            Updated state with results
        """
        logger.info(f"Executing parallel group with tasks: {group_tasks}")
        
        task_list = state.get("task_list", [])
        results = {}
        
        # Submit tasks to parallel pool
        for task_idx in group_tasks:
            if task_idx < len(task_list):
                task = task_list[task_idx]
                task_id = f"task_{task_idx}"
                
                # Determine agent role from task
                agent_role = "coder"  # Default role
                if hasattr(task, 'type'):
                    if "test" in str(task.type).lower():
                        agent_role = "tester"
                    elif "review" in str(task.type).lower():
                        agent_role = "reviewer"
                
                # Submit task
                parallel_task = self.agent_pool.submit_task(
                    task_id=task_id,
                    name=task.title if hasattr(task, 'title') else str(task),
                    description=task.description if hasattr(task, 'description') else "",
                    agent_role=agent_role,
                    priority=TaskPriority.NORMAL,
                )
        
        # Execute all tasks in parallel
        results = self.agent_pool.execute_parallel_tasks(state)
        
        # Collect execution summary
        execution_summary = self.agent_pool.get_execution_summary()
        
        logger.info(f"Parallel group execution complete: {execution_summary}")
        
        return results
    
    def detect_and_resolve_conflicts(
        self,
        results: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Detect and resolve conflicts from parallel execution.
        
        Args:
            results: Results from parallel execution
            
        Returns:
            Resolved results
        """
        logger.info("Detecting conflicts from parallel execution...")
        
        # Get detected conflicts
        conflicts = self.conflict_detector.get_conflicts(critical_only=False)
        
        if not conflicts:
            logger.info("No conflicts detected")
            return results
        
        logger.warning(f"Detected {len(conflicts)} conflicts")
        
        # Resolve all conflicts
        resolutions = self.conflict_resolver.resolve_all_conflicts(conflicts)
        
        # Apply resolutions to results
        resolved_results = results.copy()
        
        for resolution in resolutions:
            if resolution.success:
                # Extract task ID from conflict ID
                conflict_id = resolution.conflict_id
                # Try to find corresponding result key
                for result_key in results:
                    if conflict_id in result_key or result_key in conflict_id:
                        resolved_results[result_key] = resolution.resolved_value
        
        logger.info(
            f"Resolved {sum(1 for r in resolutions if r.success)}/{len(resolutions)} conflicts"
        )
        
        return resolved_results
    
    def merge_parallel_results(
        self,
        group_results: List[Dict[str, Any]],
        state: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Merge results from all parallel execution groups.
        
        Args:
            group_results: List of results from each group
            state: Current workflow state
            
        Returns:
            Merged state
        """
        logger.info("Merging parallel execution results...")
        
        # Merge code changes
        all_code_changes = []
        for group_result in group_results:
            if "code_changes" in group_result:
                if isinstance(group_result["code_changes"], list):
                    all_code_changes.extend(group_result["code_changes"])
                else:
                    all_code_changes.append(group_result["code_changes"])
        
        state["code_changes"] = all_code_changes
        
        # Merge test results
        all_test_results = {}
        for group_result in group_results:
            if "test_results" in group_result:
                all_test_results.update(group_result.get("test_results", {}))
        
        state["test_results"] = all_test_results
        
        # Update state version
        self.state_version_manager.record_write(
            agent_id="orchestrator",
            state_key="merged_results",
            value={
                "code_changes_count": len(all_code_changes),
                "test_results_count": len(all_test_results),
            },
        )
        
        logger.info(
            f"Merged {len(all_code_changes)} code changes "
            f"and {len(all_test_results)} test results"
        )
        
        return state
    
    def execute_parallel_workflow(
        self,
        state: Dict[str, Any],
        agents: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute entire workflow with parallel agent execution.
        
        Args:
            state: Initial workflow state
            agents: Dictionary of available agents
            
        Returns:
            Final state after execution
        """
        logger.info("Starting parallel workflow execution...")
        
        # Register agents
        self.register_agents(agents)
        
        # Plan parallel execution
        state = self.plan_parallel_execution(state)
        
        # Get execution groups
        parallel_groups = state.get("parallel_plan", {}).get("groups", [])
        
        if not parallel_groups:
            logger.warning("No parallel groups to execute")
            return state
        
        # Execute each group sequentially (groups internally execute in parallel)
        all_group_results = []
        
        for group_idx, group_tasks in enumerate(parallel_groups):
            logger.info(f"Executing group {group_idx + 1}/{len(parallel_groups)}")
            
            # Execute group in parallel
            group_results = self.execute_parallel_group(
                group_tasks,
                state,
                agents,
            )
            
            all_group_results.append(group_results)
            
            # Detect and resolve conflicts
            group_results = self.detect_and_resolve_conflicts(group_results)
            all_group_results[-1] = group_results
        
        # Merge all results
        state = self.merge_parallel_results(all_group_results, state)
        
        logger.info("Parallel workflow execution complete")
        
        return state
    
    def get_execution_metrics(self) -> Dict[str, Any]:
        """
        Get execution metrics and performance data.
        
        Returns:
            Metrics dictionary
        """
        pool_summary = self.agent_pool.get_execution_summary()
        
        metrics = {
            "pool_metrics": pool_summary,
            "conflicts_detected": len(self.conflict_detector.get_conflicts()),
            "conflicts_resolved": len(self.conflict_resolver.get_resolutions()),
            "scheduling_stats": self.scheduler.scheduling_stats,
        }
        
        return metrics
    
    def shutdown(self) -> None:
        """Shutdown orchestrator and cleanup resources."""
        self.agent_pool.shutdown()
        logger.info("ParallelWorkflowOrchestrator shutdown complete")


def create_parallel_workflow_orchestrator(
    max_parallel_agents: int = 4,
) -> ParallelWorkflowOrchestrator:
    """Factory function for creating parallel workflow orchestrator."""
    return ParallelWorkflowOrchestrator(max_parallel_agents)

