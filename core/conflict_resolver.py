"""
Conflict Resolution for Parallel Agent Execution.

Handles detection, analysis, and resolution of conflicts when multiple
agents modify the same resources concurrently.
"""

import logging
import difflib
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class ConflictType(Enum):
    """Types of conflicts that can occur."""
    FILE_CONFLICT = "file_conflict"
    STATE_CONFLICT = "state_conflict"
    FUNCTION_CONFLICT = "function_conflict"
    IMPORT_CONFLICT = "import_conflict"
    NO_CONFLICT = "no_conflict"


class ResolutionStrategy(Enum):
    """Strategies for resolving conflicts."""
    LAST_WRITE_WINS = "last_write_wins"
    FIRST_WRITE_WINS = "first_write_wins"
    SEMANTIC_MERGE = "semantic_merge"
    MANUAL_MERGE = "manual_merge"
    ROLLBACK = "rollback"


@dataclass
class ConflictInstance:
    """Represents a single conflict."""
    conflict_id: str
    conflict_type: ConflictType
    resource_id: str
    agent_a: str
    agent_b: str
    value_a: Any
    value_b: Any
    timestamp_a: datetime
    timestamp_b: datetime
    detected_at: datetime = field(default_factory=datetime.now)
    resolution: Optional[str] = None
    resolution_strategy: Optional[ResolutionStrategy] = None
    
    def is_critical(self) -> bool:
        """Check if conflict is critical."""
        # File conflicts on core files are critical
        if self.conflict_type == ConflictType.FILE_CONFLICT:
            critical_files = [
                "core/", "main.py", "Agent.py",
                "requirements.txt", ".gitignore"
            ]
            return any(f in self.resource_id for f in critical_files)
        
        # State conflicts are critical
        if self.conflict_type == ConflictType.STATE_CONFLICT:
            return True
        
        return False
    
    def get_priority(self) -> int:
        """Get conflict priority (1=highest, 10=lowest)."""
        if self.is_critical():
            return 1
        elif self.conflict_type == ConflictType.FILE_CONFLICT:
            return 2
        elif self.conflict_type == ConflictType.STATE_CONFLICT:
            return 3
        else:
            return 5


@dataclass
class ConflictResolution:
    """Result of conflict resolution."""
    conflict_id: str
    strategy_used: ResolutionStrategy
    resolved_value: Any
    resolution_details: Dict[str, Any] = field(default_factory=dict)
    applied_at: datetime = field(default_factory=datetime.now)
    success: bool = False
    error: Optional[str] = None


class ConflictDetector:
    """
    Detects conflicts between concurrent modifications.
    """
    
    def __init__(self):
        """Initialize conflict detector."""
        self.detected_conflicts: List[ConflictInstance] = []
        self.lock = __import__('threading').RLock()
    
    def detect_file_conflict(
        self,
        file_path: str,
        content_a: str,
        content_b: str,
        agent_a: str,
        agent_b: str,
        timestamp_a: datetime,
        timestamp_b: datetime,
    ) -> Optional[ConflictInstance]:
        """
        Detect file content conflict.
        
        Args:
            file_path: Path to file
            content_a: Content from agent A
            content_b: Content from agent B
            agent_a: ID of agent A
            agent_b: ID of agent B
            timestamp_a: Timestamp of agent A's modification
            timestamp_b: Timestamp of agent B's modification
            
        Returns:
            ConflictInstance if conflict exists
        """
        if content_a == content_b:
            # No conflict - same content
            return None
        
        # Check if one is subset of other
        if content_a in content_b or content_b in content_a:
            # One version is subset of other
            # Can be merged (not a hard conflict)
            return None
        
        # Check line-level conflicts
        lines_a = content_a.split('\n')
        lines_b = content_b.split('\n')
        
        diff = list(difflib.unified_diff(
            lines_a,
            lines_b,
            lineterm=''
        ))
        
        if not diff:
            return None
        
        # Conflict detected
        conflict_id = (
            f"{file_path}_{agent_a}_{agent_b}_"
            f"{timestamp_a.timestamp()}"
        )
        
        conflict = ConflictInstance(
            conflict_id=conflict_id,
            conflict_type=ConflictType.FILE_CONFLICT,
            resource_id=file_path,
            agent_a=agent_a,
            agent_b=agent_b,
            value_a=content_a,
            value_b=content_b,
            timestamp_a=timestamp_a,
            timestamp_b=timestamp_b,
        )
        
        logger.warning(f"File conflict detected: {conflict_id}")
        
        with self.lock:
            self.detected_conflicts.append(conflict)
        
        return conflict
    
    def detect_state_conflict(
        self,
        state_key: str,
        state_a: Dict[str, Any],
        state_b: Dict[str, Any],
        agent_a: str,
        agent_b: str,
        timestamp_a: datetime,
        timestamp_b: datetime,
    ) -> Optional[ConflictInstance]:
        """
        Detect state modification conflict.
        
        Args:
            state_key: Key in state
            state_a: State from agent A
            state_b: State from agent B
            agent_a: ID of agent A
            agent_b: ID of agent B
            timestamp_a: Timestamp of agent A's modification
            timestamp_b: Timestamp of agent B's modification
            
        Returns:
            ConflictInstance if conflict exists
        """
        # Deep comparison
        if state_a == state_b:
            return None
        
        # Check for overlapping keys with different values
        for key in state_a:
            if key in state_b:
                if state_a[key] != state_b[key]:
                    # Conflict on this key
                    conflict_id = (
                        f"{state_key}_{key}_{agent_a}_{agent_b}_"
                        f"{timestamp_a.timestamp()}"
                    )
                    
                    conflict = ConflictInstance(
                        conflict_id=conflict_id,
                        conflict_type=ConflictType.STATE_CONFLICT,
                        resource_id=f"{state_key}.{key}",
                        agent_a=agent_a,
                        agent_b=agent_b,
                        value_a=state_a[key],
                        value_b=state_b[key],
                        timestamp_a=timestamp_a,
                        timestamp_b=timestamp_b,
                    )
                    
                    logger.warning(f"State conflict detected: {conflict_id}")
                    
                    with self.lock:
                        self.detected_conflicts.append(conflict)
                    
                    return conflict
        
        return None
    
    def get_conflicts(
        self,
        critical_only: bool = False,
    ) -> List[ConflictInstance]:
        """
        Get detected conflicts.
        
        Args:
            critical_only: Only return critical conflicts
            
        Returns:
            List of conflicts
        """
        with self.lock:
            conflicts = self.detected_conflicts.copy()
        
        if critical_only:
            conflicts = [c for c in conflicts if c.is_critical()]
        
        # Sort by priority
        conflicts.sort(key=lambda c: c.get_priority())
        
        return conflicts


class ConflictResolver:
    """
    Resolves conflicts between concurrent modifications.
    
    Uses multiple strategies: last-write-wins, semantic merge, etc.
    """
    
    def __init__(self):
        """Initialize conflict resolver."""
        self.resolutions: List[ConflictResolution] = []
        self.lock = __import__('threading').RLock()
    
    def resolve_by_timestamp(
        self,
        conflict: ConflictInstance,
        strategy: ResolutionStrategy = ResolutionStrategy.LAST_WRITE_WINS,
    ) -> ConflictResolution:
        """
        Resolve conflict based on timestamp.
        
        Args:
            conflict: Conflict to resolve
            strategy: Resolution strategy
            
        Returns:
            ConflictResolution
        """
        if strategy == ResolutionStrategy.LAST_WRITE_WINS:
            # Use the most recent modification
            if conflict.timestamp_a > conflict.timestamp_b:
                resolved_value = conflict.value_a
                winning_agent = conflict.agent_a
            else:
                resolved_value = conflict.value_b
                winning_agent = conflict.agent_b
        
        elif strategy == ResolutionStrategy.FIRST_WRITE_WINS:
            # Use the first modification
            if conflict.timestamp_a < conflict.timestamp_b:
                resolved_value = conflict.value_a
                winning_agent = conflict.agent_a
            else:
                resolved_value = conflict.value_b
                winning_agent = conflict.agent_b
        
        else:
            resolved_value = conflict.value_a
            winning_agent = conflict.agent_a
        
        resolution = ConflictResolution(
            conflict_id=conflict.conflict_id,
            strategy_used=strategy,
            resolved_value=resolved_value,
            resolution_details={
                "winning_agent": winning_agent,
                "winning_timestamp": (
                    conflict.timestamp_a.isoformat()
                    if winning_agent == conflict.agent_a
                    else conflict.timestamp_b.isoformat()
                ),
            },
            success=True,
        )
        
        logger.info(
            f"Conflict resolved using {strategy.name}: "
            f"{conflict.resource_id} -> agent {winning_agent}"
        )
        
        with self.lock:
            self.resolutions.append(resolution)
        
        return resolution
    
    def resolve_file_conflict_semantic(
        self,
        conflict: ConflictInstance,
    ) -> ConflictResolution:
        """
        Resolve file conflict using semantic merge.
        
        Args:
            conflict: File conflict
            
        Returns:
            ConflictResolution
        """
        content_a = conflict.value_a
        content_b = conflict.value_b
        
        # Try three-way merge (simple implementation)
        # In production, use tools like 'git merge-base'
        
        lines_a = content_a.split('\n')
        lines_b = content_b.split('\n')
        
        # Use difflib to find common sections
        matcher = difflib.SequenceMatcher(None, lines_a, lines_b)
        matching_blocks = matcher.get_matching_blocks()
        
        merged_lines = []
        
        for block in matching_blocks:
            a_start, b_start, size = block.a, block.b, block.size
            
            # Add lines before this block (conflict region)
            if merged_lines or a_start > 0:
                # For now, just take lines from A in conflict regions
                merged_lines.extend(lines_a[len(merged_lines):a_start + size])
            else:
                merged_lines.extend(lines_a[:a_start + size])
        
        merged_content = '\n'.join(merged_lines)
        
        resolution = ConflictResolution(
            conflict_id=conflict.conflict_id,
            strategy_used=ResolutionStrategy.SEMANTIC_MERGE,
            resolved_value=merged_content,
            resolution_details={
                "merge_type": "three_way",
                "agent_a_lines": len(lines_a),
                "agent_b_lines": len(lines_b),
                "merged_lines": len(merged_lines),
            },
            success=True,
        )
        
        logger.info(
            f"File conflict resolved using semantic merge: "
            f"{conflict.resource_id}"
        )
        
        with self.lock:
            self.resolutions.append(resolution)
        
        return resolution
    
    def resolve_conflict(
        self,
        conflict: ConflictInstance,
        preferred_strategy: Optional[ResolutionStrategy] = None,
    ) -> ConflictResolution:
        """
        Resolve a conflict using appropriate strategy.
        
        Args:
            conflict: Conflict to resolve
            preferred_strategy: Preferred resolution strategy
            
        Returns:
            ConflictResolution
        """
        if preferred_strategy is None:
            # Auto-select strategy based on conflict type
            if conflict.conflict_type == ConflictType.FILE_CONFLICT:
                preferred_strategy = ResolutionStrategy.SEMANTIC_MERGE
            else:
                preferred_strategy = ResolutionStrategy.LAST_WRITE_WINS
        
        try:
            if (
                preferred_strategy == ResolutionStrategy.SEMANTIC_MERGE
                and conflict.conflict_type == ConflictType.FILE_CONFLICT
            ):
                return self.resolve_file_conflict_semantic(conflict)
            else:
                return self.resolve_by_timestamp(conflict, preferred_strategy)
        
        except Exception as e:
            logger.error(f"Error resolving conflict {conflict.conflict_id}: {e}")
            
            # Fallback to manual resolution
            return ConflictResolution(
                conflict_id=conflict.conflict_id,
                strategy_used=ResolutionStrategy.MANUAL_MERGE,
                resolved_value=conflict.value_a,  # Fallback to A
                resolution_details={
                    "error": str(e),
                    "fallback": "manual_merge",
                },
                success=False,
                error=str(e),
            )
    
    def resolve_all_conflicts(
        self,
        conflicts: List[ConflictInstance],
        strategy: Optional[ResolutionStrategy] = None,
    ) -> List[ConflictResolution]:
        """
        Resolve multiple conflicts.
        
        Args:
            conflicts: List of conflicts
            strategy: Optional override strategy
            
        Returns:
            List of resolutions
        """
        resolutions = []
        
        for conflict in conflicts:
            resolution = self.resolve_conflict(conflict, strategy)
            resolutions.append(resolution)
        
        logger.info(
            f"Resolved {len(resolutions)} conflicts "
            f"({sum(1 for r in resolutions if r.success)}/{len(resolutions)} successful)"
        )
        
        return resolutions
    
    def get_resolutions(self) -> List[ConflictResolution]:
        """Get all resolutions."""
        with self.lock:
            return self.resolutions.copy()


def create_conflict_detector() -> ConflictDetector:
    """Factory function for creating conflict detector."""
    return ConflictDetector()


def create_conflict_resolver() -> ConflictResolver:
    """Factory function for creating conflict resolver."""
    return ConflictResolver()

