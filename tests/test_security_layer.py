"""Test per Security Layer."""

import pytest
import tempfile
from pathlib import Path
from core.security_layer import (
    PermissionLevel, AgentCapabilities, PermissionManager,
    OperationAudit, SafeFileOperations, SecurityLayer, create_security_layer
)


class TestPermissionManager:
    """Test PermissionManager."""

    def test_default_capabilities(self):
        """Test capability di default."""
        manager = PermissionManager()
        
        assert manager.get_capabilities("planner") is not None
        assert manager.get_capabilities("coder") is not None
        assert manager.get_capabilities("tester") is not None

    def test_planner_read_only(self):
        """Test planner può solo leggere."""
        manager = PermissionManager()
        
        assert manager.can_read("planner", "src/main.py") is True
        assert manager.can_write("planner", "src/main.py") is False
        assert manager.can_execute("planner", "pytest") is False

    def test_coder_read_write(self):
        """Test coder può leggere e scrivere."""
        manager = PermissionManager()
        
        assert manager.can_read("coder", "src/main.py") is True
        assert manager.can_write("coder", "src/main.py") is True
        assert manager.can_execute("coder", "pytest") is False

    def test_tester_execute(self):
        """Test tester può eseguire."""
        manager = PermissionManager()
        
        assert manager.can_read("tester", "tests/") is True
        assert manager.can_write("tester", "src/main.py") is False
        assert manager.can_execute("tester", "pytest") is True

    def test_protected_files_blocked(self):
        """Test file protetti sono bloccati."""
        manager = PermissionManager()
        
        assert manager.can_read("coder", ".env") is False
        assert manager.can_write("coder", ".env") is False
        assert manager.can_read("planner", "secrets/api.key") is False

    def test_blocked_commands(self):
        """Test comandi bloccati."""
        manager = PermissionManager()
        
        assert manager.can_execute("tester", "pytest") is True
        assert manager.can_execute("tester", "rm -rf /") is False
        assert manager.can_execute("tester", "format disk") is False


class TestOperationAudit:
    """Test OperationAudit."""

    def test_log_operation(self):
        """Test logging operazione."""
        audit = OperationAudit()
        audit.log_operation("coder", "write", "src/main.py", True)
        
        assert len(audit.operations) == 1
        assert audit.operations[0]["agent"] == "coder"
        assert audit.operations[0]["allowed"] is True

    def test_get_blocked_operations(self):
        """Test get blocked operations."""
        audit = OperationAudit()
        audit.log_operation("planner", "write", "src/main.py", False)
        audit.log_operation("coder", "write", "src/main.py", True)
        
        blocked = audit.get_blocked_operations()
        assert len(blocked) == 1
        assert blocked[0]["agent"] == "planner"


class TestSafeFileOperations:
    """Test SafeFileOperations."""

    def test_safe_read_allowed(self):
        """Test lettura file consentita."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Crea file
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("content")
            
            manager = PermissionManager()
            audit = OperationAudit()
            safe_ops = SafeFileOperations(manager, audit)
            
            result = safe_ops.read_file("planner", str(test_file))
            
            assert result["status"] == "denied"  # planner non può leggere paths arbitrari

    def test_safe_write_denied(self):
        """Test scrittura file negata."""
        manager = PermissionManager()
        audit = OperationAudit()
        safe_ops = SafeFileOperations(manager, audit)
        
        result = safe_ops.write_file("planner", "src/main.py", "code")
        
        assert result["status"] == "denied"

    def test_execute_command_allowed(self):
        """Test esecuzione comando consentita."""
        manager = PermissionManager()
        audit = OperationAudit()
        safe_ops = SafeFileOperations(manager, audit)
        
        result = safe_ops.execute_command("tester", "pytest")
        
        assert result["status"] == "success"

    def test_execute_command_blocked(self):
        """Test esecuzione comando bloccata."""
        manager = PermissionManager()
        audit = OperationAudit()
        safe_ops = SafeFileOperations(manager, audit)
        
        result = safe_ops.execute_command("tester", "rm -rf /")
        
        assert result["status"] == "denied"


class TestSecurityLayer:
    """Test SecurityLayer."""

    def test_security_layer_creation(self):
        """Test creazione security layer."""
        layer = create_security_layer()
        assert layer is not None

    def test_get_permissions_report(self):
        """Test report permessi."""
        layer = create_security_layer()
        report = layer.get_agent_permissions_report("coder")
        
        assert report["agent"] == "coder"
        assert report["can_write"] is True
        assert report["can_execute"] is False

    def test_get_audit_report(self):
        """Test report audit."""
        layer = create_security_layer()
        layer.permission_manager.can_write("planner", "src/main.py")
        
        report = layer.get_audit_report()
        
        assert "total_operations" in report
        assert "blocked" in report


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

