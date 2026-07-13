"""
Tests for Task 22: Advanced Coder Agent.

Testing intelligent code generation, self-debugging, quality assessment,
and agent collaboration.
"""

import pytest
from core.agents import (
    CodeGenStrategy, IssueSeverity, Issue, CodeQuality, GeneratedCode,
    Diff, CollaborationMessage, AdvancedCoderAgent
)


class TestCodeGenStrategy:
    """Test code generation strategies."""
    
    def test_strategy_values(self):
        """Test strategy enum values."""
        assert CodeGenStrategy.TEMPLATE_BASED.value == "template"
        assert CodeGenStrategy.LLM_BASED.value == "llm"
        assert CodeGenStrategy.HYBRID.value == "hybrid"


class TestIssueSeverity:
    """Test issue severity levels."""
    
    def test_severity_levels(self):
        """Test severity enum values."""
        assert IssueSeverity.INFO.value == 1
        assert IssueSeverity.WARNING.value == 2
        assert IssueSeverity.ERROR.value == 3
        assert IssueSeverity.CRITICAL.value == 4


class TestIssue:
    """Test issue representation."""
    
    def test_create_issue(self):
        """Test creating an issue."""
        issue = Issue(
            issue_type="syntax",
            severity=IssueSeverity.ERROR,
            location="line:10",
            message="Invalid syntax"
        )
        
        assert issue.issue_type == "syntax"
        assert issue.severity == IssueSeverity.ERROR
        assert issue.location == "line:10"


class TestCodeQuality:
    """Test code quality assessment."""
    
    def test_quality_creation(self):
        """Test creating quality assessment."""
        quality = CodeQuality(
            correctness=0.9,
            readability=0.8,
            maintainability=0.75,
            efficiency=0.85,
            test_coverage=0.7
        )
        
        assert quality.correctness == 0.9
    
    def test_overall_score(self):
        """Test overall score calculation."""
        quality = CodeQuality(
            correctness=1.0,
            readability=1.0,
            maintainability=1.0,
            efficiency=1.0,
            test_coverage=1.0
        )
        
        # 1.0 * 0.3 + 1.0 * 0.15 + 1.0 * 0.15 + 1.0 * 0.2 + 1.0 * 0.2 = 1.0
        assert quality.overall_score == 1.0
    
    def test_weighted_score(self):
        """Test weighted overall score."""
        quality = CodeQuality(
            correctness=0.5,  # Weight 0.3
            readability=0.5,
            maintainability=0.5,
            efficiency=0.5,
            test_coverage=0.5
        )
        
        # All 0.5, so overall should be 0.5
        assert quality.overall_score == 0.5


class TestGeneratedCode:
    """Test generated code representation."""
    
    def test_create_generated_code(self):
        """Test creating generated code."""
        code = GeneratedCode(
            source="def test(): pass",
            file_path="test.py",
            strategy_used=CodeGenStrategy.TEMPLATE_BASED,
            confidence=0.9
        )
        
        assert code.source == "def test(): pass"
        assert code.file_path == "test.py"
        assert len(code.issues) == 0
    
    def test_add_issues(self):
        """Test adding issues to generated code."""
        code = GeneratedCode(
            source="def test(): pass",
            file_path="test.py",
            strategy_used=CodeGenStrategy.LLM_BASED,
            confidence=0.85
        )
        
        issue = Issue("syntax", IssueSeverity.WARNING, "line:1", "No docstring")
        code.issues.append(issue)
        
        assert len(code.issues) == 1


class TestDiff:
    """Test diff representation."""
    
    def test_create_diff(self):
        """Test creating diff."""
        diff = Diff(
            unified="+new line\n-old line",
            additions=1,
            deletions=1,
            total_changes=2
        )
        
        assert diff.additions == 1
        assert diff.deletions == 1
        assert diff.total_changes == 2
    
    def test_is_minimal(self):
        """Test minimal diff detection."""
        diff_small = Diff("", 2, 2, 4)
        assert diff_small.is_minimal
        
        diff_large = Diff("", 50, 50, 100)
        assert not diff_large.is_minimal


class TestCollaborationMessage:
    """Test agent collaboration messages."""
    
    def test_create_message(self):
        """Test creating collaboration message."""
        msg = CollaborationMessage(
            message_type="request_review",
            sender="CoderAgent",
            receiver="TesterAgent",
            code="def test(): pass"
        )
        
        assert msg.sender == "CoderAgent"
        assert msg.receiver == "TesterAgent"


class TestAdvancedCoderAgent:
    """Test Advanced Coder Agent."""
    
    def test_agent_creation(self):
        """Test creating advanced coder agent."""
        agent = AdvancedCoderAgent()
        assert agent.name == "AdvancedCoderAgent"
        assert agent.max_debug_iterations == 3
    
    def test_generate_test_code(self):
        """Test generating test code."""
        agent = AdvancedCoderAgent()
        task = {"title": "Create test"}
        
        generated = agent._generate_code(task, {})
        
        assert "pytest" in generated.source or "def test" in generated.source
        assert generated.file_path.startswith("tests/")
    
    def test_generate_class_code(self):
        """Test generating class code."""
        agent = AdvancedCoderAgent()
        task = {"title": "Create model class"}
        
        generated = agent._generate_code(task, {})
        
        assert "class " in generated.source
        assert "def __init__" in generated.source
    
    def test_generate_function_code(self):
        """Test generating function code."""
        agent = AdvancedCoderAgent()
        task = {"title": "Create helper function"}
        
        generated = agent._generate_code(task, {})
        
        assert "def " in generated.source
    
    def test_generate_generic_code(self):
        """Test generating generic code."""
        agent = AdvancedCoderAgent()
        task = {"title": "Implement something"}
        
        generated = agent._generate_code(task, {})
        
        assert len(generated.source) > 0
    
    def test_determine_file_path(self):
        """Test file path determination."""
        agent = AdvancedCoderAgent()
        
        test_task = {"title": "Test my feature"}
        path = agent._determine_file_path(test_task)
        assert path.startswith("tests/")
        
        code_task = {"title": "Implement helper"}
        path = agent._determine_file_path(code_task)
        assert path.startswith("src/")
    
    def test_find_issues(self):
        """Test issue detection."""
        agent = AdvancedCoderAgent()
        
        code = GeneratedCode(
            source="# Just a comment",
            file_path="test.py",
            strategy_used=CodeGenStrategy.HYBRID,
            confidence=0.5
        )
        
        issues = agent._find_issues(code)
        
        # Should find that no functions/classes are defined
        assert len(issues) > 0
    
    def test_find_no_issues(self):
        """Test when no issues are found."""
        agent = AdvancedCoderAgent()
        
        code = GeneratedCode(
            source="def test(): pass",
            file_path="test.py",
            strategy_used=CodeGenStrategy.HYBRID,
            confidence=0.9
        )
        
        issues = agent._find_issues(code)
        
        # Should find that no functions/classes are defined (only 'def' present)
        # Actually this has 'def' so no issue
        has_logic_issue = any(i.issue_type == "logic" for i in issues)
        assert not has_logic_issue
    
    def test_assess_quality(self):
        """Test quality assessment."""
        agent = AdvancedCoderAgent()
        
        code = GeneratedCode(
            source="def test(): pass",
            file_path="test.py",
            strategy_used=CodeGenStrategy.HYBRID,
            confidence=0.9
        )
        
        quality = agent._assess_quality(code)
        
        assert isinstance(quality, CodeQuality)
        assert 0 <= quality.overall_score <= 1.0
    
    def test_run_full_pipeline(self):
        """Test complete generation pipeline."""
        agent = AdvancedCoderAgent()
        state = {
            "current_task": {"title": "Create test function"},
            "code_context": {}
        }
        
        result = agent.run(state)
        
        assert "code_changes" in result
        assert "generated_code" in result["code_changes"]
        assert "quality_score" in result["code_changes"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

