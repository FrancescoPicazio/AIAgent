"""
Security Layer - Permissions, Sandboxing, and Safe Execution.

Provides controlled access to files, commands, and operations.
"""

import logging
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class PermissionLevel(Enum):
    """Permission levels for agents."""
    NONE = "none"
    READ = "read"
    READ_WRITE = "read_write"
    EXECUTE = "execute"
    FULL = "full"


@dataclass
class AgentCapabilities:
    """Capabilities granted to an agent."""
    agent_name: str
    can_read: bool = True
    can_write: bool = False
    can_execute: bool = False
    can_delete: bool = False
    can_commit: bool = False
    readable_dirs: List[str] = field(default_factory=list)
    writable_dirs: List[str] = field(default_factory=list)
    protected_files: List[str] = field(default_factory=list)
    allowed_commands: List[str] = field(default_factory=list)
    blocked_commands: List[str] = field(default_factory=list)


class PermissionManager:
    """
    Centralized permission management system.
    
    Controls what each agent can do.
    """

    def __init__(self):
        """Initialize permission manager."""
        self.capabilities: Dict[str, AgentCapabilities] = {}
        self._setup_default_capabilities()
        logger.info("Permission manager initialized")

    def _setup_default_capabilities(self):
        """Setup default agent capabilities."""
        # Planner - read-only
        self.register_agent(AgentCapabilities(
            agent_name="planner",
            can_read=True,
            can_write=False,
            can_execute=False,
            readable_dirs=["src/", "tests/", ".ai/"],
            protected_files=[".env", ".git/", "secrets/"],
            allowed_commands=[]
        ))

        # Coder - read/write
        self.register_agent(AgentCapabilities(
            agent_name="coder",
            can_read=True,
            can_write=True,
            can_execute=False,
            readable_dirs=["src/", "tests/", ".ai/"],
            writable_dirs=["src/", "tests/"],
            protected_files=[".env", ".git/", "secrets/"],
            allowed_commands=[]
        ))

        # Tester - execute only
        self.register_agent(AgentCapabilities(
            agent_name="tester",
            can_read=True,
            can_write=False,
            can_execute=True,
            readable_dirs=["src/", "tests/", ".ai/"],
            protected_files=[".env", ".git/", "secrets/"],
            allowed_commands=["python", "pytest", "npm", "git"],
            blocked_commands=["rm", "del", "format", "shutdown"]
        ))

    def register_agent(self, capabilities: AgentCapabilities):
        """Register an agent with capabilities."""
        self.capabilities[capabilities.agent_name] = capabilities
        logger.info(f"Registered agent: {capabilities.agent_name}")

    def get_capabilities(self, agent_name: str) -> Optional[AgentCapabilities]:
        """Get capabilities for an agent."""
        return self.capabilities.get(agent_name)

    def can_read(self, agent_name: str, file_path: str) -> bool:
        """Check if agent can read a file."""
        caps = self.get_capabilities(agent_name)
        if not caps or not caps.can_read:
            return False

        # Check protected files
        for protected in caps.protected_files:
            if protected in file_path:
                return False

        # Check readable directories
        if caps.readable_dirs:
            for readable in caps.readable_dirs:
                if file_path.startswith(readable):
                    return True
            return False

        return True

    def can_write(self, agent_name: str, file_path: str) -> bool:
        """Check if agent can write a file."""
        caps = self.get_capabilities(agent_name)
        if not caps or not caps.can_write:
            return False

        # Check protected files
        for protected in caps.protected_files:
            if protected in file_path:
                return False

        # Check writable directories
        if caps.writable_dirs:
            for writable in caps.writable_dirs:
                if file_path.startswith(writable):
                    return True
            return False

        return True

    def can_execute(self, agent_name: str, command: str) -> bool:
        """Check if agent can execute a command."""
        caps = self.get_capabilities(agent_name)
        if not caps or not caps.can_execute:
            return False

        # Check blocked commands
        for blocked in caps.blocked_commands:
            if blocked in command.lower():
                return False

        # Check allowed commands
        if caps.allowed_commands:
            for allowed in caps.allowed_commands:
                if command.lower().startswith(allowed):
                    return True
            return False

        return True

    def can_delete(self, agent_name: str, file_path: str) -> bool:
        """Check if agent can delete a file."""
        caps = self.get_capabilities(agent_name)
        return caps is not None and caps.can_delete

    def can_commit(self, agent_name: str) -> bool:
        """Check if agent can commit to git."""
        caps = self.get_capabilities(agent_name)
        return caps is not None and caps.can_commit


class OperationAudit:
    """
    Audit trail for all operations.
    """

    def __init__(self):
        """Initialize audit system."""
        self.operations: List[Dict[str, Any]] = []
        logger.info("Audit system initialized")

    def log_operation(self, agent_name: str, operation_type: str, 
                     target: str, allowed: bool, reason: str = ""):
        """
        Log an operation.
        
        Args:
            agent_name: Name of agent
            operation_type: Type (read, write, execute, delete, commit)
            target: Target file or command
            allowed: Whether operation was allowed
            reason: Reason if blocked
        """
        from datetime import datetime
        
        record = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "operation": operation_type,
            "target": target,
            "allowed": allowed,
            "reason": reason
        }
        
        self.operations.append(record)
        
        status = "✓" if allowed else "✗"
        logger.info(f"[AUDIT] {status} {agent_name} {operation_type} {target}")

    def get_operations_for_agent(self, agent_name: str) -> List[Dict[str, Any]]:
        """Get all operations for an agent."""
        return [op for op in self.operations if op["agent"] == agent_name]

    def get_blocked_operations(self) -> List[Dict[str, Any]]:
        """Get all blocked operations."""
        return [op for op in self.operations if not op["allowed"]]


class SafeFileOperations:
    """
    Safe file operations with permission checking.
    """

    def __init__(self, permission_manager: PermissionManager, audit: OperationAudit):
        """
        Initialize safe file operations.
        
        Args:
            permission_manager: Permission manager instance
            audit: Audit system instance
        """
        self.permission_manager = permission_manager
        self.audit = audit

    def read_file(self, agent_name: str, file_path: str) -> Dict[str, Any]:
        """
        Safely read a file with permission checking.
        
        Args:
            agent_name: Agent requesting access
            file_path: File to read
            
        Returns:
            Result dict with status and content (if allowed)
        """
        allowed = self.permission_manager.can_read(agent_name, file_path)
        self.audit.log_operation(agent_name, "read", file_path, allowed)

        if not allowed:
            return {
                "status": "denied",
                "error": f"Agent {agent_name} not allowed to read {file_path}"
            }

        try:
            with open(file_path, "r") as f:
                content = f.read()
            return {
                "status": "success",
                "content": content,
                "file": file_path
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def write_file(self, agent_name: str, file_path: str, content: str) -> Dict[str, Any]:
        """
        Safely write to a file with permission checking.
        
        Args:
            agent_name: Agent requesting access
            file_path: File to write
            content: Content to write
            
        Returns:
            Result dict with status
        """
        allowed = self.permission_manager.can_write(agent_name, file_path)
        self.audit.log_operation(agent_name, "write", file_path, allowed)

        if not allowed:
            return {
                "status": "denied",
                "error": f"Agent {agent_name} not allowed to write {file_path}"
            }

        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w") as f:
                f.write(content)
            return {
                "status": "success",
                "file": file_path
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def delete_file(self, agent_name: str, file_path: str) -> Dict[str, Any]:
        """
        Safely delete a file with permission checking.
        
        Args:
            agent_name: Agent requesting access
            file_path: File to delete
            
        Returns:
            Result dict with status
        """
        allowed = self.permission_manager.can_delete(agent_name, file_path)
        self.audit.log_operation(agent_name, "delete", file_path, allowed)

        if not allowed:
            return {
                "status": "denied",
                "error": f"Agent {agent_name} not allowed to delete {file_path}"
            }

        try:
            Path(file_path).unlink()
            return {
                "status": "success",
                "file": file_path
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def execute_command(self, agent_name: str, command: str) -> Dict[str, Any]:
        """
        Safely execute a command with permission checking.
        
        Args:
            agent_name: Agent requesting execution
            command: Command to execute
            
        Returns:
            Result dict with status and output
        """
        allowed = self.permission_manager.can_execute(agent_name, command)
        self.audit.log_operation(agent_name, "execute", command, allowed)

        if not allowed:
            return {
                "status": "denied",
                "error": f"Agent {agent_name} not allowed to execute: {command}"
            }

        # In production, this would use Docker sandbox
        # For MVP, just log and return success
        return {
            "status": "success",
            "command": command,
            "output": f"[MOCK] Executed: {command}"
        }


class SecurityLayer:
    """
    Complete security layer orchestration.
    """

    def __init__(self):
        """Initialize security layer."""
        self.permission_manager = PermissionManager()
        self.audit = OperationAudit()
        self.safe_operations = SafeFileOperations(self.permission_manager, self.audit)
        
        logger.info("Security layer initialized")

    def get_agent_permissions_report(self, agent_name: str) -> Dict[str, Any]:
        """Get permission report for an agent."""
        caps = self.permission_manager.get_capabilities(agent_name)
        if not caps:
            return {"error": f"Agent not found: {agent_name}"}

        return {
            "agent": agent_name,
            "can_read": caps.can_read,
            "can_write": caps.can_write,
            "can_execute": caps.can_execute,
            "can_delete": caps.can_delete,
            "can_commit": caps.can_commit,
            "readable_dirs": caps.readable_dirs,
            "writable_dirs": caps.writable_dirs,
            "protected_files": caps.protected_files,
            "allowed_commands": caps.allowed_commands,
            "blocked_commands": caps.blocked_commands
        }

    def get_audit_report(self) -> Dict[str, Any]:
        """Get audit report."""
        total_ops = len(self.audit.operations)
        allowed_ops = sum(1 for op in self.audit.operations if op["allowed"])
        blocked_ops = total_ops - allowed_ops

        return {
            "total_operations": total_ops,
            "allowed": allowed_ops,
            "blocked": blocked_ops,
            "block_rate": blocked_ops / total_ops if total_ops > 0 else 0,
            "recent_blocks": self.audit.get_blocked_operations()[:10]
        }


def create_security_layer() -> SecurityLayer:
    """Factory function."""
    return SecurityLayer()

