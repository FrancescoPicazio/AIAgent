"""
Synchronization layer for parallel agent execution.

Manages coordination, locking, and state consistency across parallel tasks.
"""

import threading
import logging
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import hashlib
import json

logger = logging.getLogger(__name__)


class LockType(Enum):
    """Types of locks for different resources."""
    FILE = "file"
    MODULE = "module"
    SECTION = "section"
    STATE = "state"


class VectorClockVersion:
    """Vector clock for tracking causality in distributed execution."""
    
    def __init__(self, agent_ids: List[str]):
        """
        Initialize vector clock.
        
        Args:
            agent_ids: List of agent IDs in the system
        """
        self.clock: Dict[str, int] = {agent_id: 0 for agent_id in agent_ids}
        self.agent_ids = agent_ids
    
    def increment(self, agent_id: str) -> None:
        """Increment clock for agent."""
        if agent_id in self.clock:
            self.clock[agent_id] += 1
    
    def merge(self, other: 'VectorClockVersion') -> None:
        """Merge with another vector clock."""
        for agent_id in self.clock:
            if agent_id in other.clock:
                self.clock[agent_id] = max(
                    self.clock[agent_id],
                    other.clock[agent_id]
                )
    
    def happens_before(self, other: 'VectorClockVersion') -> bool:
        """Check if this clock happens before another."""
        less = False
        for agent_id in self.clock:
            if self.clock[agent_id] > other.clock.get(agent_id, 0):
                return False
            if self.clock[agent_id] < other.clock.get(agent_id, 0):
                less = True
        return less
    
    def concurrent_with(self, other: 'VectorClockVersion') -> bool:
        """Check if concurrent with another clock."""
        return (
            not self.happens_before(other)
            and not other.happens_before(self)
        )
    
    def __str__(self) -> str:
        return str(self.clock)
    
    def to_dict(self) -> Dict[str, int]:
        """Convert to dictionary."""
        return self.clock.copy()


@dataclass
class ResourceLock:
    """Lock on a specific resource."""
    resource_id: str
    lock_type: LockType
    owner_agent_id: str
    acquired_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    is_exclusive: bool = True
    lock_id: str = ""
    
    def __post_init__(self):
        """Generate unique lock ID."""
        if not self.lock_id:
            content = (
                f"{self.resource_id}:{self.owner_agent_id}:"
                f"{self.acquired_at.isoformat()}"
            )
            self.lock_id = hashlib.md5(content.encode()).hexdigest()
    
    def is_expired(self) -> bool:
        """Check if lock is expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
    
    def duration_seconds(self) -> float:
        """Get lock duration in seconds."""
        return (datetime.now() - self.acquired_at).total_seconds()


class LockManager:
    """
    Manages resource locks for coordinating parallel agent access.
    
    Prevents race conditions and data corruption through exclusive
    and shared locks on critical resources.
    """
    
    def __init__(self):
        """Initialize lock manager."""
        self.locks: Dict[str, List[ResourceLock]] = {}
        self.lock = threading.RLock()
        self.lock_timeout_seconds = 300  # 5 minutes
        
        logger.info("LockManager initialized")
    
    def acquire_lock(
        self,
        resource_id: str,
        lock_type: LockType,
        agent_id: str,
        exclusive: bool = True,
        timeout_seconds: Optional[int] = None,
    ) -> ResourceLock:
        """
        Acquire a lock on a resource.
        
        Args:
            resource_id: ID of resource to lock
            lock_type: Type of lock
            agent_id: ID of acquiring agent
            exclusive: Whether lock is exclusive
            timeout_seconds: Lock timeout
            
        Returns:
            ResourceLock instance
            
        Raises:
            RuntimeError: If lock cannot be acquired
        """
        if timeout_seconds is None:
            timeout_seconds = self.lock_timeout_seconds
        
        with self.lock:
            # Check for conflicting locks
            key = resource_id
            
            if key in self.locks:
                existing_locks = [
                    l for l in self.locks[key]
                    if not l.is_expired()
                ]
                self.locks[key] = existing_locks
                
                if existing_locks:
                    if exclusive or any(l.is_exclusive for l in existing_locks):
                        raise RuntimeError(
                            f"Cannot acquire {'exclusive' if exclusive else 'shared'} "
                            f"lock on {resource_id}: already held by "
                            f"{existing_locks[0].owner_agent_id}"
                        )
            
            # Create new lock
            expires_at = (
                datetime.now() + timedelta(seconds=timeout_seconds)
                if timeout_seconds
                else None
            )
            
            resource_lock = ResourceLock(
                resource_id=resource_id,
                lock_type=lock_type,
                owner_agent_id=agent_id,
                expires_at=expires_at,
                is_exclusive=exclusive,
            )
            
            if key not in self.locks:
                self.locks[key] = []
            
            self.locks[key].append(resource_lock)
            
            logger.info(
                f"Lock acquired: {resource_id} by {agent_id} "
                f"(exclusive={exclusive}, timeout={timeout_seconds}s)"
            )
            
            return resource_lock
    
    def release_lock(self, lock: ResourceLock) -> None:
        """
        Release a lock.
        
        Args:
            lock: Lock to release
        """
        with self.lock:
            key = lock.resource_id
            
            if key in self.locks:
                try:
                    self.locks[key].remove(lock)
                    logger.info(
                        f"Lock released: {key} by {lock.owner_agent_id}"
                    )
                except ValueError:
                    logger.warning(f"Lock not found: {lock.lock_id}")
    
    def has_lock(
        self,
        resource_id: str,
        agent_id: str,
    ) -> bool:
        """Check if agent has lock on resource."""
        with self.lock:
            key = resource_id
            
            if key in self.locks:
                for lock in self.locks[key]:
                    if (
                        not lock.is_expired()
                        and lock.owner_agent_id == agent_id
                    ):
                        return True
            
            return False


class StateVersionManager:
    """
    Manages state versions and transactions for consistent distributed state.
    
    Uses Vector Clocks to track causality and detect conflicts.
    """
    
    def __init__(self, agent_ids: List[str]):
        """
        Initialize state version manager.
        
        Args:
            agent_ids: List of agent IDs in system
        """
        self.agent_ids = agent_ids
        self.global_version = VectorClockVersion(agent_ids)
        self.state_versions: Dict[str, VectorClockVersion] = {}
        self.state_history: Dict[str, List[Dict[str, Any]]] = {}
        self.lock = threading.RLock()
        
        logger.info(f"StateVersionManager initialized for {len(agent_ids)} agents")
    
    def get_version(self, state_key: str) -> VectorClockVersion:
        """Get version for state key."""
        with self.lock:
            if state_key not in self.state_versions:
                self.state_versions[state_key] = VectorClockVersion(
                    self.agent_ids
                )
            return self.state_versions[state_key]
    
    def record_write(
        self,
        agent_id: str,
        state_key: str,
        value: Any,
    ) -> Dict[str, Any]:
        """
        Record a state write with version information.
        
        Args:
            agent_id: ID of writing agent
            state_key: Key of state being written
            value: New value
            
        Returns:
            Transaction record with version
        """
        with self.lock:
            # Update version
            version = self.get_version(state_key)
            version.increment(agent_id)
            self.global_version.increment(agent_id)
            
            # Record in history
            if state_key not in self.state_history:
                self.state_history[state_key] = []
            
            record = {
                "timestamp": datetime.now().isoformat(),
                "agent_id": agent_id,
                "value": value,
                "version": version.to_dict(),
                "global_version": self.global_version.to_dict(),
            }
            
            self.state_history[state_key].append(record)
            
            logger.info(
                f"State write recorded: {state_key} by {agent_id} "
                f"(version: {version})"
            )
            
            return record
    
    def detect_conflict(
        self,
        state_key: str,
        version_a: VectorClockVersion,
        version_b: VectorClockVersion,
    ) -> bool:
        """
        Detect if two versions of state have a conflict.
        
        Args:
            state_key: Key of state
            version_a: First version
            version_b: Second version
            
        Returns:
            True if versions are concurrent (conflict)
        """
        return version_a.concurrent_with(version_b)
    
    def get_state_history(
        self,
        state_key: str,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get history of state changes.
        
        Args:
            state_key: Key of state
            limit: Maximum number of records
            
        Returns:
            List of historical records
        """
        with self.lock:
            if state_key not in self.state_history:
                return []
            
            history = self.state_history[state_key]
            
            if limit:
                return history[-limit:]
            
            return history.copy()


class SynchronizationBarrier:
    """
    Synchronization barrier for waiting on multiple agents to reach a point.
    
    Similar to Java's CyclicBarrier or pthread barrier.
    """
    
    def __init__(self, num_agents: int, timeout_seconds: int = 300):
        """
        Initialize barrier.
        
        Args:
            num_agents: Number of agents to synchronize
            timeout_seconds: Timeout for barrier wait
        """
        self.num_agents = num_agents
        self.timeout_seconds = timeout_seconds
        self.parties_waiting = 0
        self.barrier_lock = threading.Condition(threading.RLock())
        self.passed_agents: Set[str] = set()
        self.created_at = datetime.now()
        
        logger.info(
            f"SynchronizationBarrier created for {num_agents} agents "
            f"(timeout={timeout_seconds}s)"
        )
    
    def wait(self, agent_id: str) -> bool:
        """
        Wait at barrier for all agents to arrive.
        
        Args:
            agent_id: ID of waiting agent
            
        Returns:
            True if barrier passed, False on timeout
        """
        with self.barrier_lock:
            self.parties_waiting += 1
            self.passed_agents.add(agent_id)
            
            logger.info(
                f"Agent {agent_id} reached barrier "
                f"({self.parties_waiting}/{self.num_agents})"
            )
            
            # Wait for all parties
            while self.parties_waiting < self.num_agents:
                result = self.barrier_lock.wait(timeout=self.timeout_seconds)
                
                if not result:
                    # Timeout occurred
                    logger.warning(
                        f"Barrier timeout for agent {agent_id} "
                        f"(waited {self.timeout_seconds}s)"
                    )
                    return False
            
            # All parties arrived, notify remaining
            self.barrier_lock.notify_all()
            
            logger.info(
                f"Barrier passed: {self.passed_agents}"
            )
            
            return True


def create_lock_manager() -> LockManager:
    """Factory function for creating lock manager."""
    return LockManager()


def create_state_version_manager(agent_ids: List[str]) -> StateVersionManager:
    """Factory function for creating state version manager."""
    return StateVersionManager(agent_ids)


def create_synchronization_barrier(
    num_agents: int,
    timeout_seconds: int = 300,
) -> SynchronizationBarrier:
    """Factory function for creating synchronization barrier."""
    return SynchronizationBarrier(num_agents, timeout_seconds)

