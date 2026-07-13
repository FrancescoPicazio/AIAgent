"""
Parallel Task Scheduler and Dependency Analyzer.

Analyzes task dependencies and determines which tasks can be executed
in parallel to optimize workflow efficiency.
"""

import logging
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class DependencyType(Enum):
    """Types of dependencies between tasks."""
    HARD = "hard"  # Must complete before next can start
    SOFT = "soft"  # Preferred order, but can run in parallel with care
    DATA = "data"  # Data dependency - writes from one, reads from another


@dataclass
class TaskDependency:
    """Represents dependency between tasks."""
    task_a_id: str
    task_b_id: str
    dependency_type: DependencyType
    description: str = ""


@dataclass
class DependencyGraph:
    """Graph of task dependencies."""
    tasks: Dict[str, Any] = field(default_factory=dict)
    edges: List[TaskDependency] = field(default_factory=list)
    
    def add_task(self, task_id: str, task_data: Dict[str, Any]) -> None:
        """Add task to graph."""
        self.tasks[task_id] = task_data
    
    def add_dependency(self, dep: TaskDependency) -> None:
        """Add dependency edge."""
        self.edges.append(dep)
    
    def get_predecessors(self, task_id: str) -> List[str]:
        """Get all tasks that must complete before this task."""
        predecessors = []
        for edge in self.edges:
            if (
                edge.task_b_id == task_id
                and edge.dependency_type == DependencyType.HARD
            ):
                predecessors.append(edge.task_a_id)
        return predecessors
    
    def get_successors(self, task_id: str) -> List[str]:
        """Get all tasks that depend on this task."""
        successors = []
        for edge in self.edges:
            if (
                edge.task_a_id == task_id
                and edge.dependency_type == DependencyType.HARD
            ):
                successors.append(edge.task_b_id)
        return successors
    
    def has_cycle(self) -> bool:
        """Check if graph has cycles (deadlock risk)."""
        visited = set()
        rec_stack = set()
        
        def visit(node):
            visited.add(node)
            rec_stack.add(node)
            
            for successor in self.get_successors(node):
                if successor not in visited:
                    if visit(successor):
                        return True
                elif successor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for task_id in self.tasks:
            if task_id not in visited:
                if visit(task_id):
                    return True
        
        return False


class ParallelScheduler:
    """
    Schedules parallel task execution based on dependencies.
    
    Analyzes task dependencies and creates execution groups
    that can run in parallel.
    """
    
    def __init__(self):
        """Initialize scheduler."""
        self.dependency_graph: Optional[DependencyGraph] = None
        self.parallel_groups: List[List[str]] = []
        self.scheduling_stats: Dict[str, Any] = {}
        
        logger.info("ParallelScheduler initialized")
    
    def build_dependency_graph(
        self,
        tasks: Dict[str, Dict[str, Any]],
        dependencies: List[Tuple[str, str]],
    ) -> DependencyGraph:
        """
        Build dependency graph from tasks and dependencies.
        
        Args:
            tasks: Dictionary mapping task_id to task data
            dependencies: List of (task_a_id, task_b_id) tuples
            
        Returns:
            DependencyGraph
        """
        graph = DependencyGraph()
        
        # Add tasks
        for task_id, task_data in tasks.items():
            graph.add_task(task_id, task_data)
        
        # Add dependencies
        for task_a_id, task_b_id in dependencies:
            dep = TaskDependency(
                task_a_id=task_a_id,
                task_b_id=task_b_id,
                dependency_type=DependencyType.HARD,
            )
            graph.add_dependency(dep)
        
        # Check for cycles
        if graph.has_cycle():
            logger.error("Circular dependency detected in task graph!")
            raise ValueError("Task graph contains circular dependencies")
        
        self.dependency_graph = graph
        
        logger.info(
            f"Dependency graph built: "
            f"{len(graph.tasks)} tasks, {len(graph.edges)} dependencies"
        )
        
        return graph
    
    def compute_critical_path(self) -> List[str]:
        """
        Compute the critical path (longest dependency chain).
        
        This path determines the minimum time to complete all tasks.
        
        Returns:
            List of task IDs in critical path
        """
        if not self.dependency_graph:
            return []
        
        # Compute longest path using dynamic programming
        longest_paths = {}
        
        def compute_longest_from(task_id: str) -> int:
            if task_id in longest_paths:
                return longest_paths[task_id]
            
            successors = self.dependency_graph.get_successors(task_id)
            
            if not successors:
                longest_paths[task_id] = 1
                return 1
            
            max_len = 1 + max(compute_longest_from(s) for s in successors)
            longest_paths[task_id] = max_len
            return max_len
        
        # Compute from all tasks
        for task_id in self.dependency_graph.tasks:
            compute_longest_from(task_id)
        
        # Reconstruct path
        critical_path = []
        current_max = max(longest_paths.values()) if longest_paths else 0
        
        for task_id in self.dependency_graph.tasks:
            if longest_paths.get(task_id) == current_max:
                critical_path.append(task_id)
                
                # Find next task in path
                for successor in self.dependency_graph.get_successors(task_id):
                    if (
                        longest_paths.get(successor)
                        == current_max - 1
                    ):
                        current_max -= 1
                        break
        
        logger.info(f"Critical path: {critical_path} (length: {len(critical_path)})")
        
        return critical_path
    
    def compute_parallel_groups(self) -> List[List[str]]:
        """
        Compute groups of tasks that can run in parallel.
        
        Returns:
            List of task groups, each group can run in parallel
        """
        if not self.dependency_graph:
            return []
        
        groups = []
        remaining_tasks = set(self.dependency_graph.tasks.keys())
        
        while remaining_tasks:
            # Find tasks with no pending dependencies in remaining tasks
            current_group = []
            
            for task_id in remaining_tasks:
                predecessors = self.dependency_graph.get_predecessors(task_id)
                
                # Check if all predecessors are done
                if not any(p in remaining_tasks for p in predecessors):
                    current_group.append(task_id)
            
            if not current_group:
                # No progress made, deadlock or issue
                logger.warning(
                    f"Cannot find executable group. "
                    f"Remaining: {remaining_tasks}"
                )
                break
            
            groups.append(current_group)
            remaining_tasks -= set(current_group)
            
            logger.info(f"Parallel group {len(groups)}: {current_group}")
        
        self.parallel_groups = groups
        
        return groups
    
    def compute_scheduling_stats(self) -> Dict[str, Any]:
        """
        Compute scheduling statistics and parallelism potential.
        
        Returns:
            Statistics dictionary
        """
        if not self.dependency_graph:
            return {}
        
        critical_path = self.compute_critical_path()
        parallel_groups = self.compute_parallel_groups()
        
        total_tasks = len(self.dependency_graph.tasks)
        critical_path_length = len(critical_path)
        
        # Parallelism factor: how much we can parallelize
        # If we execute sequentially, it takes total_tasks steps
        # With parallelism, it takes critical_path_length steps
        parallelism_factor = (
            total_tasks / critical_path_length
            if critical_path_length > 0
            else 1.0
        )
        
        # Compute average group size
        avg_group_size = (
            sum(len(g) for g in parallel_groups) / len(parallel_groups)
            if parallel_groups
            else 1.0
        )
        
        stats = {
            "total_tasks": total_tasks,
            "critical_path_length": critical_path_length,
            "num_parallel_groups": len(parallel_groups),
            "parallelism_factor": parallelism_factor,
            "average_group_size": avg_group_size,
            "critical_path": critical_path,
            "parallel_groups": parallel_groups,
            "max_dependencies": (
                max(
                    len(self.dependency_graph.get_predecessors(t))
                    for t in self.dependency_graph.tasks
                )
                if self.dependency_graph.tasks
                else 0
            ),
        }
        
        self.scheduling_stats = stats
        
        logger.info(f"Scheduling stats: {stats}")
        
        return stats
    
    def get_execution_order(
        self,
        max_parallel: int = 4,
    ) -> List[List[str]]:
        """
        Get execution order respecting parallelism limit.
        
        Args:
            max_parallel: Maximum parallel tasks at once
            
        Returns:
            List of task batches to execute
        """
        groups = self.compute_parallel_groups()
        
        # If groups fit within limit, return as-is
        if all(len(g) <= max_parallel for g in groups):
            return groups
        
        # Otherwise, split large groups
        execution_order = []
        for group in groups:
            if len(group) <= max_parallel:
                execution_order.append(group)
            else:
                # Split into smaller batches
                for i in range(0, len(group), max_parallel):
                    execution_order.append(group[i:i + max_parallel])
        
        logger.info(f"Execution order computed: {len(execution_order)} batches")
        
        return execution_order
    
    def estimate_total_execution_time(
        self,
        task_durations: Dict[str, float],
    ) -> float:
        """
        Estimate total execution time with parallel scheduling.
        
        Args:
            task_durations: Dictionary mapping task_id to duration in seconds
            
        Returns:
            Estimated total time in seconds
        """
        groups = self.compute_parallel_groups()
        
        total_time = 0.0
        for group in groups:
            # Each group runs in parallel, so time is max of group
            group_time = max(
                task_durations.get(task_id, 1.0)
                for task_id in group
            )
            total_time += group_time
        
        logger.info(f"Estimated total execution time: {total_time}s")
        
        return total_time
    
    def identify_bottlenecks(self) -> List[str]:
        """
        Identify tasks that are bottlenecks.
        
        A bottleneck is a task with many successors or on critical path.
        
        Returns:
            List of bottleneck task IDs
        """
        if not self.dependency_graph:
            return []
        
        critical_path = self.compute_critical_path()
        bottlenecks = []
        
        for task_id in self.dependency_graph.tasks:
            # Check if on critical path
            if task_id in critical_path:
                bottlenecks.append(task_id)
            # Check if has many successors
            elif len(self.dependency_graph.get_successors(task_id)) > 2:
                bottlenecks.append(task_id)
        
        logger.info(f"Bottleneck tasks: {bottlenecks}")
        
        return bottlenecks


def create_parallel_scheduler() -> ParallelScheduler:
    """Factory function for creating parallel scheduler."""
    return ParallelScheduler()

