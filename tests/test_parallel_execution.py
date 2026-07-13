"""
Tests for Parallel Agents Execution System (Task 19).

Tests parallel agent pool, synchronization, conflict resolution,
and scheduling functionality.
"""

import pytest
import time
import threading
from datetime import datetime
from core.parallel_agent_pool import (
    ParallelAgentPool,
    ParallelTask,
    TaskPriority,
    ExecutionPhase,
    create_parallel_agent_pool,
)
from core.synchronization import (
    LockManager,
    LockType,
    VectorClockVersion,
    StateVersionManager,
    SynchronizationBarrier,
    create_lock_manager,
    create_state_version_manager,
    create_synchronization_barrier,
)
from core.conflict_resolver import (
    ConflictDetector,
    ConflictResolver,
    ConflictType,
    ResolutionStrategy,
    create_conflict_detector,
    create_conflict_resolver,
)
from core.parallel_scheduler import (
    ParallelScheduler,
    DependencyType,
    TaskDependency,
    create_parallel_scheduler,
)


class TestParallelAgentPool:
    """Test suite for ParallelAgentPool."""
    
    def test_pool_creation(self):
        """Test pool creation with specified workers."""
        pool = create_parallel_agent_pool(max_parallel_agents=4)
        assert pool.max_parallel_agents == 4
        assert len(pool.agents) == 0
    
    def test_register_agent(self):
        """Test agent registration."""
        pool = create_parallel_agent_pool()
        
        # Create mock agent
        mock_agent = type('MockAgent', (), {'run': lambda x: {}})()
        
        pool.register_agent("agent_1", "coder", mock_agent)
        
        assert "agent_1" in pool.agents
        assert pool.agents["agent_1"].role == "coder"
    
    def test_submit_task(self):
        """Test task submission."""
        pool = create_parallel_agent_pool()
        
        task = pool.submit_task(
            task_id="task_1",
            name="Test Task",
            description="A test task",
            agent_role="coder",
            priority=TaskPriority.NORMAL,
        )
        
        assert task.task_id == "task_1"
        assert task.is_pending()
        assert pool.total_tasks_submitted == 1
    
    def test_get_available_agent(self):
        """Test getting available agent."""
        pool = create_parallel_agent_pool()
        
        mock_agent = type('MockAgent', (), {'run': lambda x: {}})()
        pool.register_agent("coder_1", "coder", mock_agent)
        
        agent = pool.get_available_agent("coder")
        assert agent is not None
        assert agent.agent_id == "coder_1"
    
    def test_task_dependency_checking(self):
        """Test task dependency checking."""
        pool = create_parallel_agent_pool()
        
        task1 = pool.submit_task(
            "task_1", "Task 1", "", "coder",
            dependencies=[],
        )
        
        task2 = pool.submit_task(
            "task_2", "Task 2", "", "coder",
            dependencies=["task_1"],
        )
        
        # Task 1 has no dependencies
        assert pool.check_dependencies(task1) is True
        
        # Task 2 depends on task 1 (not completed)
        assert pool.check_dependencies(task2) is False
        
        # Mark task 1 as completed
        pool.completed_tasks["task_1"] = task1
        
        # Now task 2 can run
        assert pool.check_dependencies(task2) is True


class TestSynchronization:
    """Test suite for synchronization mechanisms."""
    
    def test_lock_manager_creation(self):
        """Test lock manager creation."""
        manager = create_lock_manager()
        assert manager is not None
    
    def test_acquire_exclusive_lock(self):
        """Test acquiring exclusive lock."""
        manager = create_lock_manager()
        
        lock = manager.acquire_lock(
            resource_id="file1.py",
            lock_type=LockType.FILE,
            agent_id="coder_1",
            exclusive=True,
        )
        
        assert lock.resource_id == "file1.py"
        assert lock.owner_agent_id == "coder_1"
        assert lock.is_exclusive is True
    
    def test_lock_conflict(self):
        """Test lock conflict prevention."""
        manager = create_lock_manager()
        
        # First agent acquires lock
        lock1 = manager.acquire_lock(
            resource_id="file1.py",
            lock_type=LockType.FILE,
            agent_id="coder_1",
            exclusive=True,
        )
        
        # Second agent tries to acquire same lock
        with pytest.raises(RuntimeError):
            manager.acquire_lock(
                resource_id="file1.py",
                lock_type=LockType.FILE,
                agent_id="coder_2",
                exclusive=True,
            )
    
    def test_lock_release(self):
        """Test lock release."""
        manager = create_lock_manager()
        
        lock = manager.acquire_lock(
            resource_id="file1.py",
            lock_type=LockType.FILE,
            agent_id="coder_1",
            exclusive=True,
        )
        
        manager.release_lock(lock)
        
        # Now another agent can acquire lock
        lock2 = manager.acquire_lock(
            resource_id="file1.py",
            lock_type=LockType.FILE,
            agent_id="coder_2",
            exclusive=True,
        )
        
        assert lock2.owner_agent_id == "coder_2"
    
    def test_vector_clock(self):
        """Test vector clock for causality tracking."""
        agents = ["agent_1", "agent_2", "agent_3"]
        clock1 = VectorClockVersion(agents)
        clock2 = VectorClockVersion(agents)
        
        clock1.increment("agent_1")
        clock1.increment("agent_1")
        clock2.increment("agent_2")
        
        # Clock1 and Clock2 are concurrent
        assert clock1.concurrent_with(clock2)
        
        # Clock1 happens before Clock1 + increment
        clock2.increment("agent_1")
        clock2.increment("agent_1")
        clock2.increment("agent_1")
        
        # Now clock1 might happen before clock2
        assert clock1.happens_before(clock2)
    
    def test_state_version_manager(self):
        """Test state version tracking."""
        agents = ["agent_1", "agent_2"]
        manager = create_state_version_manager(agents)
        
        # Record write from agent 1
        record1 = manager.record_write(
            agent_id="agent_1",
            state_key="code_changes",
            value={"file": "app.py", "lines": 10},
        )
        
        assert record1["agent_id"] == "agent_1"
        assert record1["value"]["file"] == "app.py"
        
        # Record write from agent 2
        record2 = manager.record_write(
            agent_id="agent_2",
            state_key="code_changes",
            value={"file": "app.py", "lines": 20},
        )
        
        # Check history
        history = manager.get_state_history("code_changes")
        assert len(history) == 2
    
    def test_synchronization_barrier(self):
        """Test synchronization barrier."""
        barrier = create_synchronization_barrier(
            num_agents=3,
            timeout_seconds=5,
        )
        
        results = []
        
        def agent_work(agent_id):
            time.sleep(0.1)  # Simulate work
            result = barrier.wait(agent_id)
            results.append((agent_id, result))
        
        threads = [
            threading.Thread(target=agent_work, args=(f"agent_{i}",))
            for i in range(3)
        ]
        
        for t in threads:
            t.start()
        
        for t in threads:
            t.join()
        
        # All agents should successfully pass barrier
        assert len(results) == 3
        assert all(result is True for _, result in results)


class TestConflictResolution:
    """Test suite for conflict detection and resolution."""
    
    def test_conflict_detector_creation(self):
        """Test conflict detector creation."""
        detector = create_conflict_detector()
        assert detector is not None
    
    def test_detect_file_conflict(self):
        """Test file conflict detection."""
        detector = create_conflict_detector()
        
        content_a = "line1\nline2\nline3\n"
        content_b = "line1\nmodified_line2\nline3\n"
        
        conflict = detector.detect_file_conflict(
            file_path="app.py",
            content_a=content_a,
            content_b=content_b,
            agent_a="coder_1",
            agent_b="coder_2",
            timestamp_a=datetime.now(),
            timestamp_b=datetime.now(),
        )
        
        assert conflict is not None
        assert conflict.conflict_type == ConflictType.FILE_CONFLICT
    
    def test_detect_state_conflict(self):
        """Test state conflict detection."""
        detector = create_conflict_detector()
        
        state_a = {"key1": "value_a", "key2": 10}
        state_b = {"key1": "value_b", "key2": 20}
        
        conflict = detector.detect_state_conflict(
            state_key="task_results",
            state_a=state_a,
            state_b=state_b,
            agent_a="agent_1",
            agent_b="agent_2",
            timestamp_a=datetime.now(),
            timestamp_b=datetime.now(),
        )
        
        assert conflict is not None
        assert conflict.conflict_type == ConflictType.STATE_CONFLICT
    
    def test_resolve_conflict_last_write_wins(self):
        """Test conflict resolution with last-write-wins."""
        detector = create_conflict_detector()
        resolver = create_conflict_resolver()
        
        time_a = datetime.now()
        time_b = datetime(year=time_a.year, month=time_a.month,
                         day=time_a.day, hour=time_a.hour,
                         minute=time_a.minute, second=time_a.second + 1)
        
        conflict = detector.detect_file_conflict(
            file_path="app.py",
            content_a="content_a",
            content_b="content_b",
            agent_a="coder_1",
            agent_b="coder_2",
            timestamp_a=time_a,
            timestamp_b=time_b,
        )
        
        resolution = resolver.resolve_conflict(
            conflict,
            preferred_strategy=ResolutionStrategy.LAST_WRITE_WINS,
        )
        
        assert resolution.success is True
        assert resolution.resolved_value == "content_b"  # Later timestamp


class TestParallelScheduler:
    """Test suite for task scheduler."""
    
    def test_scheduler_creation(self):
        """Test scheduler creation."""
        scheduler = create_parallel_scheduler()
        assert scheduler is not None
    
    def test_build_dependency_graph(self):
        """Test building dependency graph."""
        scheduler = create_parallel_scheduler()
        
        tasks = {
            "task_1": {"name": "Task 1"},
            "task_2": {"name": "Task 2"},
            "task_3": {"name": "Task 3"},
        }
        
        dependencies = [
            ("task_1", "task_2"),
            ("task_2", "task_3"),
        ]
        
        graph = scheduler.build_dependency_graph(tasks, dependencies)
        
        assert len(graph.tasks) == 3
        assert len(graph.edges) == 2
    
    def test_cycle_detection(self):
        """Test cycle detection in dependency graph."""
        scheduler = create_parallel_scheduler()
        
        tasks = {
            "task_1": {"name": "Task 1"},
            "task_2": {"name": "Task 2"},
            "task_3": {"name": "Task 3"},
        }
        
        # Create circular dependency
        dependencies = [
            ("task_1", "task_2"),
            ("task_2", "task_3"),
            ("task_3", "task_1"),  # Creates cycle
        ]
        
        with pytest.raises(ValueError):
            scheduler.build_dependency_graph(tasks, dependencies)
    
    def test_compute_parallel_groups(self):
        """Test computation of parallel execution groups."""
        scheduler = create_parallel_scheduler()
        
        tasks = {
            "task_1": {"name": "Task 1"},
            "task_2": {"name": "Task 2"},
            "task_3": {"name": "Task 3"},
        }
        
        dependencies = [
            ("task_1", "task_2"),
            ("task_1", "task_3"),
        ]
        
        scheduler.build_dependency_graph(tasks, dependencies)
        groups = scheduler.compute_parallel_groups()
        
        # Should have 2 groups: [task_1] and [task_2, task_3]
        assert len(groups) == 2
        assert "task_1" in groups[0]
        assert set(groups[1]) == {"task_2", "task_3"}
    
    def test_compute_critical_path(self):
        """Test critical path computation."""
        scheduler = create_parallel_scheduler()
        
        tasks = {
            "task_1": {"name": "Task 1"},
            "task_2": {"name": "Task 2"},
            "task_3": {"name": "Task 3"},
            "task_4": {"name": "Task 4"},
        }
        
        dependencies = [
            ("task_1", "task_2"),
            ("task_2", "task_3"),
            ("task_3", "task_4"),
        ]
        
        scheduler.build_dependency_graph(tasks, dependencies)
        critical_path = scheduler.compute_critical_path()
        
        assert len(critical_path) > 0
        assert "task_1" in critical_path
        assert "task_4" in critical_path
    
    def test_scheduling_stats(self):
        """Test scheduling statistics computation."""
        scheduler = create_parallel_scheduler()
        
        tasks = {
            "task_1": {"name": "Task 1"},
            "task_2": {"name": "Task 2"},
            "task_3": {"name": "Task 3"},
        }
        
        dependencies = [
            ("task_1", "task_2"),
            ("task_1", "task_3"),
        ]
        
        scheduler.build_dependency_graph(tasks, dependencies)
        stats = scheduler.compute_scheduling_stats()
        
        assert stats["total_tasks"] == 3
        assert stats["num_parallel_groups"] > 0
        assert stats["parallelism_factor"] >= 1.0  # At least 1.0 (serial), typically > 1.0 with parallelism


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

