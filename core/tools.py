"""
Tools Implementation for MVP v1.

File operations, terminal execution, and git integration.
"""

import logging
import subprocess
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class FileSystemTools:
    """
    File system operations for the agent.
    
    Provides controlled access to file operations with proper error handling.
    """

    def __init__(self, project_root: str = "."):
        """
        Initialize filesystem tools.
        
        Args:
            project_root: Root directory for operations
        """
        self.project_root = Path(project_root)

    def read_file(self, file_path: str) -> Dict[str, Any]:
        """
        Read a file.
        
        Args:
            file_path: Path to file (relative to project_root)
            
        Returns:
            Dict with status, content, metadata
        """
        try:
            full_path = self.project_root / file_path
            
            if not full_path.exists():
                return {
                    "status": "error",
                    "error": f"File not found: {file_path}",
                    "content": None
                }

            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()

            logger.info(f"Read file: {file_path} ({len(content)} bytes)")

            return {
                "status": "success",
                "file": file_path,
                "content": content,
                "lines": len(content.splitlines()),
                "size_bytes": len(content.encode())
            }

        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return {
                "status": "error",
                "error": str(e),
                "content": None
            }

    def write_file(self, file_path: str, content: str, overwrite: bool = False) -> Dict[str, Any]:
        """
        Write to a file.
        
        Args:
            file_path: Path to file (relative to project_root)
            content: Content to write
            overwrite: Allow overwriting existing file
            
        Returns:
            Dict with status and metadata
        """
        try:
            full_path = self.project_root / file_path
            
            # Create parent directories
            full_path.parent.mkdir(parents=True, exist_ok=True)

            if full_path.exists() and not overwrite:
                return {
                    "status": "error",
                    "error": f"File already exists: {file_path}. Use overwrite=True"
                }

            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)

            logger.info(f"Wrote file: {file_path} ({len(content)} bytes)")

            return {
                "status": "success",
                "file": file_path,
                "size_bytes": len(content.encode()),
                "lines": len(content.splitlines())
            }

        except Exception as e:
            logger.error(f"Error writing file {file_path}: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    def apply_patch(self, file_path: str, patch: str) -> Dict[str, Any]:
        """
        Apply a patch to a file.
        
        For MVP v1, use simple line-based patching.
        Future: Use unified diff format.
        
        Args:
            file_path: Path to file
            patch: Patch content
            
        Returns:
            Dict with status and metadata
        """
        try:
            # Read original file
            read_result = self.read_file(file_path)
            if read_result["status"] != "success":
                return read_result

            original_content = read_result["content"]

            # Simple: append patch to file
            new_content = original_content + "\n" + patch

            # Write back
            return self.write_file(file_path, new_content, overwrite=True)

        except Exception as e:
            logger.error(f"Error applying patch to {file_path}: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    def delete_file(self, file_path: str) -> Dict[str, Any]:
        """
        Delete a file.
        
        Restricted operation - requires explicit approval.
        
        Args:
            file_path: Path to file
            
        Returns:
            Dict with status
        """
        try:
            full_path = self.project_root / file_path

            if not full_path.exists():
                return {
                    "status": "error",
                    "error": f"File not found: {file_path}"
                }

            full_path.unlink()
            logger.info(f"Deleted file: {file_path}")

            return {
                "status": "success",
                "file": file_path,
                "deleted": True
            }

        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e}")
            return {
                "status": "error",
                "error": str(e)
            }


class TerminalTools:
    """
    Terminal/command execution tools.
    
    Runs shell commands with proper error handling and output capture.
    """

    @staticmethod
    def run_command(command: str, cwd: Optional[str] = None, timeout: int = 30) -> Dict[str, Any]:
        """
        Run a shell command.
        
        Args:
            command: Shell command to execute
            cwd: Working directory
            timeout: Timeout in seconds
            
        Returns:
            Dict with status, stdout, stderr
        """
        try:
            logger.info(f"Running command: {command}")

            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            logger.info(f"Command completed with exit code: {result.returncode}")

            return {
                "status": "success" if result.returncode == 0 else "error",
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": command
            }

        except subprocess.TimeoutExpired:
            logger.error(f"Command timeout after {timeout}s: {command}")
            return {
                "status": "error",
                "error": f"Command timeout after {timeout}s",
                "command": command
            }

        except Exception as e:
            logger.error(f"Error running command: {e}")
            return {
                "status": "error",
                "error": str(e),
                "command": command
            }

    @staticmethod
    def run_tests(test_type: str = "pytest", cwd: Optional[str] = None) -> Dict[str, Any]:
        """
        Run tests.
        
        Args:
            test_type: Type of tests (pytest, unittest, etc)
            cwd: Working directory
            
        Returns:
            Test results
        """
        if test_type == "pytest":
            command = "python -m pytest -v"
        elif test_type == "unittest":
            command = "python -m unittest discover"
        else:
            command = test_type

        return TerminalTools.run_command(command, cwd=cwd)


class GitTools:
    """
    Git operations for version control integration.
    """

    def __init__(self, repo_path: str = "."):
        """
        Initialize git tools.
        
        Args:
            repo_path: Path to git repository
        """
        self.repo_path = repo_path

    def status(self) -> Dict[str, Any]:
        """
        Get git status.
        
        Returns:
            Git status information
        """
        result = TerminalTools.run_command("git status --porcelain", cwd=self.repo_path)
        
        if result["status"] != "success":
            return result

        files = []
        for line in result["stdout"].strip().split("\n"):
            if line:
                status_code = line[:2]
                file_path = line[3:]
                files.append({"status": status_code, "file": file_path})

        return {
            "status": "success",
            "files": files,
            "total_changes": len(files)
        }

    def diff(self, file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Get git diff.
        
        Args:
            file_path: Specific file (None for all changes)
            
        Returns:
            Diff content
        """
        command = "git diff"
        if file_path:
            command += f" {file_path}"

        result = TerminalTools.run_command(command, cwd=self.repo_path)
        
        return {
            "status": result["status"],
            "diff": result["stdout"],
            "error": result.get("stderr")
        }

    def branch(self, branch_name: str) -> Dict[str, Any]:
        """
        Create a new branch.
        
        Args:
            branch_name: Name of branch to create
            
        Returns:
            Status
        """
        command = f"git checkout -b {branch_name}"
        result = TerminalTools.run_command(command, cwd=self.repo_path)

        return {
            "status": result["status"],
            "branch": branch_name,
            "message": result.get("stdout", result.get("stderr"))
        }

    def commit(self, message: str, files: list = None) -> Dict[str, Any]:
        """
        Create a git commit.
        
        Args:
            message: Commit message
            files: Files to commit (None for all staged)
            
        Returns:
            Commit status
        """
        try:
            # Add files
            if files:
                for file_path in files:
                    TerminalTools.run_command(f"git add {file_path}", cwd=self.repo_path)
            else:
                TerminalTools.run_command("git add -A", cwd=self.repo_path)

            # Commit
            command = f'git commit -m "{message}"'
            result = TerminalTools.run_command(command, cwd=self.repo_path)

            return {
                "status": result["status"],
                "message": message,
                "output": result["stdout"]
            }

        except Exception as e:
            logger.error(f"Error committing: {e}")
            return {
                "status": "error",
                "error": str(e)
            }


class ToolsFactory:
    """
    Factory for creating tool instances.
    """

    @staticmethod
    def create_filesystem(project_root: str = ".") -> FileSystemTools:
        """Create filesystem tools."""
        return FileSystemTools(project_root)

    @staticmethod
    def create_terminal() -> TerminalTools:
        """Create terminal tools."""
        return TerminalTools()

    @staticmethod
    def create_git(repo_path: str = ".") -> GitTools:
        """Create git tools."""
        return GitTools(repo_path)

    @staticmethod
    def create_all_tools(project_root: str = ".") -> Dict[str, Any]:
        """Create all tool instances."""
        return {
            "filesystem": ToolsFactory.create_filesystem(project_root),
            "terminal": ToolsFactory.create_terminal(),
            "git": ToolsFactory.create_git(project_root),
        }

