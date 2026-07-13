"""Test per Tools Implementation."""

import pytest
import tempfile
from pathlib import Path
from core.tools import (
    FileSystemTools, TerminalTools, GitTools,
    ToolsFactory
)


class TestFileSystemTools:
    """Test FileSystemTools."""

    def test_read_file(self):
        """Test lettura file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Crea file test
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("Hello World")
            
            # Test read
            tools = FileSystemTools(tmpdir)
            result = tools.read_file("test.txt")
            
            assert result["status"] == "success"
            assert result["content"] == "Hello World"

    def test_read_nonexistent_file(self):
        """Test lettura file inesistente."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tools = FileSystemTools(tmpdir)
            result = tools.read_file("nonexistent.txt")
            
            assert result["status"] == "error"

    def test_write_file(self):
        """Test scrittura file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tools = FileSystemTools(tmpdir)
            result = tools.write_file("new_file.txt", "Test content")
            
            assert result["status"] == "success"
            assert (Path(tmpdir) / "new_file.txt").exists()

    def test_write_file_creates_directories(self):
        """Test che write crea directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tools = FileSystemTools(tmpdir)
            result = tools.write_file("subdir/nested/file.txt", "content")
            
            assert result["status"] == "success"
            assert (Path(tmpdir) / "subdir" / "nested" / "file.txt").exists()

    def test_write_file_no_overwrite(self):
        """Test no overwrite per default."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Crea file esistente
            test_file = Path(tmpdir) / "existing.txt"
            test_file.write_text("original")
            
            tools = FileSystemTools(tmpdir)
            result = tools.write_file("existing.txt", "new content")
            
            assert result["status"] == "error"

    def test_delete_file(self):
        """Test cancellazione file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Crea file
            test_file = Path(tmpdir) / "to_delete.txt"
            test_file.write_text("content")
            
            tools = FileSystemTools(tmpdir)
            result = tools.delete_file("to_delete.txt")
            
            assert result["status"] == "success"
            assert not test_file.exists()


class TestTerminalTools:
    """Test TerminalTools."""

    def test_run_command_success(self):
        """Test esecuzione comando."""
        result = TerminalTools.run_command("echo hello")
        
        assert result["status"] == "success"
        assert "hello" in result["stdout"]

    def test_run_command_failure(self):
        """Test comando fallito."""
        result = TerminalTools.run_command("ls /nonexistent_path_xyz")
        
        assert result["status"] == "error"
        assert result["exit_code"] != 0

    def test_run_tests_pytest(self):
        """Test run pytest."""
        result = TerminalTools.run_tests(test_type="pytest")
        
        assert result["status"] in ["success", "error"]


class TestGitTools:
    """Test GitTools."""

    def test_git_tools_creation(self):
        """Test creazione git tools."""
        tools = GitTools("..")
        assert tools is not None
        assert tools.repo_path == "."

    def test_git_status(self):
        """Test git status."""
        tools = GitTools("..")
        result = tools.status()
        
        # Deve tornare status o errore (se non git repo)
        assert "status" in result


class TestToolsFactory:
    """Test ToolsFactory."""

    def test_create_filesystem(self):
        """Test create filesystem."""
        tools = ToolsFactory.create_filesystem(".")
        assert isinstance(tools, FileSystemTools)

    def test_create_terminal(self):
        """Test create terminal."""
        tools = ToolsFactory.create_terminal()
        assert isinstance(tools, TerminalTools)

    def test_create_git(self):
        """Test create git."""
        tools = ToolsFactory.create_git("..")
        assert isinstance(tools, GitTools)

    def test_create_all_tools(self):
        """Test create all tools."""
        tools = ToolsFactory.create_all_tools(".")
        
        assert "filesystem" in tools
        assert "terminal" in tools
        assert "git" in tools
        assert len(tools) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

