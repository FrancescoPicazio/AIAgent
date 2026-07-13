"""
Parallel Agent Pool and Executor.

Manages concurrent execution of multiple agents for independent tasks.
Handles task distribution, agent lifecycle, and result synchronization.
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, Future
from datetime import datetime
import threading

logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """Priority levels for parallel tasks."""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


class ExecutionPhase(Enum):
    """Execution phase for parallel operations."""
    PENDING = "pending"
    ASSIGNED = "assigned"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class ParallelTask:
    """Represents a task that can be executed in parallel."""
    task_id: str
    name: str
    description: str
    agent_role: str  # "coder", "tester", "reviewer", "security_analyzer"
    priority: TaskPriority = TaskPriority.NORMAL
    dependencies: List[str] = field(default_factory=list)
    timeout_seconds: int = 300
    max_retries: int = 3
    
    # Execution tracking
    phase: ExecutionPhase = ExecutionPhase.PENDING
    assigned_agent_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    
    # Results
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_duration_seconds: float = 0.0
    
    def is_pending(self) -> bool:
        """Check if task is pending."""
        return self.phase == ExecutionPhase.PENDING
    
    def is_completed(self) -> bool:
        """Check if task is completed."""
        return self.phase == ExecutionPhase.COMPLETED
    
    def is_failed(self) -> bool:
        """Check if task is failed."""
        return self.phase == ExecutionPhase.FAILED
    
    def can_retry(self) -> bool:
        """Check if task can be retried."""
        return self.retry_count < self.max_retries and not self.is_completed()
    
    def mark_executing(self, agent_id: str):
        """Mark task as executing."""
        self.phase = ExecutionPhase.EXECUTING
        self.assigned_agent_id = agent_id
        self.started_at = datetime.now()
    
    def mark_completed(self, result: Dict[str, Any]):
        """Mark task as completed with result."""
        self.phase = ExecutionPhase.COMPLETED
        self.result = result
        self.completed_at = datetime.now()
        if self.started_at:
            self.execution_duration_seconds = (
                self.completed_at - self.started_at
            ).total_seconds()
    
    def mark_failed(self, error: str):
        """Mark task as failed with error."""
        self.phase = ExecutionPhase.FAILED
        self.error = error
        self.completed_at = datetime.now()
        if self.started_at:
            self.execution_duration_seconds = (
                self.completed_at - self.started_at
            ).total_seconds()
        self.retry_count += 1


@dataclass
class AgentInstance:
    """Represents an agent instance in the pool."""
    agent_id: str
    role: str  # "coder", "tester", "reviewer", "security_analyzer"
    agent_object: Any
    is_available: bool = True
    current_task: Optional[str] = None
    total_tasks_completed: int = 0
    total_execution_time: float = 0.0
    last_executed_at: Optional[datetime] = None


class ParallelAgentPool:
    """
    Manages a pool of agents that can execute tasks in parallel.
    
    Responsibilities:
    - Task distribution and scheduling
    - Agent lifecycle management
    - Synchronization and coordination
    - Result collection and merging
    """
    
    def __init__(self, max_parallel_agents: int = 4):
        """
        Initialize parallel agent pool.
        
        Args:
            max_parallel_agents: Maximum number of agents running in parallel
        """
        self.max_parallel_agents = max_parallel_agents
        self.agents: Dict[str, AgentInstance] = {}
        self.task_queue: List[ParallelTask] = []
        self.completed_tasks: Dict[str, ParallelTask] = {}
        self.failed_tasks: List[ParallelTask] = []
        
        # Threading infrastructure
        self.executor = ThreadPoolExecutor(max_workers=max_parallel_agents)
        self.active_futures: Dict[str, Future] = {}
        self.lock = threading.RLock()
        
        # Execution tracking
        self.total_tasks_submitted = 0
        self.total_tasks_completed = 0
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        
        logger.info(f"ParallelAgentPool initialized with {max_parallel_agents} workers")
    
    def register_agent(self, agent_id: str, role: str, agent_object: Any) -> None:
        """
        Register an agent in the pool.
        
        Args:
            agent_id: Unique identifier for agent
            role: Agent role (coder, tester, reviewer, security_analyzer)
            agent_object: The actual agent object
        """
        with self.lock:
            self.agents[agent_id] = AgentInstance(
                agent_id=agent_id,
                role=role,
                agent_object=agent_object,
            )
            logger.info(f"Agent {agent_id} ({role}) registered in pool")
    
    def submit_task(
        self,
        task_id: str,
        name: str,
        description: str,
        agent_role: str,
        priority: TaskPriority = TaskPriority.NORMAL,
        dependencies: Optional[List[str]] = None,
        timeout_seconds: int = 300,
    ) -> ParallelTask:
        """
        Submit a task for parallel execution.
        
        Args:
            task_id: Unique identifier for task
            name: Task name
            description: Task description
            agent_role: Required agent role
            priority: Task priority
            dependencies: List of task IDs that must complete first
            timeout_seconds: Task timeout
            
        Returns:
            ParallelTask instance
        """
        with self.lock:
            task = ParallelTask(
                task_id=task_id,
                name=name,
                description=description,
                agent_role=agent_role,
                priority=priority,
                dependencies=dependencies or [],
                timeout_seconds=timeout_seconds,
            )
            
            self.task_queue.append(task)
            self.total_tasks_submitted += 1
            
            logger.info(
                f"Task {task_id} ({name}) submitted with priority {priority.name}"
            )
            
            return task
    
    def get_available_agent(self, required_role: str) -> Optional[AgentInstance]:
        """
        Get an available agent with required role.
        
        Args:
            required_role: Required agent role
            
        Returns:
            Available AgentInstance or None
        """
        with self.lock:
            for agent in self.agents.values():
                if agent.role == required_role and agent.is_available:
                    return agent
            return None
    
    def sort_tasks_by_priority(self) -> None:
        """Sort task queue by priority and dependencies."""
        with self.lock:
            # First, sort by priority
            self.task_queue.sort(
                key=lambda t: (t.priority.value, t.created_at)
            )
    
    def check_dependencies(self, task: ParallelTask) -> bool:
        """
        Check if all dependencies of a task are completed.
        
        Args:
            task: Task to check
            
        Returns:
            True if all dependencies are completed
        """
        for dep_id in task.dependencies:
            if dep_id not in self.completed_tasks:
                # Dependency not completed
                return False
        return True
    
    def get_executable_tasks(self) -> List[ParallelTask]:
        """
        Get all tasks that are ready to execute (dependencies satisfied).
        
        Returns:
            List of executable ParallelTask instances
        """
        with self.lock:
            executable = []
            for task in self.task_queue:
                if task.is_pending() and self.check_dependencies(task):
                    executable.append(task)
            return executable
    
    def execute_task(
        self,
        task: ParallelTask,
        agent: AgentInstance,
        state: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute a task with an agent.
        
        Args:
            task: Task to execute
            agent: Agent to use
            state: Current workflow state
            
        Returns:
            Execution result
        """
        try:
            logger.info(
                f"Executing task {task.task_id} ({task.name}) "
                f"with agent {agent.agent_id}"
            )
            
            # Mark task as executing
            task.mark_executing(agent.agent_id)
            agent.is_available = False
            agent.current_task = task.task_id
            
            # Prepare task state
            task_state = state.copy()
            task_state["current_task_id"] = task.task_id
            task_state["task_description"] = task.description
            
            # Execute agent with task
            result = agent.agent_object.run(task_state)
            
            # Mark task as completed
            task.mark_completed(result)
            agent.is_available = True
            agent.current_task = None
            agent.total_tasks_completed += 1
            
            logger.info(f"Task {task.task_id} completed successfully")
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing task {task.task_id}: {str(e)}")
            task.mark_failed(str(e))
            agent.is_available = True
            agent.current_task = None
            raise
    
    def submit_task_for_execution(
        self,
        task: ParallelTask,
        agent: AgentInstance,
        state: Dict[str, Any],
    ) -> str:
        """
        Submit a task for asynchronous execution.
        
        Args:
            task: Task to execute
            agent: Agent to use
            state: Current workflow state
            
        Returns:
            Task ID for tracking
        """
        future = self.executor.submit(
            self.execute_task,
            task,
            agent,
            state,
        )
        
        with self.lock:
            self.active_futures[task.task_id] = future
        
        logger.info(f"Task {task.task_id} submitted to executor")
        
        return task.task_id
    
    def execute_parallel_tasks(
        self,
        state: Dict[str, Any],
        max_concurrent: Optional[int] = None,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Execute all ready tasks in parallel.
        
        Args:
            state: Current workflow state
            max_concurrent: Maximum concurrent tasks (None = use pool max)
            
        Returns:
            Dictionary mapping task_id to results
        """
        if max_concurrent is None:
            max_concurrent = self.max_parallel_agents
        
        results = {}
        self.start_time = datetime.now()
        
        # Sort tasks by priority
        self.sort_tasks_by_priority()
        
        # Execute tasks in batches
        executing_count = 0
        
        while self.task_queue:
            # Get executable tasks
            executable = self.get_executable_tasks()
            
            if not executable:
                # No executable tasks, but some still pending
                # Wait for completion
                if self.active_futures:
                    self._wait_for_any_completion()
                else:
                    break
                continue
            
            # Assign tasks to available agents
            for task in executable[:max_concurrent - executing_count]:
                agent = self.get_available_agent(task.agent_role)
                
                if agent:
                    self.submit_task_for_execution(task, agent, state)
                    executing_count += 1
                    
                    with self.lock:
                        self.task_queue.remove(task)
            
            # Wait for at least one completion
            if self.active_futures:
                task_id = self._wait_for_any_completion()
                if task_id:
                    results[task_id] = self.completed_tasks[task_id].result
                    executing_count -= 1
            else:
                break
        
        # Wait for all remaining tasks to complete
        self._wait_for_all_completion()
        
        # Collect all results
        for task_id, task in self.completed_tasks.items():
            if task.result:
                results[task_id] = task.result
        
        self.end_time = datetime.now()
        self.total_tasks_completed = len(self.completed_tasks)
        
        logger.info(
            f"All parallel tasks completed. "
            f"Total: {self.total_tasks_completed}, "
            f"Failed: {len(self.failed_tasks)}"
        )
        
        return results
    
    def _wait_for_any_completion(self) -> Optional[str]:
        """Wait for any task to complete."""
        if not self.active_futures:
            return None
        
        done_futures = []
        
        for task_id, future in self.active_futures.items():
            try:
                # Use timeout to prevent blocking
                result = future.result(timeout=1)
                done_futures.append(task_id)
                
                with self.lock:
                    self.completed_tasks[task_id] = (
                        next(
                            t for t in [task for task_list in [self.task_queue]
                                       for task in task_list]
                            if t.task_id == task_id
                        )
                        if task_id in [t.task_id for t in self.task_queue]
                        else None
                    )
                
                logger.info(f"Task {task_id} completed")
                
            except (asyncio.TimeoutError, TimeoutError):
                pass
            except Exception as e:
                logger.error(f"Task {task_id} raised exception: {e}")
                done_futures.append(task_id)
        
        # Remove completed futures
        for task_id in done_futures:
            with self.lock:
                del self.active_futures[task_id]
        
        return done_futures[0] if done_futures else None
    
    def _wait_for_all_completion(self) -> None:
        """Wait for all active tasks to complete."""
        while self.active_futures:
            self._wait_for_any_completion()
            time.sleep(0.1)
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """
        Get execution summary and metrics.
        
        Returns:
            Execution summary with metrics
        """
        total_duration = (
            (self.end_time - self.start_time).total_seconds()
            if self.start_time and self.end_time
            else 0.0
        )
        
        summary = {
            "total_tasks_submitted": self.total_tasks_submitted,
            "total_tasks_completed": self.total_tasks_completed,
            "failed_tasks": len(self.failed_tasks),
            "total_execution_time_seconds": total_duration,
            "average_task_time_seconds": (
                total_duration / self.total_tasks_completed
                if self.total_tasks_completed > 0
                else 0.0
            ),
            "parallelism_factor": (
                sum(
                    a.total_tasks_completed
                    for a in self.agents.values()
                ) / self.total_tasks_completed
                if self.total_tasks_completed > 0
                else 0.0
            ),
            "agent_statistics": {
                agent_id: {
                    "role": agent.role,
                    "tasks_completed": agent.total_tasks_completed,
                    "total_execution_time": agent.total_execution_time,
                }
                for agent_id, agent in self.agents.items()
            },
        }
        
        logger.info(f"Execution summary: {summary}")
        
        return summary
    
    def shutdown(self) -> None:
        """Shutdown the thread pool and cleanup."""
        self.executor.shutdown(wait=True)
        logger.info("ParallelAgentPool shutdown complete")


def create_parallel_agent_pool(
    max_parallel_agents: int = 4,
) -> ParallelAgentPool:
    """Factory function for creating parallel agent pool."""
    return ParallelAgentPool(max_parallel_agents)

